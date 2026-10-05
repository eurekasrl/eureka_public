import React, { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box, Button, Checkbox, FormControlLabel, Grid, MenuItem, Paper, Select,
  TextField, Typography, FormControl, InputLabel, CircularProgress, Alert,
  Divider, Chip, Tooltip
} from "@mui/material";

import {
  // Piani Utilizzo
  getPianiUtilizzoByPreventivoId,
  getPianiUtilizzoByRagioneSocialeId,
  // Common
  getPrezziByYearCondifesaProdottoId,
  getComune,
  getCondifesaById,
  getProdottoById,
  // Tassi
  getTassiByPianoUtilizzoPreventivo,
  getTassiByPianoUtilizzoAndCompagniaIntermediario,
  // CRUD
  createPreventivoGrandine,
  getPreventivoGrandineBySalePreventivoId,
  patchPreventivoGrandine
} from "../../../../api";
import { useSnackbar } from "../../../../context/SnackbarProvider";

const GrandinePage = ({ preventivoId, initialData, mode = 'create' }) => {
  const navigate = useNavigate();
  const enqueue = useSnackbar();
  const isUpdateMode = mode === 'edit';
  
  // Context Data
  const currentragioneSocialeId = isUpdateMode ? null : initialData?.ragione_sociale_id;
  const currentCompagniaId = isUpdateMode ? null : initialData?.compagnia_id;
  const currentIntermediarioId = isUpdateMode ? null : initialData?.intermediario_id;

  // State
  const [existingPreventivoId, setExistingPreventivoId] = useState(null);
  const [existingData, setExistingData] = useState(null);

  // Loading States
  const [loadingExisting, setLoadingExisting] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Errors
  const [errorDependentOptions, setErrorDependentOptions] = useState(null);
  const [validationWarnings, setValidationWarnings] = useState([]);
  const [error, setError] = useState(null);

  // Data Sources
  const [pianoUtilizzoOptions, setPianoUtilizzoOptions] = useState([]);
  const [areaOptions, setAreaOptions] = useState([]);
  const [fasciaPrezzoOptions, setFasciaPrezzoOptions] = useState([]);
  const [tabellaConversioneOptions, setTabellaConversioneOptions] = useState([]);

  // Raw Data
  const [allPrezzi, setAllPrezzi] = useState([]);
  const [allTassiRaw, setAllTassiRaw] = useState([]);

  // Selections & Details
  const [selectedPianoUtilizzoDetails, setSelectedPianoUtilizzoDetails] = useState(null);
  const [selectedPrezzo, setSelectedPrezzo] = useState(null);
  const [nomeComune, setNomeComune] = useState("Caricamento...");
  const [nomeCondifesa, setNomeCondifesa] = useState("Caricamento...");
  const [nomeProdotto, setNomeProdotto] = useState("Caricamento...");
  const [prodottoDetails, setProdottoDetails] = useState(null);

  // Grouped Tassi Structure for UI
  const [groupedTassi, setGroupedTassi] = useState({});
  const [selectedFranchises, setSelectedFranchises] = useState({});

  // Main Form Data
  const [formData, setFormData] = useState({
    piano_utilizzo_id: "",
    contribuzione: true,
    condifesa: true,
    caa_coldiretti: true,
    resa_cliente: "",
    area: "",
    fascia_prezzo_cliente: "",
    tabella_conversione: "",
    valore_assicurato: 0,
    ag: 0,
    nag: 0,
    lordo: 0,
    premio_lordo: 0,
    premio_netto: 0,
  });

  // 0. LOAD EXISTING DATA (Only in Edit Mode)
  useEffect(() => {
    const checkExisting = async () => {
      if (!isUpdateMode || !preventivoId) return;
      setLoadingExisting(true);
      try {
        const data = await getPreventivoGrandineBySalePreventivoId(preventivoId);
        if (data) {
          setExistingPreventivoId(data.sale_preventivo_id);
          setExistingData(data);
          setFormData(prev => ({
            ...prev,
            piano_utilizzo_id: data.piano_utilizzo_id,
            contribuzione: data.contribuzione,
            condifesa: data.condifesa,
            caa_coldiretti: data.caa_coldiretti,
            resa_cliente: data.resa_cliente,
          }))
        }
      } catch (err) {
        console.error("Errore caricamento preventivo esistente:", err);
        setError("Impossibile caricare il preventivo esistente.");
      } finally {
        setLoadingExisting(false);
      }
    };
    checkExisting();
  }, [isUpdateMode, preventivoId]);

  // 1. FETCH PIANI UTILIZZO
  useEffect(() => {
    const fetchPianoUtilizzoOptions = async () => {
      try {
        let response = [];
        if (isUpdateMode && preventivoId) {
          response = await getPianiUtilizzoByPreventivoId(preventivoId);
        } else if (currentragioneSocialeId) {
          response = await getPianiUtilizzoByRagioneSocialeId(currentragioneSocialeId);
        }

        // Spread ...item to keep all fields (condifesa_id etc) safe
        const formattedOptions = response.map(item => ({
          ...item,
          id: item.id,
          name: `Piano ${item.tipo} - Anno ${item.anno} (ID: ${item.id.substring(0, 8)}...)`,
        }));
        setPianoUtilizzoOptions(formattedOptions);
      } catch (err) {
        enqueue("Errore nel caricamento piani: " + err.message, 'error');
      }
    };
    fetchPianoUtilizzoOptions();
  }, [isUpdateMode, preventivoId, currentragioneSocialeId, enqueue]);

  // 2. Update Selected Piano Details
  useEffect(() => {
    if (formData.piano_utilizzo_id && pianoUtilizzoOptions.length > 0) {
      const details = pianoUtilizzoOptions.find(o => o.id === formData.piano_utilizzo_id);
      setSelectedPianoUtilizzoDetails(details || null);
    } else {
      setSelectedPianoUtilizzoDetails(null);
    }
  }, [formData.piano_utilizzo_id, pianoUtilizzoOptions]);

  // 3. Fetch Names
  useEffect(() => {
    const fetchNames = async () => {
      if (selectedPianoUtilizzoDetails) {
        try {
          // Comune
          let cName = "N/A";
          if (selectedPianoUtilizzoDetails.codice_comune) {
            const cRes = await getComune(selectedPianoUtilizzoDetails.codice_comune);
            if (cRes?.[0]?.nome) cName = cRes[0].nome;
          }
          setNomeComune(cName);
          // Condifesa
          let condName = "N/A";
          if (selectedPianoUtilizzoDetails.condifesa_id) {
            const condRes = await getCondifesaById(selectedPianoUtilizzoDetails.condifesa_id);
            if (condRes?.nome) condName = condRes.nome;
          }
          setNomeCondifesa(condName);
          // Prodotto
          let pName = "N/A";
          if (selectedPianoUtilizzoDetails.prodotto_id) {
            const pRes = await getProdottoById(selectedPianoUtilizzoDetails.prodotto_id);
            setProdottoDetails(pRes);
            if (pRes?.nome) pName = `${pRes.nome}-${pRes.dettaglio}`;
          }
          setNomeProdotto(pName);
        } catch {
          enqueue('Errore caricamento nomi.', 'error');
        }
      }
    };
    fetchNames();
  }, [selectedPianoUtilizzoDetails, enqueue]);

  // 4. Fetch Dependent Options (Prezzi & Tassi) AND Handle Reset Logic
  useEffect(() => {
    setErrorDependentOptions(null);
    
    if (formData.piano_utilizzo_id && selectedPianoUtilizzoDetails) {
      const fetchDependent = async () => {
        try {
          const { anno, condifesa_id, prodotto_id } = selectedPianoUtilizzoDetails;

          // A. Get Prezzi
          const prezziResponse = await getPrezziByYearCondifesaProdottoId(anno, condifesa_id, prodotto_id);
          setAllPrezzi(prezziResponse || []);
          const distinctAreas = [...new Set((prezziResponse || []).map(i => i.area))];
          setAreaOptions(distinctAreas);

          // B. Get Tassi
          let tassiResponse = [];
          if (isUpdateMode) {
             // In Edit, tassi might be custom
             tassiResponse = await getTassiByPianoUtilizzoPreventivo(formData.piano_utilizzo_id, preventivoId);
          } else {
             if (currentCompagniaId && currentIntermediarioId) {
                tassiResponse = await getTassiByPianoUtilizzoAndCompagniaIntermediario(formData.piano_utilizzo_id, currentCompagniaId, currentIntermediarioId);
             } else {
                console.warn("Missing Compagnia/Intermediario ID");
             }
          }
          setAllTassiRaw(tassiResponse || []);
          const distinctTabelle = [...new Set((tassiResponse || []).map(i => i.tabella_conversione))];
          setTabellaConversioneOptions(distinctTabelle);

          // --- RESET LOGIC (FIXED) ---
          // We only reset downstream fields if we are in Create mode, 
          // OR if we are in Edit mode but the user selected a DIFFERENT plan than the original.
          const isOriginalPlan = isUpdateMode && existingData && existingData.piano_utilizzo_id === formData.piano_utilizzo_id;

          if (!isOriginalPlan) {
            setFormData(prev => ({ 
              ...prev, 
              area: "", 
              fascia_prezzo_cliente: "", 
              tabella_conversione: "" 
            }));
            setFasciaPrezzoOptions([]);
            setSelectedPrezzo(null);
            setGroupedTassi({});
            setSelectedFranchises({});
          }

        } catch (err) {
          setErrorDependentOptions("Errore caricamento opzioni: " + err.message);
        }
      };
      fetchDependent();
    }
  }, [
    formData.piano_utilizzo_id, 
    selectedPianoUtilizzoDetails, 
    isUpdateMode, 
    preventivoId, 
    currentCompagniaId, 
    currentIntermediarioId,
    // Note: existingData must be a dependency for the isOriginalPlan check, 
    // but we must ensure existingData doesn't flip to null unexpectedly.
    existingData 
  ]);

  // 4.5 REHYDRATION LOGIC (FIXED)
  // This restores the UI state once Tassi/Prezzi are loaded in Edit Mode
  useEffect(() => {
    if (isUpdateMode && existingData && allPrezzi.length > 0 && allTassiRaw.length > 0) {
      // Check if we already matched the prezzo to avoid infinite loops or overwrites
      if (selectedPrezzo && selectedPrezzo.id === existingData.prezzo_id) return;

      // A. Restore Area/Fascia
      if (existingData.prezzo_id) {
        const matchedPrezzo = allPrezzi.find(p => p.id === existingData.prezzo_id);
        if (matchedPrezzo) {
          setFormData(prev => ({
            ...prev,
            area: matchedPrezzo.area,
            fascia_prezzo_cliente: matchedPrezzo.fascia,
          }));
          setSelectedPrezzo(matchedPrezzo);
        }
      }

      // B. Restore Checkboxes & Franchises
      const activeGuarantees = {};
      const activeFranchises = {};
      let detectedTabella = "";
      
      const savedIds = new Set(Object.values(existingData));

      allTassiRaw.forEach(tasso => {
        if (savedIds.has(tasso.id)) {
          activeGuarantees[tasso.garanzia] = true;
          activeFranchises[tasso.garanzia] = tasso.fr;
          if (!detectedTabella) detectedTabella = tasso.tabella_conversione;
        }
      });

      setFormData(prev => ({
        ...prev,
        ...activeGuarantees,
        tabella_conversione: detectedTabella || prev.tabella_conversione
      }));
      
      setSelectedFranchises(prev => ({ ...prev, ...activeFranchises }));
      
      // IMPORTANT: Do NOT setExistingData(null) here. 
      // Keeping it ensures the "isOriginalPlan" check in Effect 4 remains valid.
    }
  }, [isUpdateMode, existingData, allPrezzi, allTassiRaw, selectedPrezzo]);

  // 5. Filter Fascia Prezzo
  useEffect(() => {
    if (formData.area) {
      let filtered = allPrezzi.filter(i => i.area === formData.area);
      if (selectedPianoUtilizzoDetails?.bio) {
        filtered = filtered.filter(i => i.fascia === 'D');
      } else {
        filtered = filtered.filter(i => i.fascia !== 'D');
      }
      const distinctFascias = [...new Set(filtered.map(i => i.fascia))];
      
      setFormData(prev => ({
        ...prev,
        fascia_prezzo_cliente: distinctFascias.includes(prev.fascia_prezzo_cliente) ? prev.fascia_prezzo_cliente : ""
      }));
      setFasciaPrezzoOptions(distinctFascias);
    } else {
      setFasciaPrezzoOptions([]);
    }
  }, [formData.area, selectedPianoUtilizzoDetails, allPrezzi]);

  // 6. Set Selected Prezzo Object
  useEffect(() => {
    if (formData.area && formData.fascia_prezzo_cliente) {
      const found = allPrezzi.find(i => i.area === formData.area && i.fascia === formData.fascia_prezzo_cliente);
      setSelectedPrezzo(found || null);
    } else {
      setSelectedPrezzo(null);
    }
  }, [formData.area, formData.fascia_prezzo_cliente, allPrezzi]);

  // 7. CORE LOGIC: Group Tassi
  useEffect(() => {
    if (formData.tabella_conversione && allTassiRaw.length > 0) {
      const filteredTassi = allTassiRaw.filter(t => t.tabella_conversione === formData.tabella_conversione);
      
      const grouped = {};
      filteredTassi.forEach(item => {
        const { tipo, garanzia, fr, tasso, valore, id } = item;
        if (!grouped[tipo]) grouped[tipo] = {};
        if (!grouped[tipo][garanzia]) grouped[tipo][garanzia] = {};
        if (!grouped[tipo][garanzia][fr]) grouped[tipo][garanzia][fr] = { AG: { val: 0, id: null }, NAG: { val: 0, id: null } };
        
        if (tasso === 'AG') grouped[tipo][garanzia][fr].AG = { val: parseFloat(valore), id: id };
        if (tasso === 'NAG') grouped[tipo][garanzia][fr].NAG = { val: parseFloat(valore), id: id };
      });

      setGroupedTassi(grouped);

      // Default Selections if empty
      setSelectedFranchises(prev => {
        const newSelections = { ...prev };
        Object.keys(grouped).forEach(tipoKey => {
          Object.keys(grouped[tipoKey]).forEach(garanziaKey => {
            const availableFranchises = Object.keys(grouped[tipoKey][garanziaKey]).sort((a,b) => Number(a)-Number(b));
            // Only set default if not already set (preserves rehydration)
            if (!newSelections[garanziaKey] || !availableFranchises.includes(newSelections[garanziaKey].toString())) {
              if (availableFranchises.length > 0) newSelections[garanziaKey] = availableFranchises[0];
            }
          });
        });
        return newSelections;
      });
    } else {
      setGroupedTassi({});
    }
  }, [formData.tabella_conversione, allTassiRaw]);

  // Memo Signature
  const checkedGuaranteesSignature = useMemo(() => {
    if (!groupedTassi) return "";
    return Object.keys(groupedTassi)
      .flatMap(tipo => Object.keys(groupedTassi[tipo]))
      .filter(garanzia => formData[garanzia] === true)
      .sort()
      .join(',');
  }, [groupedTassi, formData]);

  // 8. Calculation
  useEffect(() => {
    let totalAg = 0;
    let totalNag = 0;
    Object.keys(groupedTassi).forEach(tipo => {
      Object.keys(groupedTassi[tipo]).forEach(garanzia => {
        if (formData[garanzia] === true) {
          const selectedFr = selectedFranchises[garanzia];
          if (selectedFr && groupedTassi[tipo][garanzia][selectedFr]) {
            const rates = groupedTassi[tipo][garanzia][selectedFr];
            const valAG = typeof rates.AG === 'object' && rates.AG !== null ? rates.AG.val : rates.AG;
            const valNAG = typeof rates.NAG === 'object' && rates.NAG !== null ? rates.NAG.val : rates.NAG;
            totalAg += (parseFloat(valAG) || 0);
            totalNag += (parseFloat(valNAG) || 0);
          }
        }
      });
    });
    const agFormatted = totalAg.toFixed(2);
    const nagFormatted = totalNag.toFixed(2);
    const lordoFormatted = (totalAg + totalNag).toFixed(2);
    const superficie = parseInt(selectedPianoUtilizzoDetails?.superficie) || 0;
    const resaCliente = parseInt(formData.resa_cliente) || 0;
    const prezzoValore = parseFloat(selectedPrezzo?.valore) || 0;
    const calculatedValoreAssicurato = (superficie / 10000) * resaCliente * prezzoValore;
    const calculatedPremioLordo = calculatedValoreAssicurato * (parseFloat(lordoFormatted) / 100);
    const calculatedPremioNetto = calculatedValoreAssicurato * ((0.5 * parseFloat(agFormatted) + parseFloat(nagFormatted)) / 100);

    setFormData(prev => ({
      ...prev,
      ag: agFormatted,
      nag: nagFormatted,
      lordo: lordoFormatted,
      valore_assicurato: isNaN(calculatedValoreAssicurato) ? 0 : calculatedValoreAssicurato.toFixed(2),
      premio_lordo: isNaN(calculatedPremioLordo) ? 0 : calculatedPremioLordo.toFixed(2),
      premio_netto: isNaN(calculatedPremioNetto) ? 0 : calculatedPremioNetto.toFixed(2),
    }));
  }, [formData.resa_cliente, formData.area, JSON.stringify(selectedFranchises), groupedTassi, selectedPrezzo, selectedPianoUtilizzoDetails, checkedGuaranteesSignature]);

  // 9. Validation
  useEffect(() => {
    const warnings = [];
    const resaCliente = parseInt(formData.resa_cliente);
    if (!isNaN(resaCliente)) {
      const resaMax = parseInt(selectedPrezzo?.resa_max);
      if (!isNaN(resaMax) && resaCliente > resaMax) {
        warnings.push(`ATTENZIONE: La Resa Cliente (${resaCliente}) supera la Resa Massima consentita (${resaMax}).`);
      }
      if (selectedPrezzo) {
        const prezzoValore = parseFloat(selectedPrezzo.valore) || 0;
        const isBio = selectedPianoUtilizzoDetails?.bio === true;
        const svToUse = isBio ? parseInt(selectedPrezzo.sv_bio) : parseInt(selectedPrezzo.sv);
        const valoreGenerato = resaCliente * prezzoValore;
        if (!isNaN(svToUse) && valoreGenerato > svToUse) {
          const label = isBio ? "Standard Value BIO" : "Standard Value";
          warnings.push(`ATTENZIONE: Il valore prodotto (${valoreGenerato.toFixed(2)}) supera il ${label} (${svToUse.toFixed(2)}).`);
        }
      }
    }
    setValidationWarnings(warnings);
  }, [formData.resa_cliente, selectedPrezzo, selectedPianoUtilizzoDetails]);

  // 10. Logic: Entity Name Rules
  useEffect(() => {
    if (!nomeCondifesa || ['Caricamento...', 'N/A', 'Errore'].includes(nomeCondifesa)) return;
    const normalizedName = nomeCondifesa.toUpperCase().trim();
    const isIndividualeEntity = normalizedName === "INDIVIDUALE";
    setFormData(prev => {
      let newCondifesa = prev.condifesa;
      let newCaaColdiretti = prev.caa_coldiretti;
      if (isIndividualeEntity) {
        newCondifesa = false;
      } else {
        newCondifesa = true;
        newCaaColdiretti = false;
      }
      if (newCondifesa !== prev.condifesa || newCaaColdiretti !== prev.caa_coldiretti) {
        return { ...prev, condifesa: newCondifesa, caa_coldiretti: newCaaColdiretti };
      }
      return prev;
    });
  }, [nomeCondifesa]);

  // --- HANDLERS ---
  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleFranchiseChange = (garanzia, newValue) => {
    setSelectedFranchises(prev => ({ ...prev, [garanzia]: newValue }));
  };

  // --- SUBMIT ---
  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      const payload = {
        piano_utilizzo_id: formData.piano_utilizzo_id,
        prezzo_id: selectedPrezzo?.id || null,
        contribuzione: formData.contribuzione,
        condifesa: formData.condifesa,
        caa_coldiretti: formData.caa_coldiretti,
        resa_cliente: parseInt(formData.resa_cliente, 10),
        valore_assicurato: parseInt(formData.valore_assicurato),
        premio_lordo: parseFloat(formData.premio_lordo),
        premio_netto: parseFloat(formData.premio_netto),
        ag: parseFloat(formData.ag),
        nag: parseFloat(formData.nag),
        lordo: parseFloat(formData.lordo),
      };
      if (!isUpdateMode) {
        Object.assign(payload, {
          ragione_sociale_id: initialData.ragione_sociale_id,
          ramo_id: initialData.ramo_id,
          intermediario_id: initialData.intermediario_id,
          compagnia_id: initialData.compagnia_id,
        });
      }
      const colMap = {
        "GR": "GR", "VF": "VF", "EP": "EP", "EP_CAT": "EP_CAT",
        "NEVE": "neve", "ALLUVIONE": "alluvione", "GELO": "gelo_brina",
        "SICCITA": "siccita", "COLPO_SOLE": "colpo_sole_vento_caldo",
        "SBALZO_TERMICO": "sbalzo_termico_onda_calore",
        "COLPO_SOLE_CAT": "colpo_sole_vento_caldo_CAT",
        "SBALZO_TERMICO_CAT": "sbalzo_termico_onda_calore_CAT"
      };
      Object.keys(groupedTassi).forEach(tipo => {
        Object.keys(groupedTassi[tipo]).forEach(garanzia => {
          if (formData[garanzia] === true) {
            const fr = selectedFranchises[garanzia];
            const rates = groupedTassi[tipo][garanzia][fr];
            const prefix = colMap[garanzia] || garanzia;
            if (rates?.AG?.id) payload[`${prefix}_AG_id`] = rates.AG.id;
            if (rates?.NAG?.id) payload[`${prefix}_NAG_id`] = rates.NAG.id;
          }
        });
      });

      let ragioneSocialeId;
      if (isUpdateMode && existingPreventivoId) {
        Object.assign(payload, {sale_preventivo_id: existingPreventivoId})
        const response = await patchPreventivoGrandine(payload)
        const [hasChanged, personaId] = response

        if (hasChanged===false) {
          enqueue('Nessuna modifica rilevata.', 'info');
          setIsSubmitting(false);
          return;
        }
        enqueue('Preventivo aggiornato con successo!', 'success');
        ragioneSocialeId = personaId;
      } else {
        const response = await createPreventivoGrandine(payload);
        enqueue('Preventivo creato con successo!', 'success');
        ragioneSocialeId = response;
      }

      if (ragioneSocialeId) {
        navigate(`/preventivi/ragioni-sociali/${ragioneSocialeId}`);
      } else {
        navigate(-1);
      }
    } catch (err) {
      console.error('Errore durante il salvataggio:', err);
      setError(`Errore: ${err.message}.`);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loadingExisting) {
    return <Box sx={{p:3}}><CircularProgress /> <Typography>Caricamento dati esistenti...</Typography></Box>;
  }

  if (error) {
    return <Alert severity="error" sx={{m:3}}>{error}</Alert>;
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        {isUpdateMode ? "Modifica Preventivo Grandine" : "Nuovo Preventivo Grandine"}
      </Typography>
      {errorDependentOptions && <Alert severity="warning" sx={{mb:2}}>{errorDependentOptions}</Alert>}
      
      <Paper elevation={3} sx={{ p: 4 }}>
        <form onSubmit={handleSubmit}>
          <Grid container rowSpacing={3} columnSpacing={{ xs: 1, sm: 2, md: 3 }}>
            {/* 1. TOP SECTION */}
            <Grid size={{xs:12, sm:6}}>
              <FormControl fullWidth>
                <InputLabel>Piano Utilizzo</InputLabel>
                <Select value={formData.piano_utilizzo_id} name="piano_utilizzo_id" onChange={handleChange} label="Piano Utilizzo">
                  <MenuItem value=""><em>Nessuno</em></MenuItem>
                  {pianoUtilizzoOptions.map(o => (
                    <MenuItem key={o.id} value={o.id}>{o.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {selectedPianoUtilizzoDetails && (
              <Grid size={{xs:12, sm:6}}>
                <Paper variant="outlined" sx={{ p: 2, bgcolor: '#f9f9f9' }}>
                  <Typography variant="subtitle2"><b>Riepilogo:</b></Typography>
                  <Typography variant="body2">Comune: {nomeComune} | Condifesa: {nomeCondifesa}</Typography>
                  <Typography variant="body2">Prodotto: {nomeProdotto}</Typography>
                  <Typography variant="body2">Sup: {selectedPianoUtilizzoDetails.superficie} ha | Bio: {selectedPianoUtilizzoDetails.bio ? 'Si' : 'No'}</Typography>
                </Paper>
              </Grid>
            )}

            <Grid size={{xs:3, sm:3}}>
              <FormControl fullWidth disabled={!formData.piano_utilizzo_id}>
                <InputLabel>Area</InputLabel>
                <Select name="area" value={formData.area} onChange={handleChange} label="Area">
                  {areaOptions.map(o => <MenuItem key={o} value={o}>{o}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{xs:3, sm:3}}>
              <FormControl fullWidth disabled={!formData.area}>
                <InputLabel>Fascia Prezzo</InputLabel>
                <Select name="fascia_prezzo_cliente" value={formData.fascia_prezzo_cliente} onChange={handleChange} label="Fascia Prezzo">
                  {fasciaPrezzoOptions.map(o => <MenuItem key={o} value={o}>{o}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{xs:3, sm:3}}>
              <FormControl fullWidth disabled={!formData.fascia_prezzo_cliente}>
                <InputLabel>Tabella Conversione</InputLabel>
                <Select name="tabella_conversione" value={formData.tabella_conversione} onChange={handleChange} label="Tabella Conversione">
                  {tabellaConversioneOptions.map(o => <MenuItem key={o} value={o}>{o}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>

            {/* 2. DYNAMIC TASSI */}
            {Object.keys(groupedTassi).length > 0 && (
              <Grid size={{xs:12}}>
                <Divider sx={{ my: 2 }} />
                <Typography variant="h5" gutterBottom sx={{ color: 'primary.main' }}>
                  Opzioni di Copertura
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
                  <Tooltip title="Segna la casella se il cliente vuole la contribuzione">
                    <FormControlLabel control={<Checkbox checked={formData.contribuzione} onChange={handleChange} name="contribuzione" />} label="Contribuzione" />
                  </Tooltip>
                  <Tooltip title="Segna la casella se il cliente aderisce ad un condifesa...">
                    <FormControlLabel control={<Checkbox checked={formData.condifesa} name="condifesa" disabled={true} sx={{ '&.Mui-disabled': { color: formData.condifesa ? 'primary.main' : 'action.disabled' } }} />} label="Condifesa" />
                  </Tooltip>
                  <Tooltip title="Segna la casella se il cliente presenta la domanda invidualmente...">
                    <FormControlLabel control={<Checkbox checked={formData.caa_coldiretti} onChange={handleChange} name="caa_coldiretti" disabled={nomeCondifesa.toUpperCase().trim() !== "INDIVIDUALE"} sx={{ '&.Mui-disabled': { color: formData.caa_coldiretti ? 'primary.main' : 'action.disabled' } }} />} label="Caa/Coldiretti" />
                  </Tooltip>
                </Box>
                {Object.keys(groupedTassi).map((tipo) => (
                  <Paper key={tipo} variant="outlined" sx={{ p: 2, mb: 2 }}>
                    <Typography variant="h6" sx={{ mb: 1, fontSize: '1rem', fontWeight: 'bold' }}>{tipo}</Typography>
                    <Grid container spacing={2}>
                      {Object.keys(groupedTassi[tipo]).map((garanzia) => {
                        const isChecked = formData[garanzia] || false;
                        const availableFranchises = groupedTassi[tipo][garanzia];
                        const frKeys = Object.keys(availableFranchises).sort((a, b) => Number(a) - Number(b));
                        const currentFr = selectedFranchises[garanzia] || (frKeys.length > 0 ? frKeys[0] : "");
                        const currentRates = currentFr ? availableFranchises[currentFr] : null;
                        return (
                          <Grid size={{xs:12, sm:6, md:4, lg:3}} key={garanzia}>
                            <Box sx={{ border: isChecked ? '1px solid #1976d2' : '1px solid #e0e0e0', borderRadius: 1, p: 1.5, bgcolor: isChecked ? '#f0f7ff' : 'white' }}>
                              <FormControlLabel control={<Checkbox checked={isChecked} onChange={handleChange} name={garanzia} />} label={garanzia} sx={{ width: '100%', mb: 0.5 }} />
                              {isChecked && (
                                <Box sx={{ pl: 4 }}>
                                  <FormControl size="small" fullWidth sx={{ mb: 1 }}>
                                    <InputLabel>Franchigia</InputLabel>
                                    <Select value={currentFr} label="Franchigia" onChange={(e) => handleFranchiseChange(garanzia, e.target.value)}>
                                      {frKeys.map(fr => <MenuItem key={fr} value={fr}>{fr}%</MenuItem>)}
                                    </Select>
                                  </FormControl>
                                  {currentRates && (
                                    <Typography variant="caption" display="block" color="text.secondary">
                                      AG: <b>{currentRates.AG?.val?.toFixed(2)}</b> | NAG: <b>{currentRates.NAG?.val?.toFixed(2)}</b>
                                    </Typography>
                                  )}
                                </Box>
                              )}
                            </Box>
                          </Grid>
                        );
                      })}
                    </Grid>
                  </Paper>
                ))}
              </Grid>
            )}

            {/* 3. BOTTOM SECTION */}
            <Grid size={{xs:12}} container spacing={2}>
              <Grid size={{xs:6, sm:3}}><TextField label="AG Totale" value={formData.ag} fullWidth InputProps={{readOnly: true}} /></Grid>
              <Grid size={{xs:6, sm:3}}><TextField label="NAG Totale" value={formData.nag} fullWidth InputProps={{readOnly: true}} /></Grid>
              <Grid size={{xs:6, sm:3}}><TextField label="Lordo Totale %" value={formData.lordo} fullWidth InputProps={{readOnly: true}} /></Grid>
              <Grid size={{xs:6, sm:3}}>
                <TextField label="Resa Cliente" name="resa_cliente" type="number" value={formData.resa_cliente} onChange={handleChange} fullWidth color={validationWarnings.length > 0 ? "warning" : "primary"} focused={validationWarnings.length > 0} helperText={prodottoDetails?.resa_max ? `Resa Max: ${prodottoDetails.resa_max}` : ""} InputProps={{ inputProps: { min: 0 } }} />
              </Grid>
              {validationWarnings.length > 0 && (
                <Grid size={{xs:12}}>
                  <Alert severity="warning" variant="filled">
                    <Typography variant="subtitle2" fontWeight="bold">Verifiche di Conformità:</Typography>
                    <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                      {validationWarnings.map((msg, index) => <li key={index}>{msg}</li>)}
                    </ul>
                  </Alert>
                </Grid>
              )}
              <Grid size={{xs:12}}><Divider /></Grid>
              <Grid size={{xs:12, sm:4}}><TextField label="Valore Assicurato" value={formData.valore_assicurato} fullWidth InputProps={{readOnly: true}} /></Grid>
              <Grid size={{xs:12, sm:4}}><TextField label="Premio Lordo" value={formData.premio_lordo} fullWidth InputProps={{readOnly: true}} /></Grid>
              <Grid size={{xs:12, sm:4}}><TextField label="Premio Netto" value={formData.premio_netto} fullWidth InputProps={{readOnly: true}} /></Grid>
              <Grid size={{xs:12}} sx={{ mt: 2 }}>
                <Button type="submit" variant="contained" size="large" fullWidth disabled={isSubmitting}>
                  {isSubmitting ? <CircularProgress size={24} color="inherit" /> : (isUpdateMode ? "Aggiorna Preventivo" : "Salva Preventivo")}
                </Button>
              </Grid>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Box>
  );
};

export default GrandinePage;