import React, { useEffect, useState, useMemo } from 'react';

import {
    Grid, Avatar, Divider, Card, CardContent, CardHeader,
} from '@mui/material';

import InfoRow from '../InfoRow';


const AnagraficaCompany = ({ data }) => {
  const legalRep = data.responsabile_legale || {};
  const caa = data.caa_coldiretti || {};
  const referente = data.gruppo?.referente || {};

  return (
    <Grid container spacing={3}>
        <Card sx={{ mb: 3 }}>
          <CardHeader title="Dettagli Aziendali" />
          <Divider />
          <CardContent>
            <InfoRow label="CUAA" value={data.CUAA} />
            <InfoRow label="IBAN" value={data.IBAN} copyable />
            <InfoRow label="PEC" value={data.pec} />
            <InfoRow label="CAA" value={caa.nome || 'N/A'} />
          </CardContent>
        </Card>
        {data.gruppo && (
          <Card>
            <CardHeader title="Gruppo di Appartenenza" />
            <Divider />
            <CardContent>
              <InfoRow label="Gruppo" value={data.gruppo?.nome} />
              <InfoRow label="Referente" value={referente.nome} />
              <InfoRow label="Email" value={referente.email} />
            </CardContent>
          </Card>
        )}
      <Grid item xs={12} md={6}>
        <Card>
          <CardHeader title="Responsabile Legale" avatar={<Avatar>{legalRep.nome?.charAt(0)}</Avatar>} />
          <Divider />
          <CardContent>
            <InfoRow label="Nome" value={`${legalRep.nome || ''} ${legalRep.cognome || ''}`} />
            <InfoRow label="CF" value={legalRep.cf} />
            <InfoRow label="Indirizzo" value={legalRep.indirizzo} />
            <InfoRow label="Email" value={legalRep.email} copyable />
            <InfoRow label="Cell" value={legalRep.cell} />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};
export default AnagraficaCompany