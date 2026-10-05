// src/components/Preventivi/PreventivoStatusChip.jsx
import React from 'react';
import { Chip } from '@mui/material';

// 1. Centralized Logic for Colors
const getStatusColor = (stato) => {
  if (!stato) return 'default';
  
  const normalized = stato.toString().toLowerCase();

  // Success cases
  if (normalized.includes('approvat') || normalized === 'signed' || normalized === 'vinto') {
    return 'success';
  }
  
  // Error/Danger cases
  if (normalized.includes('rifiutat') || normalized === 'rejected' || normalized === 'perso') {
    return 'error';
  }
  
  // Info/Processing cases
  if (normalized.includes('inviat') || normalized === 'sent' || normalized.includes('pending')) {
    return 'info';
  }
  
  // Warning cases
  if (normalized.includes('creato') || normalized === 'draft') {
    return 'default'; // or 'warning'
  }

  // Default fallback
  return 'primary';
};

const PreventiviStatusChip = ({ stato, count, sx, ...props }) => {
  const color = getStatusColor(stato);
  
  // 2. Determine Label format
  // If 'count' is provided, show "Status: Count", otherwise just "Status"
  const label = count !== undefined && count !== null
    ? `${stato}: ${count}`
    : stato;

  return (
    <Chip 
      label={label} 
      color={color} 
      variant="outlined" 
      size="small"
      sx={{ 
        fontWeight: 'bold', 
        textTransform: 'capitalize',
        ...sx 
      }}
      {...props} 
    />
  );
};

export default PreventiviStatusChip;