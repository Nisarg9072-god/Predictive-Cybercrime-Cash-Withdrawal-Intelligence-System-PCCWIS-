import { ShieldAlert, AlertTriangle, AlertOctagon } from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';
import { InterventionPanel } from '../components/intervention/InterventionPanel';

export function AlertsPage() {
  const { activeScenario } = useInvestigation();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '1.5rem' }}>
      
      <div className="bg-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
            <ShieldAlert className="text-primary" /> Active Interventions Center
          </h1>
          <p className="text-muted">CFCFRMS / PCR Interlocks & Critical Alerts Feed</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem', flex: 1 }}>
        
        {/* Left: Active Interventions */}
        <div className="bg-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
            <AlertOctagon size={18} className="text-primary" /> Operational Interlocks
          </h2>
          
          {activeScenario ? (
            <InterventionPanel />
          ) : (
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
              Select a scenario to view active interlocks.
            </div>
          )}
        </div>

        {/* Right: Global Alerts Feed */}
        <div className="bg-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
            <AlertTriangle size={18} className="text-warning" /> Global System Alerts
          </h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', overflowY: 'auto', paddingRight: '0.5rem' }}>
            <div style={{ padding: '1rem', borderLeft: '2px solid var(--status-critical)', backgroundColor: 'var(--status-critical-bg)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--status-critical)' }}>CFCFRMS TIMEOUT</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>10m ago</span>
              </div>
              <div style={{ fontSize: '0.875rem' }}>API connection to Central Bank Gateway timed out. Re-trying node BLR-SEC-09.</div>
            </div>

            <div style={{ padding: '1rem', borderLeft: '2px solid var(--status-warning)', backgroundColor: 'var(--status-warning-bg)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--status-warning)' }}>PREDICTIVE DEVIATION</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>24m ago</span>
              </div>
              <div style={{ fontSize: '0.875rem' }}>Hotspot model uncertainty elevated for SCENARIO_003. Expanding geo-radius by 5km.</div>
            </div>
            
            <div style={{ padding: '1rem', borderLeft: '2px solid var(--status-safe)', backgroundColor: 'var(--status-safe-bg)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--status-safe)' }}>ZERO-HARM VERIFIED</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>45m ago</span>
              </div>
              <div style={{ fontSize: '0.875rem' }}>SCENARIO_006 processing complete. Cleared as legitimate. No intervention launched.</div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
