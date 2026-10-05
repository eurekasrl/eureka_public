import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography } from '@mui/material';
import { Link } from 'react-router-dom';

const DataTable = ({ data, columns, title, detailPath }) => {
  if (!data || data.length === 0) {
    return (
      <Paper sx={{ p: 2, mt: 3 }}>
        <Typography variant="h6" component="h2">{title}</Typography>
        <Typography variant="body1" sx={{ mt: 2 }}>Nessun dato disponibile.</Typography>
      </Paper>
    );
  }

  return (
    <TableContainer component={Paper} sx={{ mt: 3 }}>
      <Typography variant="h6" component="h2" sx={{ p: 2 }}>{title}</Typography>
      <Table sx={{ minWidth: 650 }} aria-label={`${title} table`}>
        <TableHead>
          <TableRow>
            {columns.map((column) => (
              <TableCell key={column.field}>{column.headerName}</TableCell>
            ))}
            {detailPath && <TableCell>Azioni</TableCell>}
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((row) => (
            <TableRow key={row.id}>
              {columns.map((column) => (
                <TableCell key={`${row.id}-${column.field}`}>
                  {column.valueGetter ? column.valueGetter(row) : row[column.field]}
                </TableCell>
              ))}
              {detailPath && (
                <TableCell>
                  <Link to={`${detailPath}/${row.id}`}>Dettagli</Link>
                </TableCell>
              )}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default DataTable;