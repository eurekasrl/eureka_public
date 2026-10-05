import React from 'react';
import { Box, Typography, Container } from '@mui/material';

const Footer = () => {
  return (
    <Box sx={{ bgcolor: 'primary.main', color: 'white', py: 3, mt: 'auto' }}>
      <Container sx={{width: '100%'}}>
        <Typography variant="body2" align="center">
          © {new Date().getFullYear()} Eureka Srl. Tutti i diritti riservati.
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer;