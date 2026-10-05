import React, { useEffect, useState, useMemo } from 'react';
import { Typography, Box, Button, CircularProgress } from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import { useSnackbar } from '../../context/SnackbarProvider';
// Updated imports: Removed getAllIntermediari/Compagnie, added getRelazioneRci
import { getAllRami, getRelazioneRci } from '../../api'; 
import SelectionGrid from '../../components/SelectionGrid';

const NewPreventivoPage = () => {
    const enqueue = useSnackbar();

    // Master Lists
    const [rami, setRami] = useState([]);
    const [relations, setRelations] = useState([]); // Stores the RelazioneRci triplets

    // UI States
    const [loadingRami, setLoadingRami] = useState(true);
    const [loadingRelations, setLoadingRelations] = useState(false);
    const [error, setError] = useState(null);

    // Selections
    const [selectedRamoId, setSelectedRamoId] = useState(null);
    const [selectedIntermediarioId, setSelectedIntermediarioId] = useState(null);
    const [selectedCompagniaId, setSelectedCompagniaId] = useState(null);
    
    const location = useLocation();
    const navigate = useNavigate();

    // Extract Persona ID from URL
    const ragioneSocialeId = location.pathname.split('/')[2];

    // 1. Initial Load: Fetch only Rami
    useEffect(() => {
        const fetchRami = async () => {
            try {
                const ramiData = await getAllRami();
                setRami(ramiData);
            } catch (err) {
                setError("Errore nel caricamento dei Rami: " + err.message);
                console.error(err);
            } finally {
                setLoadingRami(false);
            }
        };

        fetchRami();
    }, []);

    // 2. Handle Ramo Selection -> Fetch Relations
    const handleRamoSelect = async (ramoId) => {
        // Update selection
        setSelectedRamoId(ramoId);
        
        // Reset downstream selections
        setSelectedIntermediarioId(null);
        setSelectedCompagniaId(null);
        setRelations([]);

        if (!ramoId) return;

        setLoadingRelations(true);
        try {
            const data = await getRelazioneRci(ramoId);
            setRelations(data);
        } catch (err) {
            console.error("Error fetching relations", err);
            setError("Impossibile recuperare le configurazioni per questo Ramo.");
        } finally {
            setLoadingRelations(false);
        }
    };

    // 3. Handle Intermediario Selection
    const handleIntermediarioSelect = (intermediarioId) => {
        setSelectedIntermediarioId(intermediarioId);
        // Reset downstream selection
        setSelectedCompagniaId(null);
    };

    // 4. Derive Available Intermediari (Distinct list from Relations)
    const availableIntermediari = useMemo(() => {
        if (!relations.length) return [];
        
        const unique = [];
        const map = new Map();
        
        for (const item of relations) {
            // Check if active and intermediario exists
            if (item.active && item.intermediario && !map.has(item.intermediario.id)) {
                map.set(item.intermediario.id, true);
                unique.push(item.intermediario);
            }
        }
        return unique;
    }, [relations]);

    // 5. Derive Available Compagnie (Filtered by Selected Int, Distinct)
    const availableCompagnie = useMemo(() => {
        if (!selectedIntermediarioId || !relations.length) return [];

        const unique = [];
        const map = new Map();

        // Filter relations by the selected Intermediario first
        const filteredRelations = relations.filter(
            r => r.intermediario && r.intermediario.id === selectedIntermediarioId
        );

        for (const item of filteredRelations) {
            if (item.active && item.compagnia && !map.has(item.compagnia.id)) {
                map.set(item.compagnia.id, true);
                unique.push(item.compagnia);
            }
        }
        return unique;
    }, [relations, selectedIntermediarioId]);

    const handleProceed = () => {
        if (!selectedRamoId || !selectedIntermediarioId || !selectedCompagniaId) {
            enqueue("Per favore, seleziona un'opzione per ogni categoria.", 'warning');
            return;
        }

        const selectedRamoObj = rami.find(r => r.id === selectedRamoId);

        const draftData = {
            ragione_sociale_id: ragioneSocialeId,
            ramo_id: selectedRamoId,
            ramo_nome: selectedRamoObj ? selectedRamoObj.dettaglio : '',
            intermediario_id: selectedIntermediarioId,
            compagnia_id: selectedCompagniaId,
        };

        navigate(`/preventivi/${ragioneSocialeId}/compose`, { state: { draftData } });
    };

    // ---------------- RENDER ---------------- //

    if (loadingRami) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
                <CircularProgress />
                <Typography sx={{ ml: 2 }}>Caricamento Rami...</Typography>
            </Box>
        );
    }

    if (error) {
        return <Typography color="error" sx={{ my: 4, textAlign: 'center' }}>{error}</Typography>;
    }

    return (
        <Box sx={{ my: 4, textAlign: 'center' }}>
            {/* 1. Select Ramo */}
            <SelectionGrid
                data={rami}
                selectedId={selectedRamoId}
                onSelect={handleRamoSelect}
                title="Scegli un Ramo"
                renderItemContent={(ramo) => (
                    <Typography variant="h6" sx={{ mt: 1 }}>
                        {ramo.dettaglio}
                    </Typography>
                )}
            />

            {/* Loading Indicator for Relations */}
            {loadingRelations && (
                <Box sx={{ my: 4 }}>
                    <CircularProgress size={30} />
                </Box>
            )}

            {/* 2. Select Intermediario (Only visible if Ramo selected) */}
            {!loadingRelations && selectedRamoId && (
                <Box sx={{ mt: 4, opacity: availableIntermediari.length ? 1 : 0.5 }}>
                    {availableIntermediari.length === 0 ? (
                        <Typography color="text.secondary">Nessun intermediario disponibile per questo ramo.</Typography>
                    ) : (
                        <SelectionGrid
                            data={availableIntermediari}
                            selectedId={selectedIntermediarioId}
                            onSelect={handleIntermediarioSelect}
                            title="Scegli un Intermediario"
                            renderItemContent={(intermediario) => (
                                <>
                                    <Typography variant="h6" sx={{ mt: 1 }}>
                                        {intermediario.short_nome}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {intermediario.full_nome}
                                    </Typography>
                                </>
                            )}
                        />
                    )}
                </Box>
            )}

            {/* 3. Select Compagnia (Only visible if Intermediario selected) */}
            {selectedIntermediarioId && (
                <Box sx={{ mt: 4 }}>
                     {availableCompagnie.length === 0 ? (
                        <Typography color="text.secondary">Nessuna compagnia disponibile per questa selezione.</Typography>
                    ) : (
                        <SelectionGrid
                            data={availableCompagnie}
                            selectedId={selectedCompagniaId}
                            onSelect={setSelectedCompagniaId}
                            title="Scegli una Compagnia"
                            renderItemContent={(compagnia) => (
                                <>
                                    <Typography variant="h6" sx={{ mt: 1 }}>
                                        {compagnia.short_nome}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {compagnia.full_nome}
                                    </Typography>
                                </>
                            )}
                        />
                    )}
                </Box>
            )}

            {/* Proceed Button */}
            {selectedCompagniaId && (
                <Box sx={{ mt: 6, mb: 4 }}>
                    <Button
                        variant="contained"
                        color="primary"
                        size="large"
                        onClick={handleProceed}
                    >
                        Prosegui
                    </Button>
                </Box>
            )}
        </Box>
    );
};

export default NewPreventivoPage;