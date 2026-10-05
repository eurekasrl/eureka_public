import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography, Box, Button, Table, TableBody, TableCell, TableContainer, 
  TableHead, TableRow, Paper, CircularProgress, Alert, Chip, Divider, 
  IconButton, Tooltip, Stack
} from '@mui/material';
import ListAltIcon from '@mui/icons-material/ListAlt';
import TocIcon from '@mui/icons-material/Toc';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RefreshIcon from '@mui/icons-material/Refresh';
import SpaIcon from '@mui/icons-material/Spa'; // For Bio
import HouseIcon from '@mui/icons-material/House'; // For Serra
import LoopIcon from '@mui/icons-material/Loop'; // For Secondo Raccolto

import { 
  getRagioneSocialeById,
  getPianoUtilizzoComparison
} from '../../api';

const PianoUtilizzoDashboardPage = () => {
  const { ragioneSocialeId } = useParams();
  const navigate = useNavigate();
  
  // --- State ---
  const [ragioneSociale, setRagioneSociale] = useState(null);
  const [comparisonData, setComparisonData] = useState([]);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // --- Fetch Logic ---
  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch Context (Ragione Sociale Header Info)
      const rsData = await getRagioneSocialeById(ragioneSocialeId);
      setRagioneSociale(rsData);

      // 2. Fetch Aggregated Data (Stored Procedure Result)
      // Expecting array: [{ condifesa_nome: '...', sup_riepilogo: 10, ... }, ...]
      const dataList = await getPianoUtilizzoComparison(ragioneSocialeId);
      
      if (Array.isArray(dataList)) {
        setComparisonData(dataList);
      } else {
        console.error("Unexpected API response:", dataList);
        setComparisonData([]);
        setError("Formato dati non valido ricevuto dal server.");
      }

    } catch (err) {
      console.error("Error fetching dashboard data:", err);
      setError("Errore nel caricamento della dashboard.");
    } finally {
      setLoading(false);
    }
  };

  // Initial Load
  useEffect(() => {
    if (ragioneSocialeId) {
      fetchDashboardData();
    }
  }, [ragioneSocialeId]);

  // --- Render Helpers ---
  
  const formatNumber = (num) => {
    return Number(num || 0).toLocaleString('it-IT');
  };

  const getStatusChip = (diff) => {
    const isMatch = Math.abs(diff) < 0.0001; // Tolerance for float math
    return isMatch 
      ? <Chip icon={<CheckCircleIcon />} label="OK" color="success" size="small" variant="outlined" />
      : <Chip icon={<WarningIcon />} label="Mismatch" color="error" size="small" />;
  };

  const renderFlags = (row) => (
    <Stack direction="row" spacing={1}>
      {row.bio && (
        <Tooltip title="Biologico">
          <SpaIcon color="success" fontSize="small" />
        </Tooltip>
      )}
      {row.serra && (
        <Tooltip title="Coltura Protetta / Serra">
          <HouseIcon color="primary" fontSize="small" />
        </Tooltip>
      )}
      {row.secondo_raccolto && (
        <Tooltip title="Secondo Raccolto">
          <LoopIcon color="warning" fontSize="small" />
        </Tooltip>
      )}
    </Stack>
  );

  if (loading) return (
    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
      <CircularProgress />
    </Box>
  );

  if (error) return <Alert severity="error" sx={{ mt: 4 }}>{error}</Alert>;

  return (
    <Box sx={{ mt: 4, mb: 10 }}>
      {/* --- Header --- */}
      <Typography variant="h4" gutterBottom align="center">
        Dashboard Piano Utilizzo
      </Typography>
      <Typography variant="h6" align="center" color="text.secondary">
        {ragioneSociale?.nome || '...'}
      </Typography>
      
      {/* --- Action Buttons --- */}
      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 4, my: 4 }}>
        <Button 
          variant="contained" 
          size="large"
          startIcon={<ListAltIcon />}
          onClick={() => navigate(`/piani-utilizzo/ragioni-sociali/${ragioneSocialeId}/riepilogativi`)}
        >
          Gestisci Riepilogativi
        </Button>
        <Button 
          variant="contained" 
          color="secondary"
          size="large"
          startIcon={<TocIcon />}
          onClick={() => navigate(`/piani-utilizzo/ragioni-sociali/${ragioneSocialeId}/dettagliati`)}
        >
          Gestisci Dettagliati
        </Button>
        <Button 
          variant="contained" 
          color="default"
          size="large"
          startIcon={<TocIcon />}
          onClick={() => navigate(`/piani-utilizzo/ragioni-sociali/${ragioneSocialeId}/partite`)}
        >
          Gestisci Partite
        </Button>
      </Box>

      <Divider sx={{ my: 4 }} />

      {/* --- Comparison Table Header --- */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          Confronto Superfici (Ha)
        </Typography>
        <Tooltip title="Aggiorna Dati">
          <IconButton onClick={fetchDashboardData} color="primary">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>
      
      {/* --- Main Table --- */}
      <TableContainer component={Paper} elevation={3}>
        <Table sx={{ minWidth: 800 }}>
          <TableHead sx={{ bgcolor: '#f5f5f5' }}>
            <TableRow>
              <TableCell width="8%"><strong>Stato</strong></TableCell>
              <TableCell width="20%"><strong>Condifesa</strong></TableCell>
              <TableCell width="8%"><strong>Anno</strong></TableCell>
              <TableCell width="15%"><strong>Comune</strong></TableCell>
              <TableCell width="20%"><strong>Prodotto</strong></TableCell>
              <TableCell width="10%"><strong>Info</strong></TableCell>
              <TableCell align="right" width="10%"><strong>Riepilogo</strong></TableCell>
              <TableCell align="right" width="10%"><strong>Dettaglio</strong></TableCell>
              <TableCell align="right" width="10%"><strong>Diff.</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {comparisonData.length === 0 ? (
              <TableRow>
                <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                  <Typography color="text.secondary">
                    Nessun dato presente. Inizia caricando dati in Riepilogo o Dettagliati.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              comparisonData.map((row, idx) => {
                const diff = row.diff || 0;
                const isMatch = Math.abs(diff) < 0.0001;

                return (
                  <TableRow key={idx} hover>
                    {/* Status */}
                    <TableCell>{getStatusChip(diff)}</TableCell>
                    
                    {/* Names (from Stored Procedure) */}
                    <TableCell>{row.condifesa_nome || row.condifesa_id}</TableCell>
                    <TableCell>{row.anno}</TableCell>
                    <TableCell>{row.comune_nome || row.codice_comune || '-'}</TableCell>
                    <TableCell>
                      <Tooltip title={`ID: ${row.prodotto_id}`}>
                        <span>{row.prodotto_nome} - {row.prodotto_dettaglio}</span>
                      </Tooltip>
                    </TableCell>

                    {/* Flags (Bio, Serra, etc) */}
                    <TableCell>{renderFlags(row)}</TableCell>

                    {/* Numbers */}
                    <TableCell align="right">{formatNumber(row.sup_riepilogo)}</TableCell>
                    <TableCell align="right">{formatNumber(row.sup_dettaglio)}</TableCell>
                    
                    {/* Difference */}
                    <TableCell 
                      align="right" 
                      sx={{ 
                        fontWeight: 'bold', 
                        color: isMatch ? 'success.main' : 'error.main' 
                      }}
                    >
                      {diff > 0 ? `+${formatNumber(diff)}` : formatNumber(diff)}
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default PianoUtilizzoDashboardPage;