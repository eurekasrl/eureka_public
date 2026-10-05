import React, { useEffect, useState, useMemo } from 'react';

import {
    Grid, Avatar, Divider, Card, CardContent, CardHeader,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
} from '@mui/material';

import InfoRow from '../InfoRow';



const AnagraficaGroup = ({ data }) => {
  const referente = data.referente || {};
  const aziende = data.ragione_sociale || [];

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card sx={{ mb: 3 }}>
          <CardHeader title="Referente Gruppo" avatar={<Avatar>{referente.nome?.charAt(0)}</Avatar>} />
          <Divider />
          <CardContent>
            <InfoRow label="Nome" value={`${referente.nome || ''} ${referente.cognome || ''}`} />
            <InfoRow label="CF" value={referente.cf} />
            <InfoRow label="Email" value={referente.email} copyable />
            <InfoRow label="Tel" value={referente.cell || referente.telefono} />
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={8}>
        <Card>
          <CardHeader title="Aziende Associate" subheader={`${aziende.length} entità`} />
          <Divider />
          <TableContainer sx={{ maxHeight: 600 }}>
            <Table stickyHeader size="small">
              <TableHead><TableRow><TableCell>Ragione Sociale</TableCell><TableCell>P.IVA</TableCell><TableCell>CUAA</TableCell></TableRow></TableHead>
              <TableBody>
                {aziende.map((az) => (
                  <TableRow key={az.id} hover>
                    <TableCell sx={{ fontWeight: 'bold' }}>{az.nome}</TableCell>
                    <TableCell>{az.piva}</TableCell>
                    <TableCell>{az.CUAA}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Card>
      </Grid>
    </Grid>
  );
};
export default AnagraficaGroup