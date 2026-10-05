import React from 'react';
import { 
  Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  IconButton, Button, Tooltip, Box, Typography, Chip, Stack
} from '@mui/material';
import { 
  Email, Download, ForwardToInbox, CheckCircle, HourglassEmpty
} from '@mui/icons-material';
import PreventiviStatusChip from './PreventiviStatusChip';

const PreventiviTable = ({ rows, loading, onEmail, onDownload, onIntermediario }) => {
  // Helper to check if any preventivo in the row is approved
  const hasApprovedPreventivo = (statoObj) => {
    if (!statoObj) return false;
    // Check keys case-insensitive for 'approvato' and ensure count > 0
    return Object.entries(statoObj).some(([key, count]) => 
      key.toLowerCase() === 'approvato dal cliente' && count > 0
    );
  };

  return (
    <TableContainer component={Paper} elevation={2}>
      <Table>
        <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
          <TableRow>
            <TableCell>Ramo</TableCell>
            <TableCell align="center">Anno</TableCell>
            <TableCell>Riepilogo Stati</TableCell>
            <TableCell align="right">Azioni</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {loading ? (
             <TableRow>
                <TableCell colSpan={4} align="center" sx={{ py: 3 }}>
                    <Typography color="text.secondary">Caricamento preventivi...</Typography>
                </TableCell>
             </TableRow>
          ) : rows.length === 0 ? (
             <TableRow>
                <TableCell colSpan={4} align="center" sx={{ py: 3 }}>
                    <Typography color="text.secondary">Nessun preventivo trovato.</Typography>
                </TableCell>
             </TableRow>
          ) : (
            rows.map((row, index) => {
              const isApprovedAvailable = hasApprovedPreventivo(row.stato);

              return (
                <TableRow key={index} hover>
                  <TableCell>
                    <Typography fontWeight="bold" variant="body2">{row.ramo_nome}</Typography>
                    <Typography variant="caption" color="text.secondary">ID: {row.ramo_id}</Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Chip label={row.anno} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                      {Object.entries(row.stato).map(([stato, count]) => (
                        <Tooltip key={stato} title={stato}>
                           <PreventiviStatusChip stato={stato} count={count}/>
                        </Tooltip>
                      ))}
                    </Stack>
                  </TableCell>
                  <TableCell align="right">
                    <Box display="flex" justifyContent="flex-end" gap={1}>
                      {/* Standard Download */}
                      <Tooltip title="Scarica CSV">
                        <IconButton size="small" onClick={() => onDownload(row.ramo_id, row.anno)}>
                          <Download fontSize="small" />
                        </IconButton>
                      </Tooltip>

                      {/* Standard Email */}
                      <Tooltip title="Invia Email Cliente">
                        <IconButton size="small" color="primary" onClick={() => onEmail(row.ramo_id, row.anno)}>
                          <Email fontSize="small" />
                        </IconButton>
                      </Tooltip>

                      {/* Intermediario Button */}
                      {isApprovedAvailable && (
                        <Button 
                          variant="contained" 
                          color="warning" 
                          size="small"
                          startIcon={<ForwardToInbox />}
                          onClick={() => onIntermediario(row.ramo_id, row.anno)}
                          sx={{ ml: 1, textTransform: 'none', fontSize: '0.75rem' }}
                        >
                          Invia Intermediario
                        </Button>
                      )}
                    </Box>
                  </TableCell>
                </TableRow>
              );
            })
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default PreventiviTable;