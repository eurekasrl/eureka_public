import React from 'react';
import { Box, Container, CssBaseline } from '@mui/material';
import Navbar from './Navbar';
import Footer from './Footer'; // Creeremo anche un semplice footer

const Layout = ({ children }) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', width: '100%' }}>
      <CssBaseline />
      <Navbar />
      <Box component="main" sx={{mt:4, mb:4, flexGrow:1, width:'100%', px:{ xs:2, md:4}}}>
        {children}
      </Box>
      <Footer />
    </Box>
  );
};

export default Layout;