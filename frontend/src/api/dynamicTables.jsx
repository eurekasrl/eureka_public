import api from "./base";

export const getAllTables = async () => {
  try {
    const response = await api.get('/tables/');
    return response.data;
  } catch (error) {
    console.error("Error fetching all tables:", error);
    throw error;
  }
};

export const getDynamicTableSchema = async (schemaName, tableName) => {
  try {
    const response = await api.get(`/tables/${schemaName}/${tableName}/schema/`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching schema for ${schemaName}.${tableName}:`, error);
    throw error;
  }
};

export const getDynamicTableData = async (schemaName, tableName, options = {}) => {
  const {skip=0, limit=100, filters = {}} = options
  try {
    const params = { skip, limit}
    if (Object.keys(filters).length>0) {
      params.filters = JSON.stringify(filters)
    }
    const response = await api.get(`/tables/${schemaName}/${tableName}/data/`, {
      params: params
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching data for ${schemaName}.${tableName}:`, error);
    throw error;
  }
};

export const addDynamicTableRow = async (schemaName, tableName, rowData) => {
  try {
    const response = await api.post(`/tables/${schemaName}/${tableName}/data/`, rowData);
    return response.data;
  } catch (error) {
    console.error(`Error adding row to ${schemaName}.${tableName}:`, error.response ? error.response.data : error.message);
    throw error;
  }
};

export const updateDynamicTableRow = async (schemaName, tableName, primaryKeyValue, rowData) => {
  try {
    const response = await api.put(`/tables/${schemaName}/${tableName}/data/${primaryKeyValue}`, rowData);
    return response.data;
  } catch (error) {
    console.error(`Error updating row in ${schemaName}.${tableName}:`, error.response ? error.response.data : error.message);
    throw error;
  }
};

export const deleteDynamicTableRow = async (schemaName, tableName, primaryKeyValue) => {
  try {
    await api.delete(`/tables/${schemaName}/${tableName}/data/${primaryKeyValue}`);
  } catch (error) {
    console.error(`Error deleting row from ${schemaName}.${tableName}:`, error.response ? error.response.data : error.message);
    throw error;
  }
};
