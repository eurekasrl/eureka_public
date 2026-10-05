import React from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography } from '@mui/material';

const ConfirmDialog = ({ open, title, message, onConfirm, onCancel, confirmColor = 'primary' }) => (
  <Dialog open={open} onClose={onCancel} maxWidth="xs" fullWidth>
    <DialogTitle>{title}</DialogTitle>
    <DialogContent>
      <Typography variant="body2">{message}</Typography>
    </DialogContent>
    <DialogActions>
      <Button onClick={onCancel} color="inherit">Annulla</Button>
      <Button onClick={onConfirm} variant="contained" color={confirmColor} autoFocus>
        Conferma
      </Button>
    </DialogActions>
  </Dialog>
);

export default ConfirmDialog;
