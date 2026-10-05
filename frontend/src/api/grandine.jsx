import api from "./base";

{/* PIANO UTILIZZO*/}
export const getPianoUtilizzobyId = async (pianoUtilizzoId) =>  {
    try {
    if (!pianoUtilizzoId) return null; 
    const response = await api.get(`/piani-utilizzo/${pianoUtilizzoId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching prodotto ${pianoUtilizzoId}:`, error);
    return null;
  }
}

export const getPianiUtilizzoByPreventivoId = async (preventivoId) => {
  try {
    if (!preventivoId) return null
    const response = await api.get(`/piani-utilizzo/preventivo/${preventivoId}`)
    return response.data
  } catch (err) {
    console.error(`Error fetching piani utilizzo by preventivo ${preventivoId}:`, err)
    return null
  }
}

export const getPianiUtilizzoByRagioneSocialeId = async (ragioneSocialeId, anno) => {
  try {
    if (!ragioneSocialeId) return null
    const response = await api.get(`/piani-utilizzo/ragioni-sociali/${ragioneSocialeId}/riepilogativi`, { params: { anno } })
    return response.data
  } catch (err) {
    console.error(`Error fetching piani utilizzo riepilogativi for ${ragioneSocialeId}:`, err)
    return null
  }
}

export const getPianiUtilizzoDettagliatoByRagioneSocialeId = async (ragioneSocialeId, anno) => {
  try {
    if (!ragioneSocialeId) return null
    const response = await api.get(`/piani-utilizzo/ragioni-sociali/${ragioneSocialeId}/dettagliati`, { params: { anno } })
    return response.data
  } catch (err) {
    console.error(`Error fetching piani utilizzo dettagliati for ${ragioneSocialeId}:`, err)
    return null
  }
}

export const createPianoUtilizzoDettagliato = async(ragioneSocialeId, payload) => {
  try {
      const response = await api.post(`/piani-utilizzo/ragioni-sociali/${ragioneSocialeId}/dettagliati`, payload);
      return response.data;
    } catch (error) {
      console.error('Error creating piano utilizzo dettagliato:', error.response ? error.response.data : error.message);
      throw error;
    }
}

export const getPianoUtilizzoComparison = async(ragioneSocialeId) => {
  try {
      const response = await api.get(`/piani-utilizzo/ragioni-sociali/${ragioneSocialeId}/comparison`);
      return response.data;
    } catch (error) {
      console.error('Error creating piano utilizzo comparison:', error.response ? error.response.data : error.message);
      throw error;
    }
}

export const createPianoUtilizzoBulk = async (payload, is_dettagliato) => {
  const response = await api.post('piani-utilizzo/bulk', payload, { params: {is_dettagliato } })
  return response.data
}

export const uploadPianoPdf = async (formData) => {
  const response = await api.post('/piani-utilizzo/upload-pdf', formData, {headers: {'Content-Type': 'multipart/form-data'}})
  return response.data
}

export const deletePianoUtilizzo = async (id, is_dettagliato) => {
  const response = await api.delete(`/piani-utilizzo/${id}`, { 
    params: { is_dettagliato } 
  });
  return response.data;
};

export const applyPianoMapping = async (payload) => {
  const response = await api.post('/piani-utilizzo/apply-mapping', payload);
  return response.data;
};

{/* PRODOTTO*/}
export const getProdottiByCondifesa = async (condifesa_id, q = '') => {
  try {
    const response = await api.get(`/prodotti/condifesa/${condifesa_id}`, { params: { q } });
    return response.data;
  } catch (error) {
    console.error("Error fetching prodotti:", error);
    throw error;
  }
}

export const getProdottoByIdWithCondifesa = async (prodottoId, condifesaId) => {
  const response = await api.get(`/prodotti/${prodottoId}`,{
    params: { condifesa_id: condifesaId }
  })
  return response.data;
};

export const getProdottoById = async (prodottoId) => {
  try {
    if (!prodottoId) return null; 
    const response = await api.get(`/prodotti/${prodottoId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching prodotto ${prodottoId}:`, error);
    return null;
  }
};

