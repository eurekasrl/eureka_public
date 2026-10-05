import React, { useEffect, useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, Typography, CircularProgress, Alert, Paper,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Button, IconButton, TextField, Dialog, DialogTitle, DialogContent, DialogActions,
  FormControlLabel, Checkbox, Autocomplete, AlertTitle
} from '@mui/material';
import ConfirmDialog from '../../../components/ConfirmDialog';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import debounce from 'lodash.debounce';
import {
  getDynamicTableSchema, getDynamicTableData,
  addDynamicTableRow, updateDynamicTableRow, deleteDynamicTableRow,
  getComuni,
  getComune
} from '../../../api';
import { formatNumberForDisplay } from '../../../components/utils'

const TableDataPage = () => {
  const { schemaName, tableName } = useParams();
  const navigate = useNavigate();

  const [schema, setSchema] = useState([]);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [fkLabels, setFkLabels] = useState({}); // { col_name: { raw_id: 'Human label' } }

  const [openFormDialog, setOpenFormDialog] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [currentEditRow, setCurrentEditRow] = useState({});
  const [formErrors, setFormErrors] = useState({});
  const [confirmDialog, setConfirmDialog] = useState({ open: false, title: '', message: '', onConfirm: null, color: 'primary' });

  const [comuniOptions, setComuniOptions] = useState([]);
  const [comuniLoading, setComuniLoading] = useState(false);

  const comuneFields = ['codice_comune', 'codice_comune_di_nascita']; 
  const numericColumnsToExcludeFromFormatting  = ['anno', ...comuneFields]; 
  
  const primaryKeyColumn = schema.find(col => col.primary_key);
  const hideField = col => ['id', 'created_at', 'updated_at'].includes(col.name);

  // --- WARNING LOGIC START ---
  // Check if the current table is one of the specific tables that require a warning
  const isRiskyTable = schemaName === 'grandine' && 
    ['piano_utilizzo', 'piano_utilizzo_dettagliato'].includes(tableName);
  // --- WARNING LOGIC END ---

  const fetchComuniDebounced = useMemo(() => debounce(async (query) => {
    setComuniLoading(true);
    try {
      const res = await getComuni(query);
      if (Array.isArray(res)) setComuniOptions(res);
    } catch (e) {
      console.error(e);
    } finally {
      setComuniLoading(false);
    }
  }, 300), []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [tableSchema, tableData] = await Promise.all([
        getDynamicTableSchema(schemaName, tableName),
        getDynamicTableData(schemaName, tableName),
      ]);
      setSchema(tableSchema);
      setData(tableData);

      // Resolve FK labels: for each FK column, fetch the referenced table and
      // build a map of id → human-readable label. Skipped for large tables.
      const fkCols = tableSchema.filter(col => col.fk);
      if (fkCols.length > 0) {
        const labelMaps = {};
        await Promise.all(fkCols.map(async (col) => {
          try {
            const { referred_schema, referred_table, referred_column, label_column } = col.fk;
            const refData = await getDynamicTableData(referred_schema, referred_table, { limit: 500 });
            const map = {};
            refData.forEach(row => {
              if (row[referred_column] != null) {
                map[String(row[referred_column])] = row[label_column] ?? row[referred_column];
              }
            });
            labelMaps[col.name] = map;
          } catch {
            // FK label resolution is best-effort — never block the main table
          }
        }));
        setFkLabels(labelMaps);
      }
    } catch (err) {
      console.error(err);
      setError(`Errore nel caricamento dei dati o schema per ${schemaName}.${tableName}.`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [schemaName, tableName]);

  const handleOpenAdd = () => {
    setIsEditing(false);
    setCurrentEditRow({});
    setFormErrors({});
    setOpenFormDialog(true);
  };

  const handleOpenEdit = async (row) => {
    setIsEditing(true);
    setFormErrors({});
    setOpenFormDialog(true);

    const fullRow = { ...row };

    setComuniLoading(true);
    try {
      const fetchPromises = comuneFields.map(async (field) => {
        if (fullRow[field]) {
          try {
            const res = await getComune(fullRow[field].toString());
            if (res && res[0]) {
              fullRow[`${field}_obj`] = res[0]; 
              setComuniOptions(prev => {
                const exists = prev.find(p => p.codice_comune === res[0].codice_comune);
                return exists ? prev : [...prev, res[0]];
              });
            }
          } catch (e) {
            console.error(`Error loading ${field}:`, e);
          }
        }
      });
  
      await Promise.all(fetchPromises);
    } finally {
      setComuniLoading(false);
    }
  
    setCurrentEditRow(fullRow);
  };

  const handleCloseFormDialog = () => setOpenFormDialog(false);

  const validateForm = (formData) => {
    const errors = {};
    schema.forEach(col => {
      if (!col.nullable && !col.autoincrement && !col.default && !formData[col.name] && !isEditing) {
        errors[col.name] = `${col.name} è richiesto.`;
      }
      if ((col.type === 'integer' || col.type === 'number') && formData[col.name] && isNaN(Number(formData[col.name]))) {
        errors[col.name] = `${col.name} deve essere un numero valido.`;
      }
    });
    return errors;
  };

  const handleFormSubmit = () => {
    const errors = validateForm(currentEditRow);
    if (Object.keys(errors).length) { setFormErrors(errors); return; }

    const doSubmit = async () => {
      setLoading(true);
      setError(null);
      try {
        const dataToSubmit = { ...currentEditRow };
        comuneFields.forEach(field => {
          if (dataToSubmit[`${field}_obj`]) {
            dataToSubmit[field] = dataToSubmit[`${field}_obj`].codice_comune;
          }
          delete dataToSubmit[`${field}_obj`];
        });

        if (isEditing) {
          if (!primaryKeyColumn) throw new Error("Primary key column not found.");
          if (!dataToSubmit[primaryKeyColumn.name]) throw new Error("Primary key value missing.");
          const updateData = {};
          schema.forEach(col => {
            let value = dataToSubmit[col.name];
            if (col.type === 'boolean') value = !!value;
            if (value !== undefined) updateData[col.name] = value;
          });
          await updateDynamicTableRow(schemaName, tableName, dataToSubmit[primaryKeyColumn.name], updateData);
        } else {
          await addDynamicTableRow(schemaName, tableName, dataToSubmit);
        }
        await fetchData();
        setOpenFormDialog(false);
      } catch (err) {
        console.error(err);
        setError(`Errore durante ${isEditing ? "l'aggiornamento" : "l'aggiunta"}: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    if (isRiskyTable) {
      setConfirmDialog({
        open: true,
        title: 'Attenzione Critica',
        message: 'Stai modificando una tabella che impatta i calcoli. Se procedi, i PREVENTIVI collegati verranno RESETTATI. Sei sicuro di voler continuare?',
        onConfirm: () => { setConfirmDialog(prev => ({ ...prev, open: false })); doSubmit(); },
        color: 'warning',
      });
    } else {
      doSubmit();
    }
  };

  const handleDeleteRow = (row) => {
    const confirmMessage = isRiskyTable
      ? "ATTENZIONE: Eliminando questa riga i relativi PREVENTIVI verranno RESETTATI. Sei sicuro di voler procedere?"
      : "Sei sicuro di voler eliminare questa riga?";

    setConfirmDialog({
      open: true,
      title: 'Conferma eliminazione',
      message: confirmMessage,
      color: isRiskyTable ? 'error' : 'primary',
      onConfirm: async () => {
        setConfirmDialog(prev => ({ ...prev, open: false }));
        setLoading(true);
        setError(null);
        try {
          if (!primaryKeyColumn) throw new Error("Colonna chiave primaria non trovata.");
          await deleteDynamicTableRow(schemaName, tableName, row[primaryKeyColumn.name]);
          await fetchData();
        } catch (err) {
          console.error(err);
          setError(`Errore durante l'eliminazione: ${err.message}`);
        } finally {
          setLoading(false);
        }
      },
    });
  };

  const renderFormField = (col) => {
    if (comuneFields.includes(col.name)) {
      return (
        <Autocomplete
          key={col.name}
          options={comuniOptions}
          loading={comuniLoading}
          getOptionLabel={(opt) => opt.nome || ''}
          value={currentEditRow[`${col.name}_obj`] || null}
          onInputChange={(e, value) => fetchComuniDebounced(value.trim())}
          onChange={(e, newValue) =>
            setCurrentEditRow({
              ...currentEditRow,
               [col.name]: newValue?.codice_comune || null,
              [`${col.name}_obj`]: newValue || null      
            })
          }
          isOptionEqualToValue={(option, value) => option.codice_comune === value?.codice_comune}
          renderInput={(params) => (
            <TextField
              {...params}
              label={col.name.replace(/_/g, ' ')}
              margin="normal"
              required={!col.nullable}
              variant="outlined"
              InputProps={{
                ...params.InputProps,
                endAdornment: (
                  <>
                    {comuniLoading ? <CircularProgress color="inherit" size={20} /> : null}
                    {params.InputProps.endAdornment}
                  </>
                ),
              }}
            />
          )}
        />
      );
    }

    if (col.type === 'boolean') {
      return (
        <FormControlLabel
          key={col.name}
          control={<Checkbox checked={!!currentEditRow[col.name]} onChange={e => setCurrentEditRow({ ...currentEditRow, [col.name]: e.target.checked })} />}
          label={col.name}
        />
      );
    }

    if (col.type === 'integer' || col.type === 'number') {
      return (
        <TextField
          key={col.name}
          fullWidth
          margin="normal"
          label={`${col.name}${!col.nullable ? ' *' : ''}`}
          type="number" 
          value={currentEditRow[col.name] === null || currentEditRow[col.name] === undefined ? '' : currentEditRow[col.name]}
          onChange={e => setCurrentEditRow({ ...currentEditRow, [col.name]: e.target.value === '' ? null : Number(e.target.value) })}
          error={!!formErrors[col.name]}
          helperText={formErrors[col.name]}
          disabled={col.primary_key && isEditing && !col.autoincrement}
        />
      );
    }

    return (
      <TextField
        key={col.name}
        fullWidth
        margin="normal"
        label={`${col.name}${!col.nullable ? ' *' : ''}`}
        value={currentEditRow[col.name] || ''}
        onChange={e => setCurrentEditRow({ ...currentEditRow, [col.name]: e.target.value })}
        error={!!formErrors[col.name]}
        helperText={formErrors[col.name]}
        disabled={col.primary_key && isEditing && !col.autoincrement}
      />
    );
  };

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if (error) return <Box sx={{ mt: 4 }}><Alert severity="error">{error}</Alert></Box>;
  if (!schema.length) return <Box sx={{ mt: 4 }}><Alert severity="info">Schema tabella non disponibile.</Alert><Button onClick={() => navigate('/admin/tables')}>Torna</Button></Box>;

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>Dati Tabella: {schemaName}.{tableName}</Typography>

      <Button variant="contained" startIcon={<AddIcon />} sx={{ mb: 2 }} onClick={handleOpenAdd}>
        Aggiungi Nuova Riga
      </Button>

      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }}>
          <TableHead>
            <TableRow>
              {schema.map(col => <TableCell key={col.name}>{col.name}{col.primary_key ? ' (PK)' : ''}</TableCell>)}
              <TableCell>Azioni</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.length ? data.map((row, idx) => (
              <TableRow key={row[primaryKeyColumn?.name] || idx}>
                {schema.map(col => {
                  const rawVal = row[col.name];
                  let display;
                  if (col.fk && fkLabels[col.name] && rawVal != null) {
                    const label = fkLabels[col.name][String(rawVal)];
                    display = label
                      ? <span title={String(rawVal)}>{label}</span>
                      : <span style={{ color: '#999', fontStyle: 'italic' }}>{String(rawVal)}</span>;
                  } else if ((col.type === 'integer' || col.type === 'number') && !numericColumnsToExcludeFromFormatting.includes(col.name)) {
                    display = formatNumberForDisplay(rawVal ?? 'NULL');
                  } else {
                    display = String(rawVal ?? 'NULL');
                  }
                  return <TableCell key={col.name}>{display}</TableCell>;
                })}
                <TableCell>
                  <IconButton onClick={() => handleOpenEdit(row)}><EditIcon /></IconButton>
                  <IconButton onClick={() => handleDeleteRow(row)}><DeleteIcon color="error" /></IconButton>
                </TableCell>
              </TableRow>
            )) : (
              <TableRow>
                <TableCell colSpan={schema.length + 1} align="center">Nessun dato disponibile.</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={openFormDialog} onClose={handleCloseFormDialog} fullWidth maxWidth="sm">
        <DialogTitle>{isEditing ? `Modifica Riga in ${schemaName}.${tableName}` : `Aggiungi Riga a ${schemaName}.${tableName}`}</DialogTitle>
        <DialogContent>
          {/* --- INSERTED WARNING ALERT --- */}
          {isRiskyTable && (
            <Alert severity="warning" sx={{ mt: 2, mb: 2 }}>
              <AlertTitle>Attenzione</AlertTitle>
              Qualsiasi modifica a questa tabella comporterà il <strong>reset dei preventivi</strong> collegati.
            </Alert>
          )}
          {/* ------------------------------- */}
          
          {schema.map(col => !hideField(col) && renderFormField(col))}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseFormDialog}>Annulla</Button>
          <Button 
            variant="contained" 
            onClick={handleFormSubmit} 
            disabled={loading}
            color={isRiskyTable ? "warning" : "primary"} // Change button color to warn visually
          >
            {loading ? <CircularProgress size={24} /> : (isEditing ? 'Salva Modifiche' : 'Aggiungi Riga')}
          </Button>
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

export default TableDataPage;