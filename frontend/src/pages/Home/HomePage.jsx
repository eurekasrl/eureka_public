import React from 'react';
import { Typography, Box, Button } from '@mui/material';
import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <Box sx={{ my: 4, textAlign: 'center' }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Benvenuto nel Gestionale Eureka
      </Typography>
      <Typography variant="h6" component="h2" color="text.secondary" sx={{ mb: 4 }}>
        La tua piattaforma integrata per la gestione delle polizze agricole.
      </Typography>
      <Box sx={{ '& button': { m: 1 } }}>
        <Button variant="contained" component={Link} to="/admin">
          Admin
        </Button>
        <Button variant="outlined" component={Link} to="/preventivi">
          Preventivi
        </Button>
        <Button variant="outlined" component={Link} to="/piani-utilizzo">Piani di Utilizzo
        </Button>
        <Button variant="outlined" component={Link} to="/tassi">Tassi
        </Button>
      </Box>
    </Box>
  );
};

export default HomePage;