import React from 'react';
import ClientiTable from '../../components/ClientiTable';

const PianiUtilizzoTablePage = () => {
    const title = "Seleziona una ragione sociale per cui vuoi preparare un Piano di Utilizzo";
    const linkPrefix = "/piani-utilizzo";

    return (
        <ClientiTable title={title} linkPrefix={linkPrefix} />
    );
};

export default PianiUtilizzoTablePage;