import React, { useState, useEffect, useMemo, useCallback, memo } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import {
  Box, Typography, Button, TextField, FormControlLabel, Checkbox,
  Autocomplete, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, CircularProgress, Alert, Grid,
  IconButton, Tooltip, Dialog, DialogTitle, DialogContent, DialogActions,
  MenuItem, Tab, Tabs, Chip
} from '@mui/material';
import {
  PictureAsPdf as PdfIcon,
  AddCircleOutline as AddIcon,
  Save as SaveIcon,
  Delete as DeleteIcon,
  InfoOutlined as InfoIcon,
  CheckCircleOutline as CheckIcon,
  WarningAmber as WarningIcon,
  Download as DownloadIcon,
  FactCheck as VerifyIcon
} from '@mui/icons-material';
import debounce from 'lodash.debounce';
import {
  getAllCondifesa,
  getRagioneSocialeById,
  getProdottiByCondifesa,
  uploadPianoPdf,
  applyPianoMapping,
  createPianoUtilizzoBulk,
  deletePianoUtilizzo,
  getPianiUtilizzoByRagioneSocialeId,
  getPianiUtilizzoDettagliatoByRagioneSocialeId,
  getComuni,
  getAnniDettagliato
} from '../../api';
import ConfirmDialog from '../../components/ConfirmDialog';
import { useSnackbar } from '../../context/SnackbarProvider';


// ---------------------------------------------------------------------------
// Single memoized row — has its OWN local autocomplete options state so
// typing in one row does NOT cause all 200+ other rows to re-render.
// ---------------------------------------------------------------------------
const PianoRow = memo(function PianoRow({
  row, isDettagliato, selectedCondifesaId, onUpdate, onRemove
}) {
  const [prodottiOptions, setProdottiOptions] = useState([]);
  const [prodottiLoading, setProdottiLoading] = useState(false);
  const [comuniOptions, setComuniOptions] = useState([]);
  const [comuniLoading, setComuniLoading] = useState(false);

  const fetchProdotti = useMemo(() => debounce(async (condifesaId, query) => {
    if (!condifesaId) return;
    setProdottiLoading(true);
    try {
      const res = await getProdottiByCondifesa(condifesaId, query);
      setProdottiOptions(Array.isArray(res) ? res : []);
    } finally { setProdottiLoading(false); }
  }, 300), []);

  const fetchComuni = useMemo(() => debounce(async (query) => {
    if (!query || query.length < 2) { setComuniOptions([]); return; }
    setComuniLoading(true);
    try {
      const res = await getComuni(query);
      setComuniOptions(Array.isArray(res) ? res : []);
    } finally { setComuniLoading(false); }
  }, 300), []);

  const comuneValue = comuniOptions.find(c => c.codice_comune === row.codice_comune)
    || (row.comune ? { nome: row.comune, codice_comune: row.codice_comune } : null);

  return (
    <TableRow hover sx={{ opacity: row.selected ? 1 : 0.6, bgcolor: !row.mapped_prodotto ? '#fff3e0' : 'inherit' }}>
      <TableCell padding="checkbox">
        <Checkbox checked={row.selected} onChange={(e) => onUpdate(row.tempId, 'selected', e.target.checked)} />
      </TableCell>

      {/* Comune */}
      <TableCell>
        <Autocomplete
          size="small" options={comuniOptions} loading={comuniLoading} disabled={!row.selected}
          filterOptions={(x) => x}
          getOptionLabel={(o) => o.nome || ''}
          isOptionEqualToValue={(opt, val) => opt.codice_comune === val?.codice_comune}
          value={comuneValue}
          onInputChange={(e, v, r) => r === 'input' && fetchComuni(v)}
          onChange={(e, v) => {
            onUpdate(row.tempId, 'comune', v?.nome || '');
            onUpdate(row.tempId, 'codice_comune', v?.codice_comune || null);
          }}
          renderInput={(p) => (
            <TextField {...p} variant="standard" error={row.selected && !row.codice_comune} />
          )}
        />
      </TableCell>

      {/* Foglio / Particella (dettagliato only) */}
      {isDettagliato && (
        <>
          <TableCell>
            <TextField variant="standard" value={row.foglio} disabled={!row.selected}
              onChange={(e) => onUpdate(row.tempId, 'foglio', e.target.value)} />
          </TableCell>
          <TableCell>
            <TextField variant="standard" value={row.particella} disabled={!row.selected}
              onChange={(e) => onUpdate(row.tempId, 'particella', e.target.value)} />
          </TableCell>
        </>
      )}

      {/* Prodotto */}
      <TableCell>
        <Box sx={{ display: 'flex', flexDirection: 'column' }}>
          {!row.isManual && !row.isSaved && (
            <Typography variant="caption" color="error" sx={{ fontWeight: 'bold', fontSize: '0.7rem' }}>
              {row.prodotto_raw}
            </Typography>
          )}
          <Autocomplete
            size="small" options={prodottiOptions} loading={prodottiLoading} disabled={!row.selected}
            getOptionLabel={(o) => `${o.nome} - ${o.dettaglio || 'Gen'}`}
            isOptionEqualToValue={(opt, val) => opt.id === val?.id}
            value={row.mapped_prodotto}
            onInputChange={(e, v, r) => r === 'input' && fetchProdotti(selectedCondifesaId, v)}
            onChange={(e, v) => onUpdate(row.tempId, 'mapped_prodotto', v)}
            renderInput={(p) => (
              <TextField {...p} variant="standard" error={row.selected && !row.mapped_prodotto} />
            )}
          />
        </Box>
      </TableCell>

      {/* Superficie */}
      <TableCell>
        <TextField type="number" variant="standard" value={row.superficie} disabled={!row.selected}
          onChange={(e) => onUpdate(row.tempId, 'superficie', e.target.value)} />
      </TableCell>

      {/* Data semina (dettagliato only) */}
      {isDettagliato && (
        <TableCell>
          <TextField type="date" variant="standard" fullWidth value={row.data_semina_trapianto}
            disabled={!row.selected} onChange={(e) => onUpdate(row.tempId, 'data_semina_trapianto', e.target.value)}
            InputLabelProps={{ shrink: true }} />
        </TableCell>
      )}

      {/* Serra / Bio / 2° raccolto */}
      <TableCell align="center">
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
          <Checkbox size="small" checked={row.serra} disabled={!row.selected}
            onChange={(e) => onUpdate(row.tempId, 'serra', e.target.checked)} />
          <Checkbox size="small" checked={row.bio} disabled={!row.selected}
            onChange={(e) => onUpdate(row.tempId, 'bio', e.target.checked)} color="success" />
          <Checkbox size="small" checked={row.secondo_raccolto} disabled={!row.selected}
            onChange={(e) => onUpdate(row.tempId, 'secondo_raccolto', e.target.checked)} color="secondary" />
        </Box>
      </TableCell>

      {/* Note */}
      <TableCell>
        <TextField variant="standard" fullWidth value={row.note} disabled={!row.selected}
          onChange={(e) => onUpdate(row.tempId, 'note', e.target.value)} />
      </TableCell>

      {/* Info */}
      <TableCell align="center">
        <Tooltip title={row.raw_line || 'OK'}>
          <InfoIcon fontSize="small" color={row.isSaved ? 'success' : 'primary'} />
        </Tooltip>
      </TableCell>

      {/* Delete */}
      <TableCell align="right">
        <IconButton color="error" size="small" onClick={() => onRemove(row)}>
          <DeleteIcon fontSize="small" />
        </IconButton>
      </TableCell>
    </TableRow>
  );
});


// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------
const PianoUtilizzoPage = () => {
  const { ragioneSocialeId } = useParams();
  const location = useLocation();
  const isDettagliato = location.pathname.includes('dettagliati');
  const modeLabel = isDettagliato ? 'Dettagliato' : 'Riepilogativo';

  // --- Core state ---
  const [ragioneSociale, setRagioneSociale] = useState(null);
  const [condifesaOptions, setCondifesaOptions] = useState([]);
  const [selectedCondifesa, setSelectedCondifesa] = useState(null);
  const [anno, setAnno] = useState(null);
  const [anniOptions, setAnniOptions] = useState([]);
  const [secondoRaccolto, setSecondoRaccolto] = useState(false);
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // --- Pre-sorting modal state ---
  const [mappingModalOpen, setMappingModalOpen] = useState(false);
  const [modalTab, setModalTab] = useState(0);
  const [uploadChoiceOpen, setUploadChoiceOpen] = useState(false);
  const [pendingPdfData, setPendingPdfData] = useState([]);
  const [uniqueMappings, setUniqueMappings] = useState({});
  const [uniqueComuni, setUniqueComuni] = useState({});

  // --- Confirm dialog state ---
  const [confirmDialog, setConfirmDialog] = useState({ open: false, title: '', message: '', onConfirm: null, color: 'primary' });

  // --- Notifications (global snackbar) ---
  const showSnackbar = useSnackbar();

  const openConfirm = useCallback((title, message, onConfirm, color = 'warning') => {
    setConfirmDialog({ open: true, title, message, onConfirm, color });
  }, []);

  const closeConfirm = useCallback(() => {
    setConfirmDialog(prev => ({ ...prev, open: false }));
  }, []);

  // --- Data fetch (filtered by the selected campaign year) ---
  const fetchExistingData = useCallback(async () => {
    if (anno == null) return;
    setLoading(true);
    try {
      const data = isDettagliato
        ? await getPianiUtilizzoDettagliatoByRagioneSocialeId(ragioneSocialeId, anno)
        : await getPianiUtilizzoByRagioneSocialeId(ragioneSocialeId, anno);
      setRows((data || []).map((item) => ({
        tempId: item.id,
        selected: false,
        comune: item.comune?.nome || '',
        codice_comune: item.codice_comune,
        foglio: item.foglio || '',
        particella: item.particella || '',
        data_semina_trapianto: item.data_semina_trapianto || '',
        superficie: item.superficie,
        mapped_prodotto: item.prodotto,
        prodotto_raw: 'Dato Salvato',
        serra: item.serra,
        bio: item.bio,
        secondo_raccolto: item.secondo_raccolto,
        note: item.note || '',
        isManual: false,
        isSaved: true,
      })));
    } catch (err) { console.error('Error fetching existing data:', err); }
    finally { setLoading(false); }
  }, [ragioneSocialeId, isDettagliato, anno]);

  // Load client, condifese, and the campaign years that have data; pick a default.
  useEffect(() => {
    const init = async () => {
      setLoading(true);
      try {
        const [rsData, condifesaRes, anni] = await Promise.all([
          getRagioneSocialeById(ragioneSocialeId),
          getAllCondifesa(),
          getAnniDettagliato(ragioneSocialeId),
        ]);
        setRagioneSociale(rsData);
        setCondifesaOptions(condifesaRes || []);
        const currentYear = new Date().getFullYear();
        const years = Array.from(new Set([...(anni || []), currentYear, currentYear + 1]))
          .sort((a, b) => b - a);
        setAnniOptions(years);
        setAnno(anni && anni.length > 0 ? anni[0] : currentYear);
      } catch { setError('Errore inizializzazione pagina.'); }
      finally { setLoading(false); }
    };
    init();
  }, [ragioneSocialeId, isDettagliato]);

  // Reload saved rows whenever the selected campaign year changes.
  useEffect(() => {
    if (anno != null) fetchExistingData();
  }, [anno, fetchExistingData]);

  // --- Row mutation — stable reference via useCallback ---
  const updateRow = useCallback((tempId, field, value) => {
    setRows(prev => prev.map(r => r.tempId === tempId ? { ...r, [field]: value } : r));
  }, []);

  const removeRow = useCallback((row) => {
    if (row.isSaved) {
      openConfirm(
        'Elimina riga',
        'Questa riga è già nel database. Eliminarla definitivamente?',
        async () => {
          closeConfirm();
          setLoading(true);
          try {
            await deletePianoUtilizzo(row.tempId, isDettagliato);
            await fetchExistingData();
            showSnackbar('Riga eliminata dal database.');
          } catch (err) {
            showSnackbar('Errore eliminazione: ' + err.message, 'error');
          } finally { setLoading(false); }
        },
        'error'
      );
    } else {
      setRows(prev => prev.filter(r => r.tempId !== row.tempId));
    }
  }, [isDettagliato, fetchExistingData, openConfirm, closeConfirm, showSnackbar]);

  // --- PDF upload ---
  const handlePdfUpload = async (e) => {
    const file = e.target.files[0];
    if (!file || !selectedCondifesa) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('condifesa_id', selectedCondifesa.id);
    formData.append('type', isDettagliato ? 'dettagliato' : 'riepilogativo');
    try {
      const response = await uploadPianoPdf(formData);
      setPendingPdfData(response.raw_rows);
      setUniqueMappings(response.uniques);
      setUniqueComuni(response.unique_comuni || {});
      // Ask the user how to proceed: line-by-line verification or CSV download.
      setUploadChoiceOpen(true);
    } catch (err) {
      // Backend returns a specific Italian reason (e.g. scan without OCR) in detail.
      showSnackbar(err.response?.data?.detail || 'Errore parsing PDF. Verifica il formato.', 'error');
    } finally {
      setLoading(false);
      e.target.value = null;
    }
  };

  // --- Post-upload choice: go to verification modal vs. download partite CSV ---
  const handleChoiceVerify = () => {
    setUploadChoiceOpen(false);
    setModalTab(0);
    setMappingModalOpen(true);
  };

  const handleChoiceDownloadCsv = () => {
    setUploadChoiceOpen(false);
    try {
      const csv = buildExtractedRowsCsv(pendingPdfData, isDettagliato);
      // BOM so Excel renders Italian accents correctly.
      const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `piano_utilizzo_${ragioneSocialeId}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      showSnackbar(`CSV scaricato (${pendingPdfData.length} righe).`, 'success');
    } catch (err) {
      showSnackbar('Errore generazione CSV: ' + err.message, 'error');
    } finally {
      // Drop the parsed rows — the user opted out of importing them.
      setPendingPdfData([]);
      setUniqueMappings({});
      setUniqueComuni({});
    }
  };

  // --- Modal: update prodotto mapping ---
  const updateProdottoMapping = useCallback((rawStr, field, value) => {
    setUniqueMappings(prev => ({ ...prev, [rawStr]: { ...prev[rawStr], [field]: value } }));
  }, []);

  // --- Modal: update comune mapping ---
  const updateComuneMapping = useCallback((rawStr, field, value) => {
    setUniqueComuni(prev => ({ ...prev, [rawStr]: { ...prev[rawStr], [field]: value } }));
  }, []);

  // --- Modal: confirm and apply all mappings ---
  const confirmMappingAndImport = async () => {
    setLoading(true);
    try {
      const finalMappedRows = await applyPianoMapping({
        raw_rows: pendingPdfData,
        mapping: uniqueMappings,
        comune_mapping: uniqueComuni,
      });
      setRows(prev => [...finalMappedRows, ...prev]);
      setMappingModalOpen(false);
      setPendingPdfData([]);
    } catch {
      showSnackbar("Errore durante l'applicazione della mappatura.", 'error');
    } finally { setLoading(false); }
  };

  const handleAddManualRow = () => {
    setRows(prev => [{
      tempId: `manual-${Date.now()}`,
      selected: true,
      comune: '', codice_comune: null,
      foglio: '', particella: '',
      mapped_prodotto: null, prodotto_raw: 'Manuale',
      superficie: 0, data_semina_trapianto: '',
      serra: false, bio: false, secondo_raccolto: false,
      note: '', isManual: true,
    }, ...prev]);
  };

  const handleSave = () => {
    const selectedRows = rows.filter(r => r.selected && r.mapped_prodotto && r.superficie > 0);
    if (selectedRows.length === 0) {
      showSnackbar('Nessuna riga valida selezionata.', 'warning');
      return;
    }
    const msg = `Attenzione: il salvataggio sovrascriverà TUTTI i dati ${modeLabel.toLowerCase()} dell'anno ${anno}. Continuare?`;
    openConfirm('Salva Piano di Utilizzo', msg, async () => {
      closeConfirm();
      setLoading(true);
      try {
        const rowData = selectedRows.map(r => ({
          codice_comune: r.codice_comune,
          prodotto_id: r.mapped_prodotto.id,
          superficie: parseInt(r.superficie),
          ...(isDettagliato && {
            foglio: parseInt(r.foglio),
            particella: parseInt(r.particella),
            data_semina_trapianto: r.data_semina_trapianto || null,
          }),
          serra: r.serra, bio: r.bio,
          secondo_raccolto: r.secondo_raccolto,
          note: r.note,
        }));
        await createPianoUtilizzoBulk({
          ragione_sociale_id: ragioneSocialeId,
          condifesa_id: selectedCondifesa.id,
          anno: Number(anno),
          secondo_raccolto: secondoRaccolto,
          rows: rowData,
        }, isDettagliato);
        showSnackbar('Salvataggio completato!');
        await fetchExistingData();
      } catch (err) {
        showSnackbar('Errore: ' + err.message, 'error');
      } finally { setLoading(false); }
    });
  };

  // Number of unmatched comuni (codice_comune is null) to show badge in modal
  const unmatchedComuniCount = Object.values(uniqueComuni).filter(c => !c.codice_comune).length;

  if (loading && rows.length === 0) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  }

  return (
    <Box sx={{ mt: 2, mb: 10, px: 4, width: '100%' }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', color: '#1a237e' }}>
        Piano Utilizzo {modeLabel}: {ragioneSociale?.nome}
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* --- Settings --- */}
      <Paper sx={{ p: 3, mb: 4, width: '100%', boxShadow: 3 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid size={{ xs: 12, md: 4 }}>
            <Autocomplete
              options={condifesaOptions} getOptionLabel={(o) => o.nome || ''}
              value={selectedCondifesa} onChange={(e, v) => setSelectedCondifesa(v)}
              renderInput={(p) => <TextField {...p} label="Condifesa" variant="outlined" />}
            />
          </Grid>
          <Grid size={{ xs: 6, md: 2 }}>
            <TextField select label="Campagna" fullWidth value={anno ?? ''}
              onChange={e => setAnno(Number(e.target.value))}>
              {anniOptions.map((y) => <MenuItem key={y} value={y}>{y}</MenuItem>)}
            </TextField>
          </Grid>
          <Grid size={{ xs: 6, md: 2 }}>
            <FormControlLabel
              control={<Checkbox checked={secondoRaccolto} onChange={e => setSecondoRaccolto(e.target.checked)} />}
              label="2° Racc. Globale"
            />
          </Grid>
          <Grid size={{ xs: 12, md: 4 }} sx={{ display: 'flex', gap: 1 }}>
            <Button variant="contained" color="error" component="label" fullWidth
              startIcon={loading ? <CircularProgress size={20} /> : <PdfIcon />}
              disabled={!selectedCondifesa || loading}>
              Carica PDF
              <input type="file" hidden accept=".pdf" onChange={handlePdfUpload} />
            </Button>
            <Button variant="outlined" fullWidth startIcon={<AddIcon />}
              onClick={handleAddManualRow} disabled={!selectedCondifesa || loading}>
              Manuale
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* --- Post-upload choice dialog --- */}
      <Dialog open={uploadChoiceOpen} onClose={() => setUploadChoiceOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>PDF caricato — come vuoi procedere?</DialogTitle>
        <DialogContent dividers>
          <Typography variant="body2" color="text.secondary">
            Sono state estratte <strong>{pendingPdfData.length}</strong> righe dal PDF.
            Scegli se verificarle riga per riga e importarle nel database, oppure scaricare
            le righe estratte come CSV.
          </Typography>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setUploadChoiceOpen(false)} color="inherit">Annulla</Button>
          <Button
            onClick={handleChoiceDownloadCsv}
            startIcon={<DownloadIcon />}
            variant="outlined"
          >
            Scarica CSV
          </Button>
          <Button
            onClick={handleChoiceVerify}
            startIcon={<VerifyIcon />}
            variant="contained"
            color="primary"
          >
            Verifica riga per riga
          </Button>
        </DialogActions>
      </Dialog>

      {/* --- Pre-sorting modal --- */}
      <Dialog open={mappingModalOpen} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: '#f5f5f5', borderBottom: '1px solid #ddd' }}>
          Validazione Mappatura PDF
        </DialogTitle>
        <DialogContent dividers sx={{ p: 0 }}>
          <Tabs value={modalTab} onChange={(_, v) => setModalTab(v)} sx={{ borderBottom: '1px solid #ddd', px: 2 }}>
            <Tab label={`Prodotti (${Object.keys(uniqueMappings).length})`} />
            <Tab
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  Comuni ({Object.keys(uniqueComuni).length})
                  {unmatchedComuniCount > 0 && (
                    <Chip label={unmatchedComuniCount} color="warning" size="small" icon={<WarningIcon />} />
                  )}
                </Box>
              }
            />
          </Tabs>

          <Box sx={{ p: 2 }}>
            {/* Tab 0: Prodotti */}
            {modalTab === 0 && (
              <>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  Associa i prodotti rilevati nel PDF a quelli nel database. Deseleziona per escluderli.
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 'bold', width: 56 }}>Importa</TableCell>
                        <TableCell sx={{ fontWeight: 'bold' }}>Testo PDF</TableCell>
                        <TableCell sx={{ fontWeight: 'bold', width: '52%' }}>Prodotto Eureka</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.keys(uniqueMappings).map((rawStr) => (
                        <ProdottoMappingRow
                          key={rawStr}
                          rawStr={rawStr}
                          info={uniqueMappings[rawStr]}
                          condifesaId={selectedCondifesa?.id}
                          onUpdate={updateProdottoMapping}
                        />
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </>
            )}

            {/* Tab 1: Comuni */}
            {modalTab === 1 && (
              <>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  Verifica i comuni rilevati. I comuni con sfondo arancione non sono stati abbinati automaticamente.
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 'bold' }}>Testo PDF</TableCell>
                        <TableCell sx={{ fontWeight: 'bold' }}>Stato</TableCell>
                        <TableCell sx={{ fontWeight: 'bold' }}>Comune Eureka</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.keys(uniqueComuni).map((rawStr) => (
                        <ComuneMappingRow
                          key={rawStr}
                          rawStr={rawStr}
                          info={uniqueComuni[rawStr]}
                          onUpdate={updateComuneMapping}
                        />
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </>
            )}
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2, bgcolor: '#f5f5f5' }}>
          <Button onClick={() => setMappingModalOpen(false)} color="inherit">Annulla</Button>
          <Button onClick={confirmMappingAndImport} variant="contained" color="primary"
            startIcon={loading ? <CircularProgress size={18} /> : <CheckIcon />}
            disabled={loading}>
            Conferma e Genera Tabella
          </Button>
        </DialogActions>
      </Dialog>

      {/* --- Table --- */}
      {rows.length > 0 && (
        <Box sx={{ width: '100%' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Anteprima Dati ({rows.filter(r => r.selected).length} / {rows.length})
            </Typography>
            <Button variant="contained" color="success" size="large" startIcon={<SaveIcon />}
              onClick={handleSave} disabled={loading}>
              Salva Selezione
            </Button>
          </Box>

          <TableContainer component={Paper} sx={{ width: '100%', maxHeight: '75vh', overflowX: 'auto' }}>
            <Table stickyHeader sx={{ minWidth: isDettagliato ? 1900 : 1600 }}>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox" sx={{ bgcolor: '#f5f5f5', width: 50 }}>
                    <Checkbox
                      checked={rows.length > 0 && rows.every(r => r.selected)}
                      onChange={(e) => setRows(rows.map(r => ({ ...r, selected: e.target.checked })))}
                    />
                  </TableCell>
                  <TableCell sx={{ bgcolor: '#f5f5f5', fontWeight: 'bold', minWidth: 200 }}>Comune</TableCell>
                  {isDettagliato && (
                    <>
                      <TableCell sx={{ bgcolor: '#f5f5f5', fontWeight: 'bold', width: 100 }}>Foglio</TableCell>
                      <TableCell sx={{ bgcolor: '#f5f5f5', fontWeight: 'bold', width: 100 }}>Particella</TableCell>
                    </>
                  )}
                  <TableCell sx={{ bgcolor: '#f5f5f5', fontWeight: 'bold', width: 400 }}>Prodotto (Eureka)</TableCell>
                  <TableCell sx={{ bgcolor: '#f5f5f5', fontWeight: 'bold', width: 120 }}>Sup (Ha)</TableCell>
                  {isDettagliato && (
                    <TableCell sx={{ bgcolor: '#f5f5f5', fontWeight: 'bold', width: 180 }}>Data Semina</TableCell>
                  )}
                  <TableCell sx={{ bgcolor: '#f5f5f5', fontWeight: 'bold', textAlign: 'center', width: 180 }}>
                    Opzioni (S/B/2)
                  </TableCell>
                  <TableCell sx={{ bgcolor: '#f5f5f5', fontWeight: 'bold', width: 250 }}>Note</TableCell>
                  <TableCell sx={{ bgcolor: '#f5f5f5', fontWeight: 'bold', textAlign: 'center', width: 60 }}>Info</TableCell>
                  <TableCell sx={{ bgcolor: '#f5f5f5', fontWeight: 'bold', width: 60 }} align="right" />
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row) => (
                  <PianoRow
                    key={row.tempId}
                    row={row}
                    isDettagliato={isDettagliato}
                    selectedCondifesaId={selectedCondifesa?.id}
                    onUpdate={updateRow}
                    onRemove={removeRow}
                  />
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {/* --- Confirm dialog --- */}
      <ConfirmDialog
        open={confirmDialog.open}
        title={confirmDialog.title}
        message={confirmDialog.message}
        onConfirm={confirmDialog.onConfirm}
        onCancel={closeConfirm}
        confirmColor={confirmDialog.color}
      />
    </Box>
  );
};


// ---------------------------------------------------------------------------
// CSV helpers — turn the parsed PDF rows into the same shape shown in the table.
// ---------------------------------------------------------------------------

const csvCell = (val) => {
  if (val == null) return '';
  const s = String(val);
  return /[",\n\r;]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
};

const buildExtractedRowsCsv = (rows, isDettagliato) => {
  const header = isDettagliato
    ? ['Comune', 'Foglio', 'Particella', 'Prodotto (Eureka)', 'Prodotto (PDF)', 'Superficie (mq)', 'Serra', 'Bio']
    : ['Comune', 'Prodotto (Eureka)', 'Prodotto (PDF)', 'Superficie (mq)'];

  const lines = [header.map(csvCell).join(',')];
  for (const r of rows) {
    const prodottoMatched = r.mapped_prodotto
      ? `${r.mapped_prodotto.nome}${r.mapped_prodotto.dettaglio ? ' - ' + r.mapped_prodotto.dettaglio : ''}`
      : '';
    const cells = isDettagliato
      ? [r.comune, r.foglio, r.particella, prodottoMatched, r.prodotto_raw, r.superficie, r.serra ? 'S' : 'N', r.bio ? 'S' : 'N']
      : [r.comune, prodottoMatched, r.prodotto_raw, r.superficie];
    lines.push(cells.map(csvCell).join(','));
  }
  return lines.join('\n');
};


// ---------------------------------------------------------------------------
// Modal sub-components (keep outside PianoUtilizzoPage to avoid re-creation)
// ---------------------------------------------------------------------------

const ProdottoMappingRow = memo(function ProdottoMappingRow({ rawStr, info, condifesaId, onUpdate }) {
  const [options, setOptions] = useState([]);
  const [optLoading, setOptLoading] = useState(false);

  const fetchOptions = useMemo(() => debounce(async (condId, q) => {
    if (!condId) return;
    setOptLoading(true);
    try {
      const res = await getProdottiByCondifesa(condId, q);
      setOptions(Array.isArray(res) ? res : []);
    } finally { setOptLoading(false); }
  }, 300), []);

  return (
    <TableRow>
      <TableCell>
        <Checkbox checked={info.selected}
          onChange={(e) => onUpdate(rawStr, 'selected', e.target.checked)} />
      </TableCell>
      <TableCell sx={{ fontSize: '0.8rem', color: '#d32f2f' }}>{rawStr}</TableCell>
      <TableCell sx={{ width: '52%' }}>
        <Autocomplete
          size="small" options={options} loading={optLoading}
          getOptionLabel={(o) => `${o.nome} - ${o.dettaglio || 'Gen'}`}
          value={info.mapped_prodotto}
          onInputChange={(e, v, r) => r === 'input' && fetchOptions(condifesaId, v)}
          onChange={(e, v) => onUpdate(rawStr, 'mapped_prodotto', v)}
          renderInput={(p) => (
            <TextField {...p} variant="standard"
              error={!info.mapped_prodotto && info.selected} />
          )}
        />
      </TableCell>
    </TableRow>
  );
});


const ComuneMappingRow = memo(function ComuneMappingRow({ rawStr, info, onUpdate }) {
  const [options, setOptions] = useState([]);
  const [optLoading, setOptLoading] = useState(false);

  const fetchOptions = useMemo(() => debounce(async (q) => {
    if (!q || q.length < 2) { setOptions([]); return; }
    setOptLoading(true);
    try {
      const res = await getComuni(q);
      setOptions(Array.isArray(res) ? res : []);
    } finally { setOptLoading(false); }
  }, 300), []);

  const currentValue = info.codice_comune
    ? { nome: info.nome_comune || rawStr, codice_comune: info.codice_comune }
    : null;

  return (
    <TableRow sx={{ bgcolor: !info.codice_comune ? '#fff3e0' : 'inherit' }}>
      <TableCell sx={{ fontSize: '0.8rem', color: '#d32f2f' }}>{rawStr}</TableCell>
      <TableCell>
        {info.matched
          ? <Chip label="Abbinato" color="success" size="small" icon={<CheckIcon />} />
          : <Chip label="Non trovato" color="warning" size="small" icon={<WarningIcon />} />
        }
      </TableCell>
      <TableCell>
        <Autocomplete
          size="small" options={options} loading={optLoading}
          filterOptions={(x) => x}
          getOptionLabel={(o) => o.nome || ''}
          isOptionEqualToValue={(opt, val) => opt.codice_comune === val?.codice_comune}
          value={currentValue}
          onInputChange={(e, v, r) => r === 'input' && fetchOptions(v)}
          onChange={(e, v) => {
            onUpdate(rawStr, 'codice_comune', v?.codice_comune || null);
            onUpdate(rawStr, 'nome_comune', v?.nome || rawStr);
            onUpdate(rawStr, 'matched', !!v);
          }}
          renderInput={(p) => (
            <TextField {...p} variant="standard" error={!info.codice_comune} />
          )}
        />
      </TableCell>
    </TableRow>
  );
});

export default PianoUtilizzoPage;
