import React, { useState, useMemo } from 'react';
import { 
  Box, Typography, Button, Paper, Chip, 
  Card, CardContent, CardHeader, Divider,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  IconButton, Tooltip, CircularProgress, Alert, Collapse
} from '@mui/material';
import { 
  Business, Description, CheckCircle, Warning, 
  CloudUpload, Visibility, ErrorOutline, FilePresent,
  Refresh, Delete as DeleteIcon, KeyboardArrowDown, KeyboardArrowUp,
  FolderOpen, InsertDriveFile
} from '@mui/icons-material';
import DocumentRow from './DocumentRow';

// ==========================================
// HELPER: Grouping Logic
// ==========================================
const groupDocuments = (docsData) => {
    const groups = {};

    if (!docsData) return [];

    docsData.forEach(row => {
        // Handle potential missing document object
        if (!row.documento) return;
        
        const docId = row.documento.id;
        
        if (!groups[docId]) {
            groups[docId] = {
                documento: row.documento,
                archives: [],
                statusSummary: 'MISSING' 
            };
        }

        // If row has a valid file (not just a placeholder for missing)
        if (row.stato === 'UPLOADED' || row.stato === 'PENDING_APPROVAL') {
            groups[docId].archives.push(row);
            groups[docId].statusSummary = 'HAS_FILES';
        } 
    });

    return Object.values(groups);
};


// ==========================================
// COMPONENT: DocumentsTab (Main)
// ==========================================
const DocumentsTab = ({ 
    contextType, entityId, docsData, loading, diagnostic, 
    onRefresh, onOpenUpload, onDelete 
}) => {

    // Group the flat list from API
    const groupedDocs = useMemo(() => groupDocuments(docsData), [docsData]);
    if (contextType === 'gruppo') {
        return (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Business sx={{ fontSize: 50, color: 'text.disabled', mb: 2 }} />
                <Alert severity="info">La gestione documenti è disponibile solo all'interno di una specifica Ragione Sociale.</Alert>
            </Paper>
        );
    }

    return (
        <Card elevation={2}>
            <CardHeader 
                title={<Box display="flex" alignItems="center" gap={1}><Description color="primary" /><Typography variant="h6">Gestione Documentale</Typography></Box>}
                action={<Tooltip title="Aggiorna Lista"><IconButton onClick={onRefresh} disabled={loading}><Refresh /></IconButton></Tooltip>}
            />
            <Divider />
            <CardContent>
                {diagnostic && !diagnostic.exists && (
                    <Alert severity="error" variant="outlined" sx={{ mb: 2 }}>Problema Cartelle: {diagnostic.error_code}</Alert>
                )}

                <TableContainer component={Paper} variant="outlined">
                    <Table>
                        <TableHead sx={{ backgroundColor: '#f9fafb' }}>
                            <TableRow>
                                <TableCell>Documento</TableCell>
                                <TableCell>Dati Archivio</TableCell>
                                <TableCell align="center">Stato</TableCell>
                                <TableCell align="right">Azioni</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {loading ? (
                                <TableRow><TableCell colSpan={4} align="center" sx={{ py: 4 }}><CircularProgress /></TableCell></TableRow>
                            ) : groupedDocs.length === 0 ? (
                                <TableRow><TableCell colSpan={4} align="center">Nessun documento richiesto.</TableCell></TableRow>
                            ) : (
                                groupedDocs.map((group) => (
                                    <DocumentRow 
                                        key={group.documento.id}
                                        rowGroup={group}
                                        onDelete={onDelete}
                                        onOpenUpload={onOpenUpload}
                                    />
                                ))
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            </CardContent>
        </Card>
    );
};

export default DocumentsTab;