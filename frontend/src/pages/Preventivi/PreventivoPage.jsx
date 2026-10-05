import React, { useState, useEffect } from "react";
import {
    Typography,
    Box,
    Button,
    CircularProgress,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Chip,
    IconButton
} from "@mui/material";
import ConfirmDialog from "../../components/ConfirmDialog";
import { useSnackbar } from "../../context/SnackbarProvider";
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckIcon from '@mui/icons-material/Check';
import CancelIcon from '@mui/icons-material/Cancel';
import { ArrowLeft } from "@mui/icons-material";
import AddIcon from '@mui/icons-material/Add'
import RemoveIcon from '@mui/icons-material/Remove';
import { Link, useParams, useNavigate } from "react-router-dom";
import { getPreventiviByRagioneSociale, editEsitoPreventivo, deletePreventivo } from "../../api";
import PreventiviStatusChip from "../../components/Preventivi/PreventiviStatusChip";

const PreventivoPage = () => {  
    const [preventiviData, setPreventiviData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [confirmDialog, setConfirmDialog] = useState({ open: false, title: '', message: '', onConfirm: null });
    const enqueue = useSnackbar();

    const { ragioneSocialeId } = useParams();
    const navigate = useNavigate();

    // Placeholder for handleRowClick since it was referenced in your JSX but not defined in the snippet
    useEffect(() => {
        const fetchAllData = async () => {
            setLoading(true);
            try {
                const response = await getPreventiviByRagioneSociale(ragioneSocialeId, "preventivi");
                setPreventiviData(response || []); 
            } catch (error) {
                console.error("Error fetching data:", error);
            } finally {
                setLoading(false);
            }
        }; 
        
        if (ragioneSocialeId) {
            fetchAllData();
        }
    }, [ragioneSocialeId]);

    const handleEdit = (e, preventivoId, ramoNome) => {
        e.stopPropagation(); // Prevents row click
        navigate(`/preventivi/edit/${preventivoId}`, {state: {ramoNome}});
    };

    const handleEditStatus = async (e, preventivoId, stato, ramoNome) => {
        e.stopPropagation(); // Prevents row click
        try {
            await editEsitoPreventivo(preventivoId, stato);

            setPreventiviData(prevData => {
                return prevData.map(group => {
                    if (group.ramo_nome === ramoNome) {
                        return {
                            ...group,
                            preventivi: group.preventivi.map(p => 
                                p.id === preventivoId ? { ...p, stato: stato } : p
                            )
                        };
                    }
                    return group;
                });
            });
        } catch (err) {
            console.error("Error updating status:", err);
            enqueue("Errore durante l'aggiornamento dello stato", 'error');
        }
    };

    const handleDelete = (e, preventivoId, ramoNome) => {
        e.stopPropagation();
        setConfirmDialog({
            open: true,
            title: 'Elimina preventivo',
            message: 'Sei sicuro di voler eliminare questo preventivo?',
            onConfirm: async () => {
                setConfirmDialog(prev => ({ ...prev, open: false }));
                try {
                    await deletePreventivo(preventivoId, ramoNome);
                    setPreventiviData(prevData =>
                        prevData.map(group => {
                            if (group.ramo_nome === ramoNome) {
                                return { ...group, preventivi: group.preventivi.filter(p => p.id !== preventivoId) };
                            }
                            return group;
                        }).filter(group => group.preventivi.length > 0)
                    );
                } catch (err) {
                    console.error("Error deleting preventivo:", err);
                    enqueue("Errore durante l'eliminazione", 'error');
                }
            },
        });
    };

    const formatCurrency = (value) => {
        if (value === null || value === undefined) return "-";
        return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(value);
    };

    const formatDate = (dateString) => {
        if (!dateString) return "-";
        return new Date(dateString).toLocaleDateString('it-IT');
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                <CircularProgress />
            </Box>
        );
    }

    return (
        <>
        <Box sx={{ my: 4, width: '100%' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, px: 2 }}>
                <Typography variant="h5">Lista Preventivi</Typography>
                <Button 
                                variant="outlined" 
                                size="small"
                                endIcon={<ArrowLeft />} 
                                component={Link} 
                                to={`/admin/ragioni-sociali/${ragioneSocialeId}`}
                            >
                                Vai a Preventivi in Admin
                            </Button>
                <Button 
                    variant="contained" 
                    component={Link} 
                    to={`/preventivi/${ragioneSocialeId}/new`}
                >
                    Nuovo Preventivo
                </Button>
            </Box>

            <Box sx={{ px: 2 }}>
                {preventiviData.length === 0 ? (
                    <Typography variant="body1" sx={{ mt: 2 }}>Nessun preventivo trovato.</Typography>
                ) : (
                    preventiviData.map((ramoGroup) => (
                        <Accordion key={ramoGroup.ramo_id} defaultExpanded>
                            <AccordionSummary
                                expandIcon={<ExpandMoreIcon />}
                                aria-controls={`panel-${ramoGroup.ramo_nome}-content`}
                                id={`panel-${ramoGroup.ramo_nome}-header`}
                                sx={{ backgroundColor: '#f5f5f5' }}
                            >
                                <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>
                                    {ramoGroup.ramo_nome}
                                </Typography>
                            </AccordionSummary>
                            <AccordionDetails sx={{ p: 0 }}>
                                <TableContainer component={Paper} elevation={0}>
                                    <Table sx={{ minWidth: 650 }} aria-label={`${ramoGroup.ramo_nome} table`}>
                                        <TableHead>
                                            <TableRow>
                                                <TableCell><strong>Intermediario</strong></TableCell>
                                                <TableCell><strong>Compagnia</strong></TableCell>
                                                <TableCell><strong>Stato</strong></TableCell>
                                                <TableCell><strong>Comune</strong></TableCell>
                                                <TableCell><strong>Prodotto</strong></TableCell>
                                                <TableCell align="right"><strong>Superficie</strong></TableCell>
                                                <TableCell align="right"><strong>Premio Lordo</strong></TableCell>
                                                <TableCell align="right"><strong>Data Creazione</strong></TableCell>
                                                <TableCell align="right"><strong>Aggiornato</strong></TableCell>
                                                <TableCell><strong>Azioni</strong></TableCell>
                                                <TableCell><strong>Cambia Stato</strong></TableCell>
                                                <TableCell><strong>Esito</strong></TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {ramoGroup.preventivi.map((row) => {
                                                // 1. DETERMINE IF BUTTONS SHOULD BE ACTIVE
                                                const isActionable = ["creato", "inviato al cliente"].includes(row.stato);

                                                return (
                                                    <TableRow
                                                        key={row.id}
                                                        sx={{ 
                                                            '&:last-child td, &:last-child th': { border: 0 } 
                                                        }}
                                                    >
                                                        <TableCell>{row.intermediario_nome}</TableCell>
                                                        <TableCell>{row.compagnia_nome}</TableCell>
                                                        
                                                        <TableCell>
                                                            <PreventiviStatusChip stato={row.stato} />
                                                        </TableCell>

                                                        <TableCell>{row.comune_nome}</TableCell>
                                                        <TableCell>{row.prodotto_nome}</TableCell>
                                                        <TableCell align="right">{row.superficie}</TableCell>
                                                        <TableCell align="right">{formatCurrency(row.premio_lordo)}</TableCell>
                                                        <TableCell align="right">{formatDate(row.created_at)}</TableCell>
                                                        <TableCell align="right">{formatDate(row.updated_at)}</TableCell>
                                                        
                                                        {/* General Actions */}
                                                        <TableCell>
                                                            <IconButton onClick={(e) => handleEdit(e, row.id, ramoGroup.ramo_nome)}>
                                                                <EditIcon />
                                                            </IconButton>
                                                            <IconButton onClick={(e) => handleDelete(e, row.id, ramoGroup.ramo_nome)}>
                                                                <DeleteIcon color="error"/>
                                                            </IconButton>
                                                        </TableCell>
                                                        {/* Cambia Stato */}
                                                        <TableCell>
                                                            <IconButton onClick={(e) => handleEditStatus(e, row.id, "add", ramoGroup.ramo_nome)}>
                                                                <AddIcon />
                                                            </IconButton>
                                                            <IconButton onClick={(e) => handleEditStatus(e, row.id, "detract", ramoGroup.ramo_nome)}>
                                                                <RemoveIcon color="error"/>
                                                            </IconButton>
                                                        </TableCell>
                                                        
                                                        {/* Esito Actions (Approve/Reject) */}
                                                        <TableCell>
                                                            <IconButton 
                                                                onClick={(e) => handleEditStatus(e, row.id, 5, ramoGroup.ramo_nome)} 
                                                                disabled={!isActionable} // Disabled unless status matches
                                                            >
                                                                <CheckIcon color={isActionable ? "success" : "disabled"}/>
                                                            </IconButton>
                                                            
                                                            <IconButton 
                                                                onClick={(e) => handleEditStatus(e, row.id, 1, ramoGroup.ramo_nome)}
                                                                disabled={!isActionable} // Disabled unless status matches
                                                            >
                                                                <CancelIcon color={isActionable ? "warning" : "disabled"}/>
                                                            </IconButton>
                                                        </TableCell>
                                                    </TableRow>
                                                );
                                            })}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            </AccordionDetails>
                        </Accordion>
                    ))
                )}
            </Box>
        </Box>

        <ConfirmDialog
            open={confirmDialog.open}
            title={confirmDialog.title}
            message={confirmDialog.message}
            onConfirm={confirmDialog.onConfirm}
            onCancel={() => setConfirmDialog(prev => ({ ...prev, open: false }))}
            confirmColor="error"
        />
        </>
    );
};

export default PreventivoPage;