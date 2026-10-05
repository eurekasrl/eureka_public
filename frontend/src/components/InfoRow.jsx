// src/components/common/InfoRow.jsx
import React, { useState } from 'react';
import { Box, Typography, IconButton, Tooltip, Snackbar, Alert } from '@mui/material';
import { ContentCopy } from '@mui/icons-material';

const InfoRow = ({ label, value, copyable = false }) => {
  const [open, setOpen] = useState(false);

  const handleCopy = () => {
    if (value) {
      navigator.clipboard.writeText(value);
      setOpen(true); // Show success message
    }
  };

  const handleClose = () => setOpen(false);

  return (
    <>
      <Box 
        display="flex" 
        justifyContent="space-between" 
        alignItems="center" 
        py={1.5} 
        borderBottom="1px solid #eee"
        sx={{ 
          '&:last-child': { borderBottom: 'none' } // Remove border for last item
        }}
      >
        <Typography variant="body2" color="textSecondary" sx={{ minWidth: '120px' }}>
          {label}
        </Typography>
        
        <Box display="flex" alignItems="center" gap={1} sx={{ textAlign: 'right' }}>
          <Typography variant="body1" fontWeight={500}>
            {value || '-'}
          </Typography>

          {/* Render Copy Button only if copyable is true and value exists */}
          {copyable && value && (
            <Tooltip title="Copia">
              <IconButton size="small" onClick={handleCopy} sx={{ ml: 0.5 }}>
                <ContentCopy fontSize="inherit" />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      </Box>

      {/* Small popup notification when copied */}
      <Snackbar 
        open={open} 
        autoHideDuration={2000} 
        onClose={handleClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleClose} severity="success" sx={{ width: '100%' }}>
          Copiato negli appunti!
        </Alert>
      </Snackbar>
    </>
  );
};

export default InfoRow;