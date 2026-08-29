import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { LandingPage } from './pages/LandingPage';
import { AboutPage } from './pages/AboutPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { CommandCenter } from './pages/CommandCenter';
import { InvestigationView } from './pages/InvestigationView';
import { IntelligenceMap } from './pages/IntelligenceMap';
import { LegalDossier } from './pages/LegalDossier';
import { AlertsPage } from './pages/AlertsPage';
import { ComplaintsList } from './pages/ComplaintsList';
import { ComplaintIntake } from './pages/ComplaintIntake';
import { AuditTrail } from './pages/AuditTrail';
import { SystemMonitoring } from './pages/SystemMonitoring';
import { Reports } from './pages/Reports';
import { AuthProvider, useAuth } from './context/AuthContext';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to={`/login?redirect=${encodeURIComponent(location.pathname)}`} replace />;
  }

  return <>{children}</>;
}

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
          <Route path="/command-center" element={<CommandCenter />} />
          <Route path="/complaints" element={<ComplaintsList />} />
          <Route path="/complaints/new" element={<ComplaintIntake />} />
          <Route path="/investigation" element={<InvestigationView />} />
          
          <Route path="/intelligence-map" element={<IntelligenceMap />} />
          {/* Risk map points to intelligence map for now, as they share GIS */}
          <Route path="/risk-map" element={<IntelligenceMap />} />
          {/* Network can be standalone or point to investigation */}
          <Route path="/network" element={<div style={{ padding: '2rem' }}>Transaction Network Deep Dive (Coming Soon)</div>} />
          
          <Route path="/interventions" element={<AlertsPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          
          <Route path="/dossier" element={<LegalDossier />} />
          <Route path="/reports" element={<Reports />} />
          
          <Route path="/audit" element={<AuditTrail />} />
          <Route path="/system" element={<SystemMonitoring />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}

export default App;
