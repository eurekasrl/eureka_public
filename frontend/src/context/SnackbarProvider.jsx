import React, { createContext, useContext, useState, useCallback } from 'react';
import { Snackbar, Alert } from '@mui/material';

const SnackbarContext = createContext(null);

export const SnackbarProvider = ({ children }) => {
  const [state, setState] = useState({ open: false, message: '', severity: 'success' });

  const enqueue = useCallback((message, severity = 'success') => {
    setState({ open: true, message, severity });
  }, []);

  const close = useCallback((_, reason) => {
    if (reason === 'clickaway') return;
    setState(prev => ({ ...prev, open: false }));
  }, []);

  return (
    <SnackbarContext.Provider value={enqueue}>
      {children}
      <Snackbar
        open={state.open}
        autoHideDuration={4000}
        onClose={close}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={close} severity={state.severity} variant="filled" sx={{ width: '100%' }}>
          {state.message}
        </Alert>
      </Snackbar>
    </SnackbarContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useSnackbar = () => {
  const ctx = useContext(SnackbarContext);
  if (!ctx) throw new Error('useSnackbar must be used within a SnackbarProvider');
  return ctx;
};
