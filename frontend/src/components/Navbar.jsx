import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
            Eureka
          </Link>
        </Typography>
        <Box>
          {/* Changed "Aziende" to point to the new table listing page */}
          <Button color="inherit" component={Link} to="/admin/tables">Gestisci DB</Button>
          <Button color="inherit" component={Link} to="/preventivi">Preventivi</Button>
          <Button color="inherit" component={Link} to="/piani-utilizzo">Piani Utilizzo</Button>
          {/* Aggiungi altri link qui */}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;