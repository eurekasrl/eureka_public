import React, { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import GrandinePage from "./Rami/Grandine/GrandinePage";

const RamoDispatcher = () => {
    const [ramoName, setRamoName] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    
    const location = useLocation();
    const { preventivo_id } = useParams();

    // Context data (either from State or eventually needed by children)
    const [contextData, setContextData] = useState(null);

    useEffect(() => {
        const determineContext = async () => {
            setIsLoading(true);
            setError(null);

            // SCENARIO 1: Creating New (Data comes from previous page state)
            if (!preventivo_id && location.state?.draftData) {
                const { draftData } = location.state;
                setRamoName(draftData.ramo_nome);
                setContextData(draftData);
                setIsLoading(false);
                return;
            }

            // SCENARIO 2: Editing (Fetch from DB)
            if (preventivo_id && location.state?.ramoNome) {
                try { 
                    setRamoName(location.state.ramoNome);
                    setIsLoading(false)
                    return
                } catch (err) {
                    console.error("Error fetching ramo:", err);
                    setError("Failed to load ramo. Please try again.");
                } finally {
                    setIsLoading(false);
                }
                return;
            }

            // SCENARIO 3: Error (Direct access without state or ID)
            setError("Informazioni insufficienti per caricare il preventivo.");
            setIsLoading(false);
        };

        determineContext();
    }, [preventivo_id, location.state]);

    if (isLoading) return <div>Loading ramo...</div>;
    if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;
    if (!ramoName) return <div>No ramo found.</div>;

    // Normalize Ramo name
    const normalizedRamo = ramoName.trim().toLowerCase();

    // Props to pass to child components
    // If creating: pass 'initialData' (ids). If editing: pass 'preventivoId'.
    const childProps = preventivo_id 
        ? { preventivoId: preventivo_id, mode: 'edit' } 
        : { initialData: contextData, mode: 'create' };

    switch (normalizedRamo) {
        case "grandine":
            return <GrandinePage {...childProps} />;
        default:
            return <div>Unknown Ramo: {ramoName}</div>;
    }
};

export default RamoDispatcher;