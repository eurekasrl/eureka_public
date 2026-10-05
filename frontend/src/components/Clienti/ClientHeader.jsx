import React, { useEffect, useState, useMemo } from 'react';

import { 
  Box, Typography, Button, Grid, Paper, Avatar, Chip, 
} from '@mui/material';
import { 
  GroupWork, LocationOn, Email, ArrowBack
} from '@mui/icons-material';
import { Link } from 'react-router-dom';

const ClientHeader = ({ data, type }) => {
  const isGroup = type === 'gruppo';
  const getMapUrl = (addr, city) => 
    addr ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${addr}, ${city||''}`)}` : '#';

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3, borderRadius: 2 }}>
      <Grid container spacing={2} alignItems="center">
        <Grid item>
          <Avatar sx={{ width: 80, height: 80, bgcolor: isGroup ? 'secondary.main' : 'primary.main', fontSize: '2rem' }}>
            {isGroup ? <GroupWork fontSize="large" /> : (data.nome?.charAt(0) || 'A')}
          </Avatar>
        </Grid>
        <Grid item xs>
          <Typography variant="h4" fontWeight="bold">{data.nome}</Typography>
          <Typography variant="body1" color="textSecondary" gutterBottom>
            {isGroup ? 'Gruppo Aziendale' : `P.IVA: ${data.piva}`}
          </Typography>
          
          {!isGroup && (
            <Box display="flex" gap={1} flexWrap="wrap" mt={1}>
              <Chip icon={<LocationOn />} label={data.indirizzo} component="a" href={getMapUrl(data.indirizzo, data.comune?.nome)} clickable variant="outlined" />
              <Chip icon={<Email />} label={data.email} component="a" href={`mailto:${data.email}`} clickable variant="outlined" />
            </Box>
          )}
        </Grid>
        <Grid item>
          <Button variant="outlined" startIcon={<ArrowBack />} component={Link} to={-1}>
            Indietro
          </Button>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default ClientHeader