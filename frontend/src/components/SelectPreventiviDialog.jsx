import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Checkbox,
  Typography,
  Box,
  CircularProgress,
  ListItemAvatar,
  Avatar,
  Chip
} from '@mui/material';
import { 
  Business, 
  Place,      
  Check as CheckIcon,
  PeopleAlt
} from '@mui/icons-material';

import PreventiviStatusChip from './Preventivi/PreventiviStatusChip';

const SelectPreventiviDialog = ({ 
  open, 
  onClose, 
  preventivi = [], 
  loading = false, 
  onConfirm,
  
  // --- Customization Props (Defaults provided) ---
  title = "Seleziona Preventivi",
  subtitle = "Seleziona gli elementi dalla lista.",
  confirmLabel = "Conferma",
  confirmIcon = <CheckIcon fontSize="small" />,
  confirmColor = "primary", // 'primary' | 'secondary' | 'success'
  isGroupContext = false,
  initialSelectedIds = []
}) => {

  const [selectedIds, setSelectedIds] = useState([]);

  // Reset or Load initial selection
  useEffect(() => {
    if (open) {
      if (initialSelectedIds && initialSelectedIds.length > 0) {
        setSelectedIds(initialSelectedIds);
      } else {
        setSelectedIds([]);
      }
    }
  }, [open, initialSelectedIds]);

  const handleToggle = (id) => {
    const currentIndex = selectedIds.indexOf(id);
    const newChecked = [...selectedIds];
    if (currentIndex === -1) newChecked.push(id);
    else newChecked.splice(currentIndex, 1);
    setSelectedIds(newChecked);
  };

  const handleToggleAll = () => {
    if (selectedIds.length === preventivi.length) setSelectedIds([]);
    else setSelectedIds(preventivi.map(p => p.id));
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {title}
        <Typography variant="body2" color="textSecondary">
          {subtitle}
        </Typography>
      </DialogTitle>
      
      <DialogContent dividers>
        {loading ? (
          <Box display="flex" justifyContent="center" p={4}>
            <CircularProgress />
          </Box>
        ) : preventivi.length === 0 ? (
          <Box p={4} textAlign="center">
            <Typography color="textSecondary" gutterBottom>
              Nessun preventivo disponibile per questa operazione.
            </Typography>
            <Typography variant="caption">
               (Verifica che i preventivi abbiano lo stato/lifecycle corretto)
            </Typography>
          </Box>
        ) : (
          <>
            <Box mb={2} display="flex" justifyContent="flex-end">
              <Button size="small" onClick={handleToggleAll}>
                {selectedIds.length === preventivi.length ? "Deseleziona Tutti" : "Seleziona Tutti"}
              </Button>
            </Box>
            
            <List>
              {preventivi.map((prev) => {
                const labelId = `checkbox-list-label-${prev.id}`;
                return (
                  <ListItem key={prev.id} disablePadding divider alignItems="flex-start">
                    <ListItemButton onClick={() => handleToggle(prev.id)} alignItems="flex-start">
                        <ListItemIcon sx={{ mt: 0.5 }}>
                            <Checkbox
                                edge="start"
                                checked={selectedIds.indexOf(prev.id) !== -1}
                                tabIndex={-1}
                                inputProps={{ 'aria-labelledby': labelId }}
                            />
                        </ListItemIcon>

                        {isGroupContext && (
                            <ListItemAvatar sx={{ mt: 0 }}>
                                <Avatar sx={{ bgcolor: 'primary.light', width: 32, height: 32 }}>
                                    <Business fontSize="small" />
                                </Avatar>
                            </ListItemAvatar>
                        )}

                        <ListItemText
                            id={labelId}
                            secondaryTypographyProps={{ component: 'div' }} 
                            primary={
                                <Box display="flex" alignItems="center" gap={1} mb={0.5}>
                                <Typography variant="subtitle1" fontWeight="bold">
                                    {isGroupContext ? prev.azienda_nome : (prev.prodotto_nome || prev.ramo_nome || "Preventivo Generico")}
                                </Typography>
                                <PreventiviStatusChip stato={prev.stato || "N/D"}/>
                                </Box>
                            }
                            secondary={
                                <Box component="div" display="flex" flexDirection="column" gap={0.5}>
                                    <Box display="flex" alignItems="center" gap={3} mt={0.5}>
                                        <Box display="flex" alignItems="center" gap={0.5} color="text.secondary">
                                            <Place sx={{ fontSize: 16 }} color="action" />
                                            <Typography variant="caption">{prev.comune_nome || "Comune N/D"}</Typography>
                                        </Box>
                                        <Box display="flex" alignItems="center" gap={0.5} color="text.secondary">
                                            <Business sx={{ fontSize: 18 }} color="action" />
                                            <Typography variant="caption">{prev.compagnia_nome || "N/A"}</Typography>
                                        </Box>
                                        <Box display="flex" alignItems="center" gap={0.5} color="text.secondary">
                                            <PeopleAlt sx={{ fontSize: 18 }} color="action" />
                                            <Typography variant="caption">{prev.intermediario_nome || "N/A"}</Typography>
                                        </Box>
                                        <Box display="flex" alignItems="center" gap={0.5} color="text.secondary">
                                            <Typography variant="caption" fontWeight="bold">
                                                € {new Intl.NumberFormat('it-IT', { minimumFractionDigits: 2 }).format(prev.premio_lordo || 0)}
                                            </Typography>
                                        </Box>
                                    </Box>
                                </Box>
                            }
                        />
                    </ListItemButton>
                  </ListItem>
                );
              })}
            </List>
          </>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} color="inherit">Annulla</Button>
        <Button 
          onClick={() => onConfirm(selectedIds)} 
          variant="contained" 
          color={confirmColor}
          disabled={loading || selectedIds.length === 0}
          endIcon={confirmIcon}
        >
          {confirmLabel} ({selectedIds.length})
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default SelectPreventiviDialog;