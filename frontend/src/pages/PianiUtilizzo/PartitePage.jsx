import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box, Typography, Button, Paper, CircularProgress, Alert,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Chip, Divider, Stack, TextField, MenuItem,
  Accordion, AccordionSummary, AccordionDetails,
  InputAdornment,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import SaveIcon from '@mui/icons-material/Save';
import {
  getRagioneSocialeById,
  checkPartiteStatus,
  confirmPartiteMapping,
  getAnniDettagliato,
} from '../../api';
import { getPrezziByYearCondifesaProdottoId } from '../../api/grandine';
import ConfirmDialog from '../../components/ConfirmDialog';
import { useSnackbar } from '../../context/SnackbarProvider';

// ── helpers ───────────────────────────────────────────────────────────────────
const sqmToHa = (mq) => mq / 10_000;
const fmtHa   = (mq) => sqmToHa(mq).toLocaleString('it-IT', { minimumFractionDigits: 4, maximumFractionDigits: 4 });
const fmtQ    = (q)  => q.toLocaleString('it-IT', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const fmtEur  = (v)  => v.toLocaleString('it-IT', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

// prezziCache sentinel values:
//   undefined  — key not in map (never fetched)
//   null       — fetch in progress
//   false      — fetched, no record found
//   object     — fetched, Prezzi record

// ── ResaCalcRow ───────────────────────────────────────────────────────────────
function ResaCalcRow({ groupKey, superficie_totale, resaValues, onResaChange, prezzo }) {
  const resa     = Number(resaValues[groupKey] || 0);
  const ha       = sqmToHa(superficie_totale);
  const quintali = resa > 0 ? ha * resa : null;
  const valore   = quintali !== null && prezzo ? quintali * prezzo.valore : null;

  return (
    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, alignItems: 'center', mt: 2, pt: 2, borderTop: '1px dashed #ddd' }}>
      <TextField
        label="Resa"
        type="number"
        size="small"
        value={resaValues[groupKey] ?? ''}
        onChange={(e) => onResaChange(groupKey, e.target.value)}
        inputProps={{ min: 0, step: 1 }}
        sx={{ width: 155 }}
        InputProps={{ endAdornment: <InputAdornment position="end">q/ha</InputAdornment> }}
      />

      {quintali !== null && (
        <>
          <Typography color="text.disabled" sx={{ userSelect: 'none' }}>→</Typography>

          <Box>
            <Typography variant="caption" color="text.secondary" display="block">Quintali</Typography>
            <Typography fontWeight="bold" color="primary.main">{fmtQ(quintali)} q</Typography>
          </Box>

          {valore !== null ? (
            <>
              <Typography color="text.disabled" sx={{ userSelect: 'none' }}>→</Typography>
              <Box>
                <Typography variant="caption" color="text.secondary" display="block">Valore assicurato</Typography>
                <Typography fontWeight="bold" color="success.main">
                  € {fmtEur(valore)}
                  <Typography component="span" variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                    (@ € {fmtEur(prezzo.valore)}/q)
                  </Typography>
                </Typography>
              </Box>
            </>
          ) : prezzo === null ? (
            <Typography variant="caption" color="text.secondary">Caricamento prezzi…</Typography>
          ) : null}
        </>
      )}

      {prezzo?.resa_max > 0 && (
        <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto', fontStyle: 'italic' }}>
          Resa max assicurabile: {prezzo.resa_max} q/ha
        </Typography>
      )}
    </Box>
  );
}

// ── ACCORDION STYLES ─────────────────────────────────────────────────────────
const accordionSx = {
  mb: 1,
  border: '1px solid #e0e0e0',
  borderRadius: '6px !important',
  '&:before': { display: 'none' },
};

