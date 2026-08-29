import { Activity, Search, Cpu, Database, Network } from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';
import { TransactionGraph } from '../components/network/TransactionGraph';

export function InvestigationView() {
  const { activeScenario } = useInvestigation();

  if (!activeScenario) {
    return (
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', color: 'var(--text-muted)' }}>
        <Search size={48} style={{ opacity: 0.5, marginBottom: '1rem' }} />
        <h2>No Active Investigation</h2>
        <p>Return to the Command Center to select an operational scenario.</p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%' }}>
      {/* Case Header */}
      <div className="bg-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
            <Activity className="text-primary" /> Active Deep Investigation
          </h1>
          <p className="text-muted" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>ID: {activeScenario.id}</span>
            <span>{activeScenario.title}</span>
          </p>
        </div>
        <div style={{ display: 'flex', gap: '1.5rem', textAlign: 'right' }}>
          <div>
            <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Severity</div>
            <div className={`text-${activeScenario.riskLevel === 'CRITICAL' ? 'critical' : activeScenario.riskLevel === 'HIGH' ? 'warning' : 'safe'}`} style={{ fontWeight: 700, fontSize: '1.125rem' }}>
              {activeScenario.riskLevel}
            </div>
          </div>
          <div>
            <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Status</div>
            <div style={{ fontWeight: 700, fontSize: '1.125rem', color: 'var(--primary-color)' }}>ANALYSIS_ACTIVE</div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Financial Trace */}
        <div className="bg-navy-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Database size={16} className="text-primary" /> Financial Trace Vector
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>
              <span className="text-muted">Source Account</span>
              <span style={{ fontFamily: 'var(--font-mono)' }}>XXXX-XXXX-8921</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>
              <span className="text-muted">Layer-1 Mule</span>
              <span className="text-warning" style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>IDENTIFIED (3 Hops)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>
              <span className="text-muted">Transfer Velocity</span>
              <span style={{ fontWeight: 600 }}>14 tx/min (Suspicious)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="text-muted">Chain Analysis ID</span>
              <span style={{ fontFamily: 'var(--font-mono)' }}>CH-9982-XYZ</span>
            </div>
          </div>
        </div>

        {/* Forensic Profile */}
        <div className="bg-navy-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Cpu size={16} className="text-primary" /> Forensic Profile
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>
              <span className="text-muted">KYC Status</span>
              <span className="text-warning" style={{ fontWeight: 600 }}>FORGED (94% prob)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>
              <span className="text-muted">Account Age</span>
              <span style={{ fontWeight: 600 }}>3 Days</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>
              <span className="text-muted">Device / IMEI Indicator</span>
              <span className="text-critical" style={{ fontWeight: 600 }}>BURNER_FLAGGED</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="text-muted">Aggregated Risk Score</span>
              <span className="text-critical" style={{ fontWeight: 700, fontSize: '1.125rem' }}>{activeScenario.overallRisk}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Transaction Graph */}
      <div className="bg-panel" style={{ flex: 1, padding: '1.5rem', display: 'flex', flexDirection: 'column', minHeight: '500px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 700, textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
            <Network size={16} className="text-primary" /> Multi-Hop Transaction Graph
          </h3>
          <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><div style={{ width: '8px', height: '8px', backgroundColor: 'var(--status-safe)', borderRadius: '50%' }}></div> Victim</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><div style={{ width: '8px', height: '8px', backgroundColor: 'var(--status-warning)', borderRadius: '50%' }}></div> Layer 1/2</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><div style={{ width: '8px', height: '8px', backgroundColor: 'var(--status-critical)', borderRadius: '50%' }}></div> Cashout Node</span>
          </div>
        </div>
        <div style={{ flex: 1, borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-strong)', overflow: 'hidden' }}>
          <TransactionGraph nodesData={activeScenario.networkNodes} edgesData={activeScenario.networkEdges} />
        </div>
      </div>

    </div>
  );
}
