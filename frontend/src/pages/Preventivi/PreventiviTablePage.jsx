import React from 'react';
import ClientiTable from '../../components/ClientiTable';

const PreventiviTablePage = () => {
    const title = "Seleziona una ragione sociale per cui vuoi preparare o modificare un preventivo";
    const linkPrefix = "/preventivi";

    return (
        <ClientiTable title={title} linkPrefix={linkPrefix} />
    );
};

export default PreventiviTablePage;