// ── PartitePage ───────────────────────────────────────────────────────────────
const PartitePage = () => {
  const { ragioneSocialeId } = useParams();
  const enqueue = useSnackbar();

  const [ragioneSociale, setRagioneSociale] = useState(null);
  const [statusData,     setStatusData]     = useState(null);
  const [draftRows,      setDraftRows]      = useState([]);
  const [anniOptions,    setAnniOptions]    = useState([]);
  const [selectedAnno,   setSelectedAnno]   = useState(null);
  const [loading,        setLoading]        = useState(true);
  const [saving,         setSaving]         = useState(false);
  const [error,          setError]          = useState(null);
  const [confirmDialog,  setConfirmDialog]  = useState({ open: false, title: '', message: '', onConfirm: null });

  // accordion / resa / prezzi local state
  const [expandedGroups, setExpandedGroups] = useState(new Set());
  const [resaValues,     setResaValues]     = useState({});
  const [prezziCache,    setPrezziCache]    = useState({});

  // ── init ──────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!ragioneSocialeId) return;
    const init = async () => {
      setLoading(true);
      setError(null);
      try {
        const [rsData, anni] = await Promise.all([
          getRagioneSocialeById(ragioneSocialeId),
          getAnniDettagliato(ragioneSocialeId),
        ]);
        setRagioneSociale(rsData);
        const years = anni.length > 0 ? anni : [new Date().getFullYear()];
        setAnniOptions(years);
        setSelectedAnno(years[0]);
      } catch (err) {
        console.error(err);
        setError('Errore durante il caricamento dei dati.');
        setLoading(false);
      }
    };
    init();
  }, [ragioneSocialeId]);

  const fetchStatus = useCallback(async () => {
    if (!ragioneSocialeId || selectedAnno == null) return;
    setLoading(true);
    setError(null);
    try {
      const data = await checkPartiteStatus(ragioneSocialeId, selectedAnno);
      setStatusData(data);
      setDraftRows(data?.payload || []);
      // reset UI state on year change / refresh
      setExpandedGroups(new Set());
      setResaValues({});
      setPrezziCache({});
    } catch (err) {
      console.error(err);
      setError('Errore durante il caricamento dei dati.');
    } finally {
      setLoading(false);
    }
  }, [ragioneSocialeId, selectedAnno]);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  // ── draft editing ─────────────────────────────────────────────────────────
  const handlePartitaChange = (index, newValue) => {
    const updated = [...draftRows];
    updated[index].numero_partita = newValue === '' ? '' : parseInt(newValue, 10);
    setDraftRows(updated);
  };

  // ── confirm save ─────────────────────────────────────────────────────────
  const handleConfirm = () => {
    if (!draftRows.length) return;
    setConfirmDialog({
      open: true,
      title: 'Conferma generazione partite',
      message: 'Confermi la generazione delle partite? Questo sovrascriverà le partite esistenti.',
      onConfirm: async () => {
        setConfirmDialog((prev) => ({ ...prev, open: false }));
        setSaving(true);
        try {
          const payload = draftRows.map((d) => ({
            piano_utilizzo_dettagliato_id: d.pud_id,
            numero: d.numero_partita,
            foglio: d.foglio_assegnato,
            particella: d.particella_assegnata,
            superficie: d.superficie_assegnata,
          }));
          await confirmPartiteMapping(ragioneSocialeId, payload);
          enqueue('Partite salvate correttamente!', 'success');
          await fetchStatus();
        } catch (err) {
          console.error(err);
          enqueue('Errore salvataggio: ' + (err.response?.data?.detail || err.message), 'error');
        } finally {
          setSaving(false);
        }
      },
    });
  };

  // ── prezzi lazy fetch (cached by condifesa_prodotto_anno) ─────────────────
  const fetchPrezziForGroup = useCallback((cacheKey, group) => {
    setPrezziCache((prev) => {
      if (cacheKey in prev) return prev; // already loading or loaded
      // Kick off async fetch; mark as loading in the meantime
      getPrezziByYearCondifesaProdottoId(group.anno, group.condifesa_id, group.prodotto_id)
        .then((results) => {
          setPrezziCache((p) => ({ ...p, [cacheKey]: results?.[0] || false }));
        })
        .catch(() => {
          setPrezziCache((p) => ({ ...p, [cacheKey]: false }));
        });
      return { ...prev, [cacheKey]: null }; // null = loading
    });
  }, []);

  const onAccordionChange = useCallback(
    (group) => (_evt, isExpanded) => {
      setExpandedGroups((prev) => {
        const s = new Set(prev);
        isExpanded ? s.add(group.key) : s.delete(group.key);
        return s;
      });
      if (isExpanded && group.condifesa_id && group.prodotto_id && group.anno) {
        const ck = `${group.condifesa_id}_${group.prodotto_id}_${group.anno}`;
        fetchPrezziForGroup(ck, group);
      }
    },
    [fetchPrezziForGroup],
  );

  const handleResaChange = useCallback((key, val) => {
    setResaValues((prev) => ({ ...prev, [key]: val }));
  }, []);

  // ── group derivations ─────────────────────────────────────────────────────
  // Draft: group by (comune, prodotto) so the accordion key stays stable even
  // when the user edits N° Partita values inside.
  const draftGroups = useMemo(() => {
    if (statusData?.is_balanced || !draftRows.length) return [];
    const map = {};
    draftRows.forEach((row, idx) => {
      const key = `${row.comune}__${row.prodotto}`;
      if (!map[key]) {
        map[key] = {
          key,
          comune: row.comune,
          prodotto: row.prodotto,
          condifesa_id: row.condifesa_id || null,
          prodotto_id: row.prodotto_id || null,
          anno: row.anno || null,
          rows: [],
          superficie_totale: 0,
        };
      }
      map[key].rows.push({ ...row, _idx: idx });
      map[key].superficie_totale += row.superficie_assegnata || 0;
    });
    return Object.values(map);
  }, [statusData?.is_balanced, draftRows]);

  // Confirmed: one accordion per partita (comune + prodotto + numero)
  const confirmedGroups = useMemo(() => {
    if (!statusData?.is_balanced || !statusData?.payload) return [];
    const map = {};
    statusData.payload.forEach((item) => {
      const pud = item.piano_utilizzo_dettagliato;
      if (!pud) return;
      const comune   = pud.comune?.nome || String(pud.codice_comune);
      const prodotto = `${pud.prodotto?.nome} - ${pud.prodotto?.dettaglio || 'Gen'}`;
      const key = `${item.numero}__${pud.codice_comune}__${String(pud.prodotto_id)}`;
      if (!map[key]) {
        map[key] = {
          key,
          comune,
          prodotto,
          numero_partita: item.numero,
          condifesa_id: String(pud.condifesa_id),
          prodotto_id:  String(pud.prodotto_id),
          anno: pud.anno,
          terreni: [],
          superficie_totale: 0,
        };
      }
      map[key].terreni.push({ foglio: item.foglio, particella: item.particella, superficie: item.superficie });
      map[key].superficie_totale += item.superficie;
    });
    return Object.values(map).sort((a, b) => a.numero_partita - b.numero_partita);
  }, [statusData]);

  // ── loading guard ─────────────────────────────────────────────────────────
  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;

  // ── render ────────────────────────────────────────────────────────────────
  return (
    <Box sx={{ mt: 4, mb: 10 }}>
      <Typography variant="h4" gutterBottom>
        Gestione Partite: {ragioneSociale?.nome}
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* ── Status / totals ───────────────────────────────────────────────── */}
      <Paper sx={{ p: 3, mb: 3, border: '1px solid #ddd' }}>
        <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
          <Typography variant="h6">Stato Mappatura:</Typography>
          {statusData?.is_balanced
            ? <Chip icon={<CheckCircleIcon />} label="Mappatura Completa (Dati Salvati)" color="success" />
            : <Chip icon={<WarningIcon />} label="Mappatura Richiesta (Bozza)" color="warning" />}
          <Box sx={{ flexGrow: 1 }} />
          <TextField
            select size="small" label="Campagna"
            value={selectedAnno ?? ''}
            onChange={(e) => setSelectedAnno(Number(e.target.value))}
            sx={{ minWidth: 140 }}
          >
            {anniOptions.map((y) => <MenuItem key={y} value={y}>{y}</MenuItem>)}
          </TextField>
        </Stack>

        <Stack direction="row" spacing={4} divider={<Divider orientation="vertical" flexItem />}>
          <Box>
            <Typography variant="caption" color="text.secondary">Totale PUD</Typography>
            <Typography variant="h5">{(statusData?.total_superficie_pud || 0).toLocaleString('it-IT')} mq</Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">Totale Partite</Typography>
            <Typography variant="h5" color={statusData?.is_balanced ? 'success.main' : 'error.main'}>
              {(statusData?.total_superficie_partite || 0).toLocaleString('it-IT')} mq
            </Typography>
          </Box>
        </Stack>
      </Paper>

      {/* ── DRAFT VIEW ────────────────────────────────────────────────────── */}
      {!statusData?.is_balanced && (
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Configurazione Nuove Partite</Typography>
            <Button
              variant="contained" color="primary"
              startIcon={saving ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
              onClick={handleConfirm}
              disabled={saving}
            >
              Conferma e Salva nel DB
            </Button>
          </Box>

          {draftGroups.map((group) => {
            const ck     = group.condifesa_id && group.prodotto_id && group.anno
              ? `${group.condifesa_id}_${group.prodotto_id}_${group.anno}` : null;
            const prezzo = ck !== null ? prezziCache[ck] : undefined;
            const partiteNums = [...new Set(group.rows.map((r) => r.numero_partita))]
              .filter(Boolean)
              .sort((a, b) => a - b);

            return (
              <Accordion
                key={group.key}
                expanded={expandedGroups.has(group.key)}
                onChange={onAccordionChange(group)}
                disableGutters
                sx={accordionSx}
              >
                <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: '#f5f9ff', borderRadius: '6px' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, width: '100%', pr: 1 }}>
                    <Stack direction="row" spacing={0.5} flexShrink={0}>
                      {partiteNums.map((n) => (
                        <Chip key={n} label={`P.${n}`} size="small" color="primary" variant="outlined" />
                      ))}
                    </Stack>
                    <Typography fontWeight="bold" noWrap>{group.prodotto}</Typography>
                    <Typography color="text.disabled">·</Typography>
                    <Typography color="text.secondary" variant="body2" noWrap>{group.comune}</Typography>
                    <Box sx={{ flexGrow: 1 }} />
                    <Typography variant="body2" fontWeight="medium" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>
                      {fmtHa(group.superficie_totale)} ha
                    </Typography>
                  </Box>
                </AccordionSummary>

                <AccordionDetails sx={{ pt: 1 }}>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 'bold', color: '#1565c0', width: 100 }}>N° Partita</TableCell>
                          <TableCell sx={{ fontWeight: 'bold' }}>Foglio</TableCell>
                          <TableCell sx={{ fontWeight: 'bold' }}>Particella</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 'bold' }}>Sup. (mq)</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {group.rows.map((row) => (
                          <TableRow key={row._idx} sx={row.is_split ? { bgcolor: '#fffde7' } : {}}>
                            <TableCell>
                              <TextField
                                size="small" type="number" variant="standard"
                                value={row.numero_partita}
                                onChange={(e) => handlePartitaChange(row._idx, e.target.value)}
                                sx={{ width: 70, input: { fontWeight: 'bold', color: '#1565c0' } }}
                              />
                            </TableCell>
                            <TableCell>{row.foglio_assegnato}</TableCell>
                            <TableCell>
                              {row.particella_assegnata}
                              {row.is_split && (
                                <Chip label="parz." size="small" color="warning"
                                  sx={{ ml: 1, height: 18, fontSize: '0.65rem' }} />
                              )}
                            </TableCell>
                            <TableCell align="right">{row.superficie_assegnata?.toLocaleString('it-IT')}</TableCell>
                          </TableRow>
                        ))}
                        <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                          <TableCell colSpan={3} sx={{ fontWeight: 'bold', fontSize: '0.8rem' }}>Totale gruppo</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 'bold' }}>
                            {group.superficie_totale.toLocaleString('it-IT')}
                          </TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </TableContainer>

                  <ResaCalcRow
                    groupKey={group.key}
                    superficie_totale={group.superficie_totale}
                    resaValues={resaValues}
                    onResaChange={handleResaChange}
                    prezzo={prezzo}
                  />
                </AccordionDetails>
              </Accordion>
            );
          })}
        </Paper>
      )}

      {/* ── CONFIRMED VIEW ────────────────────────────────────────────────── */}
      {statusData?.is_balanced && (
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">Partite Assicurate</Typography>
            <Button size="small" variant="outlined" color="warning" onClick={fetchStatus}>
              Ricalcola / Modifica
            </Button>
          </Box>

          {confirmedGroups.map((group) => {
            const ck     = `${group.condifesa_id}_${group.prodotto_id}_${group.anno}`;
            const prezzo = prezziCache[ck];

            return (
              <Accordion
                key={group.key}
                expanded={expandedGroups.has(group.key)}
                onChange={onAccordionChange(group)}
                disableGutters
                sx={accordionSx}
              >
                <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: '#f0f7ee', borderRadius: '6px' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, width: '100%', pr: 1 }}>
                    <Chip label={`P.${group.numero_partita}`} size="small" color="success" sx={{ flexShrink: 0 }} />
                    <Typography fontWeight="bold" noWrap>{group.prodotto}</Typography>
                    <Typography color="text.disabled">·</Typography>
                    <Typography color="text.secondary" variant="body2" noWrap>{group.comune}</Typography>
                    <Box sx={{ flexGrow: 1 }} />
                    <Typography variant="body2" fontWeight="medium" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>
                      {fmtHa(group.superficie_totale)} ha
                    </Typography>
                  </Box>
                </AccordionSummary>

                <AccordionDetails sx={{ pt: 1 }}>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 'bold' }}>Foglio</TableCell>
                          <TableCell sx={{ fontWeight: 'bold' }}>Particella</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 'bold' }}>Sup. (mq)</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {group.terreni.map((t, i) => (
                          <TableRow key={i}>
                            <TableCell>{t.foglio}</TableCell>
                            <TableCell>{t.particella}</TableCell>
                            <TableCell align="right">{t.superficie.toLocaleString('it-IT')}</TableCell>
                          </TableRow>
                        ))}
                        <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                          <TableCell colSpan={2} sx={{ fontWeight: 'bold', fontSize: '0.8rem' }}>Totale</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 'bold' }}>
                            {group.superficie_totale.toLocaleString('it-IT')}
                          </TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </TableContainer>

                  <ResaCalcRow
                    groupKey={group.key}
                    superficie_totale={group.superficie_totale}
                    resaValues={resaValues}
                    onResaChange={handleResaChange}
                    prezzo={prezzo}
                  />
                </AccordionDetails>
              </Accordion>
            );
          })}
        </Paper>
      )}

      <ConfirmDialog
        open={confirmDialog.open}
        title={confirmDialog.title}
        message={confirmDialog.message}
        onConfirm={confirmDialog.onConfirm}
        onCancel={() => setConfirmDialog((prev) => ({ ...prev, open: false }))}
        confirmColor="warning"
      />
    </Box>
  );
};

export default PartitePage;
