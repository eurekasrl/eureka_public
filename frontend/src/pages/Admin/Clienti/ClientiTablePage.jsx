import React from 'react';
import ClientiTable from '../../../components/ClientiTable'

const ClientiTablePage = () => {
    const title = "Seleziona una ragione sociale o un gruppo";
    const linkPrefix = "/admin";

    return (
        <ClientiTable title={title} linkPrefix={linkPrefix} />
    );
};

export default ClientiTablePage;