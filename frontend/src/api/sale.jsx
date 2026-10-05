import api from "./base";

export const createPreventivo = async (payload) => {
    try {
      const response = await api.post('/preventivi/', payload);
      return response.data;
    } catch (error) {
      console.error('Error creating preventivo:', error.response ? error.response.data : error.message);
      throw error;
    }
};

export const editEsitoPreventivo = async (preventivoId, esito) => {
    try {
      const response = await api.patch(`/preventivi/${esito}/${preventivoId}`);
      return response.data;
    } catch (error) {
      console.error('Error creating preventivo:', error.response ? error.response.data : error.message);
      throw error;
    }
};

export const deletePreventivo = async (preventivoId, ramoNome) => {
  try {
    const response = await api.delete(`/preventivi/delete/${preventivoId}`, {params: {ramo_nome: ramoNome}})
    return response.data
  } catch (error) {
    console.error( 'Error creating preventivo:', error.response ? error.response.data : error.message)
    throw error
  }
}

export const getPreventiviByRagioneSociale = async (ragioneSocialeId, page, ramoId, anno) => {
  try {
    const hasPage = Boolean(page);

    const url = hasPage
      ? `/preventivi/page/ragioni-sociali/${ragioneSocialeId}`
      : `/preventivi/ragioni-sociali/${ragioneSocialeId}`;
    
    const params = {}
    if (hasPage) {
      params.page = page
    } 
    if (ramoId) {
      params.ramo_id = ramoId
    }
    if (anno) {
      params.anno = anno
    }
      
    const response = await api.get(url, {params});
    return response.data;

  } catch (error) {
    console.error(`Error fetching preventivo for ${ragioneSocialeId}:`, error);
    return null;
  }
};

export const getPreventiviByGruppo = async (gruppoId, page, ramoId, anno) => {
  try {
    const hasPage = Boolean(page);

    const url = hasPage
      ? `/preventivi/page/gruppi/${gruppoId}`
      : `/preventivi/gruppi/${gruppoId}`;
    
    const params = {}
    if (hasPage) {
      params.page = page
    } 
    if (ramoId) {
      params.ramo_id = ramoId
    }
    if (anno) {
      params.anno = anno
    }
      
    const response = await api.get(url, {params});
    return response.data;

  } catch (error) {
    console.error(`Error fetching preventivo for ${gruppoId}:`, error);
    return null;
  }
};

export const getRamoByPreventivoId = async (action, preventivoId, q = '') => {
  try {
    const response = await api.get(`/preventivi/${action}/${preventivoId}/`, {params: { q }}
    )
    return response.data
  } catch (error) {
    console.error(`Error fetching preventivo for ${preventivoId}:`, error)
    return null
  }
}

export const getPreventivoById = async (id) => {
  try {
    const response = await api.get(`/preventivi/get/${id}/`)
    return response.data
  } catch (error) {
    console.error(`Error fetching preventivo for ${id}:`, error)
    return null
  }
}

export const downloadPreventiviCSV = async (clientLevelId, clientLevel, ramoId, anno, selectedIds=[]) => {
  const params = {
    client_level_id: clientLevelId,
    client_level: clientLevel,
    ramo_id: ramoId,
    anno: anno
  };
  
  if (selectedIds && selectedIds.length > 0) {
    params.ids = selectedIds.join(',');
  }

  const response = await api.get('preventivi/download/csv', {
    params,
    responseType: 'blob'
  })

  return response
};

export const getPreventiviDetails = async (pgId, ramoId, anno) => {
  // Adjust URL based on your routing
  const response = await api.get(`/preventivi/details/list`, {
    params: { ragione_sociale_id: pgId, ramo_id: ramoId, anno }
  });
  return response.data;
};

export const sendPreventiviEmail = async (payload, destinatario) => {
  return await api.post(`preventivi/send-email/${destinatario}`, payload)
}

export const getRagioneSocialeDocuments = async (ragioneSocialeId) => {
  const response = await api.get(`/documenti/ragioni-sociali/${ragioneSocialeId}`)
  return response.data
}

export const uploadRagioneSocialeDocument = async (ragioneSocialeId, documentoId, file, anno, signed, sent, linkedIds) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("anno", anno);
    formData.append("signed", signed); // Note: ensure backend parses string "true"/"false" or bool
    formData.append("sent", sent);

    if (linkedIds) {
      formData.append("linked_ids", linkedIds)
    }

    try {
        const response = await api.post(
            `/documenti/ragioni-sociali/${ragioneSocialeId}/documento/${documentoId}`, 
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            }
        );
        return response.data;
    } catch (error) {
        console.error("Upload error:", error);
        throw error;
    }
}

export const deleteRagioneSocialeDocument = async (ragioneSocialeId, documentoId) => {
    const response = await api.delete(`/documenti/ragioni-sociali/${ragioneSocialeId}/documento/${documentoId}`);
    return response.data;
}

export const deleteArchiveById = async (archiveId) => {
  const response = await api.delete(`/documenti/archivio/${archiveId}`)
  return response.data
}

export const getViewDocumentURL = (archiveId) => {
    // 1. Get your base API URL (e.g., from Vite env vars)
    // Adjust 'http://localhost:8000/api/v1' to match your actual backend address
    const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    
    // 2. Return the string. 
    // Note: Use '/download' to match the backend router we wrote in the previous step.
    return `${baseURL}/documenti/view/${archiveId}`
  }