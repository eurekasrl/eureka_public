import React, { useEffect, useState } from 'react';
import { 
  Box, Tabs, Tab, CircularProgress, Alert,
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, List, ListItem, ListItemIcon, ListItemText, Typography
} from '@mui/material';
import { Warning, ErrorOutline, AttachFile, Send, Email as EmailIcon } from '@mui/icons-material';
import { useParams } from 'react-router-dom';

// --- API IMPORTS ---
import { 
    getGruppoById, getPreventiviByGruppo, 
    getRagioneSocialeById, getPreventiviByRagioneSociale,
    downloadPreventiviCSV, getRagioneSocialeDocuments, 
    uploadRagioneSocialeDocument, deleteRagioneSocialeDocument,
    sendPreventiviEmail, deleteArchiveById
} from '../../../api'; 

// --- COMPONENT IMPORTS ---
import SelectPreventiviDialog from '../../../components/SelectPreventiviDialog';
import AnagraficaCompany from '../../../components/Clienti/AnagraficaCompany';
import AnagraficaGroup from '../../../components/Clienti/AnagraficaGroup';
import ClientHeader from '../../../components/Clienti/ClientHeader';
import UploadDocDialog from '../../../components/Clienti/UploadDocDialog';
import PreventiviTab from '../../../components/Clienti/tabs/PreventiviTab';
import DocumentsTab from '../../../components/Clienti/tabs/DocumentsTab';
import ConfirmDialog from '../../../components/ConfirmDialog';
import { useSnackbar } from '../../../context/SnackbarProvider';

