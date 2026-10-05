import React, { useEffect, useState } from 'react';
import { Box, Typography, CircularProgress, Alert, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TextField, InputAdornment } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { Link } from 'react-router-dom';
import { getAllragioniSociali } from '../api';

const ClientiTable = ({ title, linkPrefix }) => {
    const [tables, setTables] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchTables = async () => {
            try {
                const data = await getAllragioniSociali();
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
            [table.gruppo?.nome, table.nome, table.responsabile_legale?.nome]
                .some((nome) => nome?.toLowerCase().includes(searchTerm.toLowerCase()))
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
                {title}
            </Typography>

            <TextField
                fullWidth
                variant="outlined"
                placeholder="Cerca per gruppo o ragione sociale o responsabile legale..."
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
                            <TableCell>Gruppo</TableCell>
                            <TableCell>Ragione Sociale</TableCell>
                            <TableCell>Responsabile Legale</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {filteredTables.length > 0 ? (
                            filteredTables.map((table) => (
                                <TableRow key={`${table.id}`}>
                                    <TableCell>
                                        {table.gruppo ? (
                                            <Link to={`${linkPrefix}/gruppi/${table.gruppo.id}`} style={{ textDecoration: 'none', color: 'inherit', fontWeight: 'bold' }}>
                                                {table.gruppo.nome}
                                            </Link>
                                        ) : '—'}
                                    </TableCell>
                                    <TableCell>
                                        <Link to={`${linkPrefix}/ragioni-sociali/${table.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                                            {table.nome}
                                        </Link>
                                    </TableCell>
                                    <TableCell>
                                        <Link to={`${linkPrefix}/ragioni-sociali/${table.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                                            {table.responsabile_legale?.nome}
                                        </Link>
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

export default ClientiTable;