import React, { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { Box, CircularProgress } from '@mui/material';
import { SnackbarProvider } from './context/SnackbarProvider';
import Layout from './components/Layout';

// Lazy-load pages so each route is a separate chunk (smaller initial bundle).
const HomePage = lazy(() => import('./pages/Home/HomePage'));
const AdminPage = lazy(() => import('./pages/Admin/AdminPage'));
const TableListPage = lazy(() => import('./pages/Admin/Tables/TableListPage'));
const TableDataPage = lazy(() => import('./pages/Admin/Tables/TableDataPage'));
const ClientiPage = lazy(() => import('./pages/Admin/Clienti/ClientiPage'));
const ClientiTablePage = lazy(() => import('./pages/Admin/Clienti/ClientiTablePage'));
const PreventiviTablePage = lazy(() => import('./pages/Preventivi/PreventiviTablePage'));
const NewPreventivoPage = lazy(() => import('./pages/Preventivi/NewPreventivoPage'));
const RamoDispatcher = lazy(() => import('./pages/Preventivi/RamoDispatcher'));
const PreventivoPage = lazy(() => import('./pages/Preventivi/PreventivoPage'));
const PianiUtilizzoTablePage = lazy(() => import('./pages/PianiUtilizzo/PianiUtilizzoTablePage'));
const PianoUtilizzoPage = lazy(() => import('./pages/PianiUtilizzo/PianoUtilizzoPage'));
const PianoUtilizzoDashboardPage = lazy(() => import('./pages/PianiUtilizzo/PianoUtilizzoDashboardPage'));
const PartitePage = lazy(() => import('./pages/PianiUtilizzo/PartitePage'));

const theme = createTheme({
  palette: {
    primary: { main: '#2196f3' },
    secondary: { main: '#ff9800' },
  },
  typography: { fontFamily: 'Roboto, sans-serif' },
});

const PageLoader = () => (
  <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}>
    <CircularProgress />
  </Box>
);

function App() {
  return (
    <ThemeProvider theme={theme}>
      <SnackbarProvider>
      <Router>
        <Layout>
          <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            
            {/* Admin Routes */}
            <Route path='/admin' element={<AdminPage />} />
            <Route path="/admin/tables" element={<TableListPage />} />
            <Route path="/admin/tables/:schemaName/:tableName" element={<TableDataPage />} />
            <Route path="/admin/clienti" element={<ClientiTablePage />} />
            <Route path="/admin/ragioni-sociali/:ragioneSocialeId" element={<ClientiPage />} />
            <Route path="/admin/gruppi/:gruppoId" element={<ClientiPage />} />
            
            {/* Preventivi Routes */}
            <Route path="/preventivi" element={<PreventiviTablePage />} />
            
            {/* Step 1: Select Ramo, Compagnia, Intermediario */}
            <Route path="/preventivi/:ragioneSocialeId/new" element={<NewPreventivoPage />} />
            
            {/* Step 2: The Dispatcher (No ID yet, creates context) */}
            <Route path="/preventivi/:ragioneSocialeId/compose" element={<RamoDispatcher />} />
            
            {/* Edit Mode (ID exists) */}
            <Route path="/preventivi/edit/:preventivo_id" element={<RamoDispatcher />} />
            
            <Route path="/preventivi/ragioni-sociali/:ragioneSocialeId" element={<PreventivoPage />} />
            
            {/* Piani Utilizzo Routes */}
            <Route path="/piani-utilizzo" element={<PianiUtilizzoTablePage />} />
            <Route path="/piani-utilizzo/ragioni-sociali/:ragioneSocialeId" element={<PianoUtilizzoDashboardPage />} />
            <Route path="/piani-utilizzo/ragioni-sociali/:ragioneSocialeId/riepilogativi" element={<PianoUtilizzoPage />} />
            <Route path="/piani-utilizzo/ragioni-sociali/:ragioneSocialeId/dettagliati" element={<PianoUtilizzoPage />} />
            <Route path="/piani-utilizzo/ragioni-sociali/:ragioneSocialeId/partite" element={<PartitePage />} />

            {/*Tassi */}
            <Route path='/tassi' element={<>Tassu</>} />
          </Routes>
          </Suspense>
        </Layout>
      </Router>
      </SnackbarProvider>
    </ThemeProvider>
  );
}

export default App;