const ClientiPage = () => {
  const { gruppoId, ragioneSocialeId } = useParams();
  const contextType = gruppoId ? 'gruppo' : 'ragione_sociale';
  const entityId = gruppoId || ragioneSocialeId;

  // --- MAIN STATE ---
  const [data, setData] = useState(null);
  const [preventiviData, setPreventiviData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);

  // --- DOCS STATE ---
  const [docsData, setDocsData] = useState([]);
  const [diagnostic, setDiagnostic] = useState(null);
  const [docsLoading, setDocsLoading] = useState(false);

  // --- DIALOG STATE (The Orchestrator) ---
  const [uploadDialog, setUploadDialog] = useState({ open: false, docType: null, loading: false });
  const [tempUploadData, setTempUploadData] = useState(null);
  const [selectDialog, setSelectDialog] = useState({ open: false, mode: null, list: [], loading: false, initialSelection: [], params: null });
  const [confirmDialog, setConfirmDialog] = useState({ open: false, title: '', message: '', onConfirm: null, color: 'primary' });
  const enqueue = useSnackbar();
  const [missingDocsDialog, setMissingDocsDialog] = useState({ open: false, missingList: [], pendingActionParams: null });

  // ==========================================
  // DATA FETCHING
  // ==========================================
  useEffect(() => {
    if (!entityId) return;
    const fetchData = async () => {
      setLoading(true);
      try {
        const fetchInfoFn = contextType === 'gruppo' ? getGruppoById : getRagioneSocialeById;
        const fetchPrevFn = contextType === 'gruppo' ? getPreventiviByGruppo : getPreventiviByRagioneSociale;
        const [entityResult, prevResult] = await Promise.all([ fetchInfoFn(entityId), fetchPrevFn(entityId, "admin") ]);
        setData(entityResult);
        setPreventiviData(prevResult || {});
      } catch (err) { setError(err.message || "Errore caricamento dati"); } 
      finally { setLoading(false); }
    };
    fetchData();
  }, [entityId, contextType]);

  const fetchDocs = async () => {
    setDocsLoading(true);
    try {
      const result = await getRagioneSocialeDocuments(entityId);
      setDiagnostic(result.folder_diagnostic);
      setDocsData(result.documents);
      return result.documents;
    } catch {
      enqueue("Errore lista documenti", "error");
      return [];
    } finally { setDocsLoading(false); }
  };

  useEffect(() => {
    if (tabValue === 2 && contextType === 'ragione_sociale') fetchDocs();
  }, [tabValue, contextType]);

  // ==========================================
  // LOGIC HELPERS
  // ==========================================
  const flattenPreventivi = (rawData, filterFn = null) => {
    let flatList = [];
    if (contextType === 'gruppo' && typeof rawData === 'object') {
       Object.entries(rawData).forEach(([pgId, list]) => {
         const company = data?.ragione_sociale?.find(p => String(p.id).toLowerCase() === String(pgId).toLowerCase());
         if(Array.isArray(list)) list.forEach(p => flatList.push({ ...p, azienda_nome: company?.nome || "Azienda", comune_nome: p.comune_nome || company?.comune?.nome || "-", id: p.id || p.preventivo_id }));
       });
    } else if (Array.isArray(rawData)) {
       flatList = rawData.map(p => ({ ...p, azienda_nome: data?.nome, comune_nome: p.comune_nome || data?.comune?.nome, id: p.id || p.preventivo_id }));
    }
    return filterFn ? flatList.filter(filterFn) : flatList;
  };

  // ==========================================
  // FLOW: UPLOAD ORCHESTRATOR
  // ==========================================
  const handleOpenUpload = (docObject) => setUploadDialog({ open: true, docType: docObject, loading: false });

  const handleUploadStep1 = async (fileData) => {
    const docType = uploadDialog.docType;
    if (docType.entity === false) {
        setTempUploadData(fileData);
        setUploadDialog(prev => ({ ...prev, open: false })); 
        setSelectDialog({ open: true, mode: 'LINK_DOC', list: [], loading: true, initialSelection: [], params: null });
        try {
            const fetchFn = contextType === 'gruppo' ? getPreventiviByGruppo : getPreventiviByRagioneSociale;
            const result = await fetchFn(entityId, "documenti", null, fileData.anno);
            const eligibleList = flattenPreventivi(result);
            setSelectDialog(prev => ({ ...prev, list: eligibleList, loading: false }));
        } catch (e) { 
          console.error("API Error in handleUploadStep1:", e); // Added logging to help debug
            setSelectDialog(prev => ({ ...prev, open: false }));
            enqueue("Errore recupero preventivi", "error");
        }
    } else {
        await performFinalUpload(fileData, []); 
    }
  };

  const performFinalUpload = async (fileData, linkedIds) => {
    const loadingSetter = selectDialog.open ? (v) => setSelectDialog(p=>({...p, loading:v})) : (v) => setUploadDialog(p=>({...p, loading:v}));
    loadingSetter(true);
    try {
      await uploadRagioneSocialeDocument(entityId, uploadDialog.docType.id, fileData.file, fileData.anno, fileData.signed, fileData.sent, linkedIds);
      enqueue("Archiviato con successo!", 'success');
      setSelectDialog(p => ({ ...p, open: false }));
      setUploadDialog(p => ({ ...p, open: false }));
      setTempUploadData(null);
      fetchDocs();
    } catch { enqueue("Errore upload", 'error'); }
    finally { loadingSetter(false); }
  };

  // ==========================================
  // FLOW: EMAIL
  // ==========================================
  const handleOpenEmailModal = async (ramoId, anno, isIntermediario = false) => {
    const mode = isIntermediario ? 'EMAIL_INTERMEDIARIO' : 'EMAIL_CLIENTE';
    setSelectDialog({ open: true, mode, loading: true, list: [], initialSelection: [], params: { ramoId, anno } });
    try {
      const fetchFn = contextType === 'gruppo' ? getPreventiviByGruppo : getPreventiviByRagioneSociale;
      const result = await fetchFn(entityId, isIntermediario ? "email-intermediario" : "email-cliente", ramoId, anno);
      const flatList = flattenPreventivi(result);
      const targetStatus = isIntermediario ? 'approvato' : 'creato';
      setSelectDialog(prev => ({ ...prev, list: flatList, initialSelection: flatList.filter(p => String(p.stato).toLowerCase() === targetStatus).map(p => p.id), loading: false }));
    } catch { setSelectDialog(prev => ({ ...prev, loading: false })); }
  };

  const handleIntermediarioCheck = async (ramoId, anno) => {
    let currentDocs = docsData;
    if (contextType === 'ragione_sociale' && currentDocs.length === 0) currentDocs = await fetchDocs();
    const missing = currentDocs.filter(d => (d.stato === 'MISSING' || d.stato === 'FILE_NOT_FOUND') && (d.documento.mandatory));
    if (missing.length > 0) setMissingDocsDialog({ open: true, missingList: missing, pendingActionParams: { ramoId, anno } });
    else handleOpenEmailModal(ramoId, anno, true);
  };

  const handleSelectionConfirm = async (selectedIds) => {
      if (selectDialog.mode === 'LINK_DOC') await performFinalUpload(tempUploadData, selectedIds);
      else {
        const type = selectDialog.mode === 'EMAIL_INTERMEDIARIO' ? 'intermediario': 'cliente'
        await performSendEmail(selectedIds, type)};
  };

  const performSendEmail = async (selectedIds, destinatario) => {
    setSelectDialog(p => ({ ...p, loading: true }));
    try {
      await sendPreventiviEmail({ client_level_id: entityId, client_level: contextType, ramo_id: selectDialog.params.ramoId, anno: selectDialog.params.anno, selected_ids: selectedIds }, destinatario);
      enqueue('Email inviata!', 'success');
      setSelectDialog(p => ({ ...p, open: false }));
    } catch { enqueue("Errore invio email", 'error'); }
    finally { setSelectDialog(p => ({ ...p, loading: false })); }
  };

  // ==========================================
  // MISC HANDLERS
  // ==========================================
  const handleDeleteDoc = (docId, archiveId = null) => {
    const isGroupDelete = archiveId === null;
    const msg = isGroupDelete
      ? "ATTENZIONE: Stai per eliminare TUTTI i file caricati per questo documento. Continuare?"
      : "Sei sicuro di voler eliminare questo specifico file?";

    setConfirmDialog({
      open: true,
      title: 'Elimina documento',
      message: msg,
      color: isGroupDelete ? 'error' : 'primary',
      onConfirm: async () => {
        setConfirmDialog(prev => ({ ...prev, open: false }));
        setDocsLoading(true);
        try {
          if (isGroupDelete) {
            await deleteRagioneSocialeDocument(entityId, docId);
          } else {
            await deleteArchiveById(archiveId);
          }
          enqueue("Eliminato con successo", "success");
          await fetchDocs();
        } catch {
          enqueue("Errore eliminazione", "error");
        } finally { setDocsLoading(false); }
      },
    });
  };

  const handleDownloadCsv = async (ramoId, anno) => {
    try {
      const res = await downloadPreventiviCSV(entityId, contextType, ramoId, anno);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a'); link.href = url; link.setAttribute('download', `prev.csv`); document.body.appendChild(link); link.click(); link.remove();
    } catch { enqueue('Errore CSV', 'error'); }
  };

  // ==========================================
  // RENDER
  // ==========================================
  if (loading) return <Box display="flex" justifyContent="center" p={4}><CircularProgress /></Box>;
  if (error || !data) return <Alert severity="error">{error || "Entità non trovata"}</Alert>;

  // Dialog Config Builder
  const getSelectDialogConfig = () => {
    if(selectDialog.mode === 'LINK_DOC') return { title: "Collega Preventivi", subtitle: `Seleziona i preventivi per "${uploadDialog.docType?.nome}".`, confirmLabel: "Carica", confirmColor: "secondary", confirmIcon: <AttachFile fontSize="small" /> };
    if(selectDialog.mode === 'EMAIL_CLIENTE') return { title: "Invio Email al Cliente", subtitle: "Seleziona preventivi per il report.", confirmLabel: "Invia", confirmColor: "primary", confirmIcon: <Send fontSize="small" /> };
    return { title: "Invio all'Intermediario", subtitle: "Richiesta copertura.", confirmLabel: "Invia", confirmColor: "warning", confirmIcon: <EmailIcon fontSize="small" /> };
  };

  return (
    <Box sx={{ p: 3, backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      <ClientHeader data={data} type={contextType} />

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="Anagrafica" />
          <Tab label="Preventivi" />
          <Tab label="Documenti" />
        </Tabs>
      </Box>

      {/* --- CONTENT AREA --- */}
      {tabValue === 0 && (contextType === 'gruppo' ? <AnagraficaGroup data={data} /> : <AnagraficaCompany data={data} />)}

      {tabValue === 1 && (
        <PreventiviTab 
            preventiviData={preventiviData}
            loading={loading}
            contextType={contextType}
            onEmail={(ramo, anno) => handleOpenEmailModal(ramo, anno, false)}
            onDownload={handleDownloadCsv}
            onIntermediario={handleIntermediarioCheck}
        />
      )}

      {tabValue === 2 && (
        <DocumentsTab 
            contextType={contextType}
            entityId={entityId}
            docsData={docsData}
            loading={docsLoading}
            diagnostic={diagnostic}
            onRefresh={fetchDocs}
            onOpenUpload={handleOpenUpload}
            onDelete={handleDeleteDoc}
        />
      )}

      {/* --- DIALOGS (Orchestrated by this Page) --- */}
      
      <UploadDocDialog 
        open={uploadDialog.open} onClose={() => setUploadDialog(p => ({...p, open: false}))}
        docName={uploadDialog.docType?.nome} docRequiresSig={uploadDialog.docType?.signed}
        onConfirm={handleUploadStep1} loading={uploadDialog.loading}
      />

      <SelectPreventiviDialog 
        open={selectDialog.open} onClose={() => setSelectDialog(p => ({...p, open: false}))}
        preventivi={selectDialog.list} loading={selectDialog.loading}
        onConfirm={handleSelectionConfirm} initialSelectedIds={selectDialog.initialSelection}
        {...getSelectDialogConfig()}
      />

      <Dialog open={missingDocsDialog.open} onClose={() => setMissingDocsDialog(p => ({...p, open: false}))} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'warning.main' }}><Warning /> Documenti Mancanti</DialogTitle>
        <DialogContent>
            <Typography variant="body1">Risultano mancanti i seguenti documenti:</Typography>
            <List dense>{missingDocsDialog.missingList.map((d, i) => <ListItem key={i}><ListItemIcon><ErrorOutline color="error" /></ListItemIcon><ListItemText primary={d.documento?.nome} /></ListItem>)}</List>
        </DialogContent>
        <DialogActions>
            <Button onClick={() => setMissingDocsDialog(p => ({...p, open: false}))}>Annulla</Button>
            <Button onClick={() => { setMissingDocsDialog(p => ({...p, open: false})); handleOpenEmailModal(missingDocsDialog.pendingActionParams.ramoId, missingDocsDialog.pendingActionParams.anno, true); }} color="warning" variant="contained">Procedi</Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={confirmDialog.open}
        title={confirmDialog.title}
        message={confirmDialog.message}
        onConfirm={confirmDialog.onConfirm}
        onCancel={() => setConfirmDialog(prev => ({ ...prev, open: false }))}
        confirmColor={confirmDialog.color}
      />
    </Box>
  );
};

export default ClientiPage;