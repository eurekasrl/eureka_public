import React, { useState } from 'react';
import { 
  Box, Typography, Button, Chip, 
  Table, TableBody, TableCell, TableHead, TableRow,
  IconButton, Tooltip, Collapse
} from '@mui/material';
import { 
  CheckCircle, Warning, CloudUpload, Visibility, 
  ErrorOutline, FilePresent, Delete as DeleteIcon, 
  KeyboardArrowDown, KeyboardArrowUp, FolderOpen, InsertDriveFile
} from '@mui/icons-material';
import { getViewDocumentURL } from '../../../api'; 

const DocumentRow = ({ rowGroup, onDelete, onOpenUpload }) => {
    const [open, setOpen] = useState(false);
    const { documento, archives } = rowGroup;
    
    // Check if this document type is "Linkable" (Transactional)
    // 0 or false means it is transactional
    const isLinkable = documento.entity === false || documento.entity === 0;

    // --- STATUS CHIP HELPER ---
    const getStatusChip = (status, count, isLinkableGroup) => {
        if (isLinkableGroup) {
            if (count > 0) {
                return <Chip icon={<FolderOpen />} label={`${count} File Caricati`} color="primary" variant="outlined" size="small" />;
            } else {
                return <Chip icon={<Warning />} label="Mancante" color="error" variant="outlined" size="small" />;
            }
        }

        // Standard Entity Level Status
        switch (status) {
            case 'UPLOADED': return <Chip icon={<CheckCircle />} label="Archiviato" color="success" size="small" variant="outlined" />;
            case 'PENDING_APPROVAL': return <Chip icon={<FilePresent />} label="Da Verificare" color="info" size="small" variant="outlined" />;
            case 'MISSING': return <Chip icon={<Warning />} label="Mancante" color="error" size="small" variant="outlined" />;
            case 'FILE_NOT_FOUND': return <Chip icon={<ErrorOutline />} label="File Perso" color="warning" size="small" variant="outlined" />;
            default: return <Chip label={status || "N/D"} size="small" />;
        }
    };

    // Determine status for the Parent Row
    // If it's a single entity doc, use the first archive's status or MISSING
    const singleDocStatus = archives.length > 0 ? archives[0].stato : 'MISSING';

    return (
        <>
            {/* =========================================
                PARENT ROW (Main Definition)
               ========================================= */}
            <TableRow sx={{ '& > *': { borderBottom: 'unset' }, backgroundColor: open ? '#f9f9f9' : 'inherit' }}>
                <TableCell>
                    <Box display="flex" alignItems="center">
                        {/* Expand Button ONLY for Linkable docs */}
                        {isLinkable && (
                            <IconButton
                                aria-label="expand row"
                                size="small"
                                onClick={() => setOpen(!open)}
                                sx={{ mr: 1 }}
                            >
                                {open ? <KeyboardArrowUp /> : <KeyboardArrowDown />}
                            </IconButton>
                        )}
                        
                        <Box>
                            <Typography variant="subtitle2" fontWeight="bold">
                                {documento.nome}
                            </Typography>
                            <Box display="flex" gap={1} alignItems="center">
                                <Typography variant="caption" color="text.secondary">
                                    {documento.sigla}
                                </Typography>
                                {documento.personale && <Chip label="Personale" size="small" color="secondary" sx={{ height: 16, fontSize: '0.6rem' }} />}
                                {isLinkable && <Chip label="Multiplo" size="small" color="default" sx={{ height: 16, fontSize: '0.6rem' }} />}
                            </Box>
                        </Box>
                    </Box>
                </TableCell>

                {/* Dati Archivio Summary */}
                <TableCell>
                    {!isLinkable && archives.length > 0 && (
                         <Box display="flex" flexDirection="column">
                            <Typography variant="caption">Anno: <b>{archives[0].anno}</b></Typography>
                            {documento.signed && (
                                <Typography variant="caption" color={archives[0].signed ? "success.main" : "error.main"}>
                                    Firma: {archives[0].signed ? "SI" : "NO"}
                                </Typography>
                            )}
                         </Box>
                    )}
                    {isLinkable && archives.length > 0 && (
                        <Typography variant="caption" color="text.secondary">
                            Ultimo agg: {new Date(archives[0].last_update || Date.now()).toLocaleDateString()}
                        </Typography>
                    )}
                </TableCell>

                {/* Status */}
                <TableCell align="center">
                    {getStatusChip(singleDocStatus, archives.length, isLinkable)}
                </TableCell>

                {/* Actions */}
                <TableCell align="right">
                    <Box display="flex" justifyContent="flex-end" gap={1}>
                        <Button 
                            variant="contained" 
                            size="small" 
                            startIcon={<CloudUpload />}
                            onClick={() => onOpenUpload(documento)}
                        >
                            {archives.length > 0 ? "Aggiungi" : "Upload"}
                        </Button>
                        
                        {/* Delete All Button (Parent Level) */}
                        {archives.length > 0 && (
                            <Tooltip title={isLinkable ? "Elimina TUTTI i file" : "Elimina documento"}>
                                <IconButton 
                                    size="small" 
                                    color="error" 
                                    onClick={() => onDelete(documento.id, null)} // null = Delete Group
                                >
                                    <DeleteIcon />
                                </IconButton>
                            </Tooltip>
                        )}
                        
                        {/* FIX: View Button for Entity Level (Non-Linkable) */}
                        {!isLinkable && archives.length > 0 && (
                             <Tooltip title="Visualizza">
                                <IconButton 
                                    size="small" 
                                    color="primary" 
                                    // FIX: Use archives[0] directly since we are in parent scope, not mapping
                                    onClick={() => window.open(getViewDocumentURL(archives[0].archive_id), '_blank')}
                                >
                                    <Visibility />
                                </IconButton>
                             </Tooltip>
                        )}
                    </Box>
                </TableCell>
            </TableRow>

            {/* =========================================
                CHILD ROW (Collapsible Details)
               ========================================= */}
            {isLinkable && (
                <TableRow>
                    <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={4}>
                        <Collapse in={open} timeout="auto" unmountOnExit>
                            <Box sx={{ margin: 2, padding: 2, backgroundColor: '#fff', borderRadius: 1, border: '1px solid #eee' }}>
                                <Typography variant="subtitle2" color="primary" gutterBottom component="div">
                                    Files Archiviati ({archives.length})
                                </Typography>
                                <Table size="small" aria-label="purchases">
                                    <TableHead>
                                        <TableRow>
                                            <TableCell><Typography variant="caption" fontWeight="bold">File</Typography></TableCell>
                                            <TableCell><Typography variant="caption" fontWeight="bold">Dettagli</Typography></TableCell>
                                            <TableCell align="right"><Typography variant="caption" fontWeight="bold">Azioni</Typography></TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {archives.map((archRow) => (
                                            <TableRow key={archRow.archive_id || archRow.file_path}>
                                                {/* File Info */}
                                                <TableCell component="th" scope="row">
                                                    <Box display="flex" alignItems="center" gap={1}>
                                                        <InsertDriveFile fontSize="small" color="action" />
                                                        <Box>
                                                            <Typography variant="body2" sx={{wordBreak: 'break-all'}}>
                                                                {archRow.file_path ? archRow.file_path.split('/').pop() : 'File Sconosciuto'}
                                                            </Typography>
                                                            <Typography variant="caption" color="text.secondary">
                                                                {new Date(archRow.last_update).toLocaleDateString()}
                                                            </Typography>
                                                        </Box>
                                                    </Box>
                                                </TableCell>

                                                {/* Meta Data */}
                                                <TableCell>
                                                    <Box display="flex" gap={2}>
                                                        <Typography variant="caption">Anno: <b>{archRow.anno}</b></Typography>
                                                        <Typography variant="caption" color={archRow.signed ? "success.main" : "text.secondary"}>
                                                            {archRow.signed ? "Firmato" : "Non Firmato"}
                                                        </Typography>
                                                        <Typography variant="caption" color={archRow.sent ? "primary.main" : "text.secondary"}>
                                                            {archRow.sent ? "Inviato" : "Non Inviato"}
                                                        </Typography>
                                                    </Box>
                                                </TableCell>

                                                {/* Child Actions */}
                                                <TableCell align="right">
                                                     <Box display="flex" justifyContent="flex-end">
                                                        <Tooltip title="Visualizza File">
                                                            <IconButton 
                                                                size="small" 
                                                                color="primary"
                                                                onClick={() => window.open(getViewDocumentURL(archRow.archive_id), '_blank')}
                                                            >
                                                                <Visibility fontSize="small" />
                                                            </IconButton>
                                                        </Tooltip>
                                                        <Tooltip title="Elimina questo file">
                                                            <IconButton 
                                                                size="small" 
                                                                color="error" 
                                                                onClick={() => onDelete(documento.id, archRow.archive_id)}
                                                            >
                                                                <DeleteIcon fontSize="small" />
                                                            </IconButton>
                                                        </Tooltip>
                                                     </Box>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                        {archives.length === 0 && (
                                            <TableRow>
                                                <TableCell colSpan={3} align="center">
                                                    <Typography variant="caption" color="text.secondary">Nessun file presente.</Typography>
                                                </TableCell>
                                            </TableRow>
                                        )}
                                    </TableBody>
                                </Table>
                            </Box>
                        </Collapse>
                    </TableCell>
                </TableRow>
            )}
        </>
    );
};

export default DocumentRow;