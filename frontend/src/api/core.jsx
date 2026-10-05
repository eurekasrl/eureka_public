import api from "./base";

//Ragioni Sociali
export const getAllragioniSociali = async (q = '') =>{
  try {
    const response = await api.get(`/ragioni-sociali/list`, {params: { q }})
    return response.data;
  } catch (error) {
    console.error(`Error fetching Ragioni Sociali`, error)
    throw error
  }
}

export const getRagioneSocialeById = async (ragione_sociale_id) => {
  try {
    if (!ragione_sociale_id) return null;
    const response = await api.get(`/ragioni-sociali/${ragione_sociale_id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching ragione sociale ${ragione_sociale_id}:`, error);
    return [];
  }
};
//COMUNI
export const getComuni = async (q = '' ) => {
  try {
    const response = await api.get('/comuni/list', { params: { q } });
    return response.data;
  } catch (error) {
    console.error("Error fetching comuni:", error);
    throw error;
  }
};

export const getComune = async (codice_comune) => {
  try {
    if (!codice_comune) return null;
    const response = await api.get(`/comuni/${codice_comune}`);
    return [response.data];
  } catch (error) {
    console.error("Error fetching comune:", error);
    return [];
  }
};
//RAMI
export const getAllRami = async () => {
  try {
    const response = await api.get(`/rami/list`)
    return response.data;
  } catch (error) {
    console.error (`Error fetching rami:`, error);
    throw error
  }
}
//COMPAGNIE
export const getAllCompagnie = async () => {
  try {
    const response = await api.get(`/compagnie/list`)
    return response.data;
  } catch (error) {
    console.error (`Error fetching compagnie:`, error);
    throw error
  }
}
//INTERMEDIARI
export const getAllIntermediari = async () => {
  try {
    const response = await api.get(`/intermediari/list`)
    return response.data;
  } catch (error) {
    console.error (`Error fetching intermediari:`, error);
    throw error
  }
}
//CONDIFESA
export const getAllCondifesa = async () => {
  try {
    const response = await api.get(`/condifesa/list`)
    return response.data;
  } catch (error) { 
    console.error (`Error fetching condifesa:`, error);
    throw error
  }
}

export const getCondifesaById = async (condifesaId) => {
  const response = await api.get(`/condifesa/${condifesaId}`);
  return response.data;
}
//GRUPPI
export const getGruppoById = async (gruppo_id) => {
  try {
    if (!gruppo_id) return null;
    const response = await api.get(`/gruppi/${gruppo_id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching gruppo ${gruppo_id}:`, error);
    return [];
  }
};

//RELAZIONE RCI
export const getRelazioneRci = async (ramoId) => {
  try {
    if (!ramoId) return null
    const response = await api.get(`/relazione_rci/${ramoId}`)
    return response.data
  } catch (error) {
    console.error(`Error fetching relazione rci for ${ramoId}:`, error);
    return [];
  }
}