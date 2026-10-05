import React, { useMemo } from 'react';
import PreventiviTable from '../../Preventivi/PreventiviTable'; // Adjust path

const PreventiviTab = ({ 
    preventiviData, 
    loading, 
    contextType, 
    data, // Entity data (for naming if needed)
    onEmail, 
    onDownload, 
    onIntermediario 
}) => {

    // Logic moved from Main Page
    const aggregatedRows = useMemo(() => {
        const groupingMap = {};
        let allLists = [];
        
        if (Array.isArray(preventiviData)) allLists = [preventiviData]; 
        else allLists = Object.values(preventiviData); 
    
        allLists.forEach(list => {
          if (!Array.isArray(list)) return;
          list.forEach(prev => {
            const key = `${prev.ramo_id}-${prev.anno}`;
            if (!groupingMap[key]) {
              const rName = prev.ramo_dettaglio || prev.ramo_nome || (prev.ramo ? prev.ramo.nome : `Ramo ${prev.ramo_id}`);
              groupingMap[key] = { ramo_id: prev.ramo_id, ramo_nome: rName, anno: prev.anno, stato: {} };
            }
            
            // Handle aggregated objects vs string statuses
            if (prev.stato && typeof prev.stato === 'object') {
               Object.entries(prev.stato).forEach(([statusName, count]) => {
                  groupingMap[key].stato[statusName] = (groupingMap[key].stato[statusName] || 0) + count;
               });
            } else {
               const sStr = typeof prev.stato === 'string' ? prev.stato : 'Sconosciuto';
               groupingMap[key].stato[sStr] = (groupingMap[key].stato[sStr] || 0) + 1;
            }
          });
        });
        return Object.values(groupingMap);
    }, [preventiviData]);

    return (
        <PreventiviTable 
            rows={aggregatedRows} 
            loading={loading} 
            onEmail={onEmail} 
            onDownload={onDownload} 
            onIntermediario={onIntermediario}
        />
    );
};

export default PreventiviTab;