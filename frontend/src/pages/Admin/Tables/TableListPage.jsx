import React, { useEffect, useState } from 'react';
import { Box, Typography, CircularProgress, Alert, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TextField, InputAdornment } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { Link } from 'react-router-dom';
import { getAllTables } from '../../../api';

const TableListPage = () => {
  const [tables, setTables] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchTables = async () => {
      try {
        const data = await getAllTables();
        setTables(data);
      } catch (err) {
        setError("Errore nel caricamento delle tabelle del database.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTables();
  }, []);

  const filteredTables = tables.filter(
    (table) =>
      table.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      table.schema.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Gestione Tabelle Database
      </Typography>

      <TextField
        fullWidth
        variant="outlined"
        placeholder="Cerca per nome tabella o schema..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        }}
        sx={{ mb: 3 }}
      />

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Schema</TableCell>
              <TableCell>Nome Tabella</TableCell>
              <TableCell>Azioni</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredTables.length > 0 ? (
              filteredTables.map((table) => (
                <TableRow key={`${table.schema}.${table.name}`}>
                  <TableCell>{table.schema}</TableCell>
                  <TableCell>{table.name}</TableCell>
                  <TableCell>
                    <Link to={`/admin/tables/${table.schema}/${table.name}`}>Visualizza Dati</Link>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={3} align="center">
                  Nessuna tabella trovata con il termine di ricerca.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default TableListPage;