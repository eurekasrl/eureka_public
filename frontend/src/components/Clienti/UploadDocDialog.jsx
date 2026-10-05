import React, { useEffect, useState} from 'react';
import { 
  Button, Grid, CircularProgress,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  FormControlLabel, Switch, InputAdornment, Typography, Box
} from '@mui/material';
import {
  CloudUpload, AttachFile, InsertDriveFile
} from '@mui/icons-material';

const UploadDocDialog = ({ 
  open, 
  onClose, 
  docName, 
  docRequiresSig, 
  onConfirm, 
  loading 
}) => {
  const [file, setFile] = useState(null);
  const [anno, setAnno] = useState(new Date().getFullYear());
  const [signed, setSigned] = useState(false);
  const [sent, setSent] = useState(false);

  // Reset state when opening
  useEffect(() => {
    if (open) {
      setFile(null);
      setAnno(new Date().getFullYear());
      setSigned(false);
      setSent(false);
    }
  }, [open]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleConfirm = () => {
    if (!file) return;
    onConfirm({ file, anno, signed, sent });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        Carica Documento
        {/* --- FIX IS HERE: component="div" --- */}
        <Typography variant="subtitle2" color="primary" component="div">
            {docName}
        </Typography>
      </DialogTitle>
      
      <DialogContent dividers>
        <Grid container spacing={3} sx={{ mt: 0.5 }}>
          
          {/* File Input */}
          <Grid item xs={12}>
            <Box display="flex" flexDirection="column" alignItems="center" gap={1}>
                <Button
                variant={file ? "contained" : "outlined"}
                component="label"
                fullWidth
                startIcon={file ? <InsertDriveFile /> : <AttachFile />}
                color={file ? "success" : "primary"}
                sx={{ height: 60, textTransform: 'none', fontSize: '1rem' }}
                >
                {file ? file.name : "Clicca qui per selezionare il file (PDF, IMG...)"}
                <input 
                    type="file" 
                    hidden 
                    accept=".pdf,.jpg,.jpeg,.png,.doc,.docx, .eml" 
                    onChange={handleFileChange} 
                />
                </Button>
                {file && (
                    <Typography variant="caption" color="textSecondary">
                        Dimensione: {(file.size / 1024 / 1024).toFixed(2)} MB
                    </Typography>
                )}
            </Box>
          </Grid>

          {/* Anno Selection */}
          <Grid item xs={12}>
            <TextField
              label="Anno di riferimento"
              type="number"
              fullWidth
              value={anno}
              onChange={(e) => setAnno(parseInt(e.target.value))}
              InputProps={{
                startAdornment: <InputAdornment position="start">🗓</InputAdornment>,
              }}
            />
          </Grid>

          {/* Flags */}
          {docRequiresSig && (
            <Grid item xs={6}>
              <FormControlLabel
                control={<Switch checked={signed} onChange={(e) => setSigned(e.target.checked)} color="success"/>}
                label="Documento Firmato"
              />
            </Grid>
          )}
          
          <Grid item xs={6}>
            <FormControlLabel
              control={<Switch checked={sent} onChange={(e) => setSent(e.target.checked)} color="primary"/>}
              label="Inviato a Compagnia"
            />
          </Grid>

        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading} color="inherit">
            Annulla
        </Button>
        <Button 
          onClick={handleConfirm} 
          variant="contained" 
          disabled={!file || loading}
          startIcon={loading ? <CircularProgress size={20} color="inherit"/> : <CloudUpload />}
        >
          Prosegui
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default UploadDocDialog;