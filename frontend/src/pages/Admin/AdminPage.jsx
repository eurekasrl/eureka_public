import React from 'react';
import { Typography, Box, Button } from '@mui/material';
import { Link } from 'react-router-dom';

const AdminPage = () => {
  return (
    <Box sx={{ my: 4, textAlign: 'center' }}>
      <Box sx={{ '& button': { m: 1 } }}>
        <Button variant="contained" component={Link} to="/admin/tables">
          Tables
        </Button>
        <Button variant="contained"  component={Link} to="/admin/clienti">
        Clienti
        </Button>
      </Box>
    </Box>
  );
};

export default AdminPage;