{/* PREZZI*/}

export const getCurrentPrezziByProdottoId = async (prodottoId) => {
  try {
    if (!prodottoId) return null
    const response = await api.get(`/prezzi/prodotto/${prodottoId}`)
    return response.data
  } catch (err) {
    console.error(`Error fetching prezzi for prodotto ${prodottoId}:`, err)
    return null
  }
}

export const getPrezziByYearCondifesaProdottoId = async (anno, condifesa_id, prodotto_id) => {
  try {
    const response = await api.get(`/prezzi/list`, {params: { anno, condifesa_id, prodotto_id }})
    return response.data
  } catch (error) {
    console.error(`Error fetching prezzi in anno ${anno} condifesa_id ${condifesa_id} e prodotto${prodotto_id}:`, error)
    return null
  }
}

{/* TASSI*/}
export const getTassiByPianoUtilizzoPreventivo = async (piano_utilizzo_id, preventivo_id) => {
  try {
    const response = await api.get(`/tassi/list/preventivo`, {params: { piano_utilizzo_id, preventivo_id }} )
    return response.data
  } catch (error) {
    console.error(`Error fetching prezzi by piano_utilizzo ${piano_utilizzo_id} e preventivo_id${preventivo_id}:`, error)
  }
}

export const getTassiByPianoUtilizzoAndCompagniaIntermediario = async (piano_utilizzo_id, compagnia_id, intermediario_id) => {
  try {
    const response = await api.get(`/tassi/list/compagnia_intermediario`, {params: { piano_utilizzo_id, compagnia_id, intermediario_id }} )
    return response.data
  } catch (err) {
    console.error(`Error fetching tassi for piano_utilizzo ${piano_utilizzo_id} compagnia ${compagnia_id} intermediario ${intermediario_id}:`, err)
  }
}

{/* PREVENTIVO*/}
export const createPreventivoGrandine = async (payload) => {
    try {
      const response = await api.post('/preventivi-grandine/', payload);
      return response.data;
    } catch (error) {
      console.error('Error creating preventivo:', error.response ? error.response.data : error.message);
      throw error;
    }
};

export const getPreventivoGrandineBySalePreventivoId = async (salePreventivoId) => {
  try {
    if (!salePreventivoId) return null
    const response = await api.get(`/preventivi-grandine/${salePreventivoId}`)
    return response.data
  } catch (error) {
    console.error(`Error fetching prodotto ${salePreventivoId}:`, error)
    return null
  }
}

export const patchPreventivoGrandine = async (payload) => {
    try {
      const response = await api.patch('/preventivi-grandine/', payload);
      return response.data;
    } catch (error) {
      console.error('Error creating preventivo:', error.response ? error.response.data : error.message);
      throw error;
    }
};

{/* PARTITE*/}
export const checkPartiteStatus = async (ragioneSocialeId, anno) => {
  try {
    if (!ragioneSocialeId) return null;
    const response = await api.get(`piani-utilizzo/ragioni-sociali/${ragioneSocialeId}/partite/check`, { params: { anno } });
    return response.data;
  } catch (err) {
    console.error(`Error checking partite status for ${ragioneSocialeId}:`, err);
    return null;
  }
};

export const getAnniDettagliato = async (ragioneSocialeId) => {
  try {
    if (!ragioneSocialeId) return [];
    const response = await api.get(`piani-utilizzo/ragioni-sociali/${ragioneSocialeId}/anni`);
    return Array.isArray(response.data) ? response.data : [];
  } catch (err) {
    console.error(`Error fetching anni for ${ragioneSocialeId}:`, err);
    return [];
  }
};

export const confirmPartiteMapping = async (ragioneSocialeId, payload) => {
  try {
    const response = await api.post(`piani-utilizzo/ragioni-sociali/${ragioneSocialeId}/partite/confirm`, payload);
    return response.data;
  } catch (err) {
    console.error('Error confirming partite mapping:', err.response ? err.response.data : err.message);
    throw err;
  }
};

