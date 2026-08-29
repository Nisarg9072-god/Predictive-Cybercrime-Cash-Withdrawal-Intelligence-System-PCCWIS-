import { HardDrive, Server, Database, Activity, Wifi } from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';

export function SystemMonitoring() {
  const { isDemoMode } = useInvestigation();

  const services = [
    { name: 'NCRP Ingestion Gateway', status: isDemoMode ? 'SIMULATED' : 'ONLINE', latency: '42ms', uptime: '99.98%' },
    { name: 'Predictive GIS Engine', status: isDemoMode ? 'SIMULATED' : 'ONLINE', latency: '112ms', uptime: '99.95%' },
    { name: 'Swarm Consensus Matrix', status: isDemoMode ? 'SIMULATED' : 'ONLINE', latency: '230ms', uptime: '99.90%' },
    { name: 'Transaction Graph Analyzer', status: isDemoMode ? 'SIMULATED' : 'ONLINE', latency: '85ms', uptime: '99.99%' },
    { name: 'CFCFRMS Interlock API', status: isDemoMode ? 'SIMULATED' : 'ONLINE', latency: '150ms', uptime: '98.50%' },
    { name: 'LEA Dispatch API', status: isDemoMode ? 'SIMULATED' : 'ONLINE', latency: '65ms', uptime: '99.99%' },
    { name: 'Cryptographic Audit Ledger', status: 'ONLINE', latency: '12ms', uptime: '100%' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '1.5rem' }}>
      
      <div className="bg-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
            <HardDrive className="text-primary" /> System Monitoring
          </h1>
          <p className="text-muted">I4C Core Node Health and Sub-system Status</p>
        </div>
        
        {isDemoMode && (
          <div style={{ padding: '0.5rem 1rem', backgroundColor: 'var(--status-warning-bg)', border: '1px solid var(--status-warning)', borderRadius: 'var(--radius-sm)', color: 'var(--status-warning)', fontWeight: 700, fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Wifi size={16} /> DEMO / OFFLINE SIMULATION ACTIVE
          </div>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
        <div className="bg-panel" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ padding: '1rem', backgroundColor: 'var(--bg-primary)', borderRadius: 'var(--radius-md)', color: 'var(--primary-color)' }}><Server size={24} /></div>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Active Node</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>BLR-SEC-09</div>
          </div>
        </div>
        <div className="bg-panel" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ padding: '1rem', backgroundColor: 'var(--bg-primary)', borderRadius: 'var(--radius-md)', color: 'var(--primary-color)' }}><Database size={24} /></div>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Memory Load</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>42.8%</div>
          </div>
        </div>
        <div className="bg-panel" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ padding: '1rem', backgroundColor: 'var(--bg-primary)', borderRadius: 'var(--radius-md)', color: 'var(--primary-color)' }}><Activity size={24} /></div>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Network I/O</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>894 Mbps</div>
          </div>
        </div>
      </div>

      <div className="bg-panel" style={{ flex: 1, padding: '1.5rem', overflowY: 'auto' }}>
        <h2 style={{ fontSize: '1rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '1.5rem', color: 'var(--text-secondary)' }}>
          Microservice Health
        </h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1rem' }}>
          {services.map((svc, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 1.5rem', backgroundColor: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontWeight: 600 }}>{svc.name}</div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '2rem', width: '300px', justifyContent: 'flex-end' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                  <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Latency</span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}>{svc.latency}</span>
                </div>
                
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                  <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Uptime</span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}>{svc.uptime}</span>
                </div>

                <div style={{ width: '100px', textAlign: 'right' }}>
                  <span style={{ 
                    padding: '0.25rem 0.5rem', 
                    borderRadius: 'var(--radius-sm)', 
                    fontSize: '0.75rem', 
                    fontWeight: 700,
                    backgroundColor: svc.status === 'ONLINE' ? 'var(--status-safe-bg)' : 'var(--status-warning-bg)',
                    color: svc.status === 'ONLINE' ? 'var(--status-safe)' : 'var(--status-warning)',
                    border: `1px solid ${svc.status === 'ONLINE' ? 'var(--status-safe)' : 'var(--status-warning)'}`
                  }}>
                    {svc.status}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
    </div>
  );
}
