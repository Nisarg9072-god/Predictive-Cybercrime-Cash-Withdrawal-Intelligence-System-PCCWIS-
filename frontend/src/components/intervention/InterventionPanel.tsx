import { Shield, Building, CheckCircle } from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';

export function InterventionPanel() {
  const { activeScenario } = useInvestigation();

  if (!activeScenario) {
    return (
      <div className="bg-panel" style={{ padding: 'var(--space-6)', borderRadius: 'var(--radius-md)', border: '1px dashed var(--border-strong)', textAlign: 'center', color: 'var(--text-muted)' }}>
        No active investigation selected.
      </div>
    );
  }

  const { bankIntervention, leaIntervention } = activeScenario;

  const isSafe = activeScenario.verdict === 'LEGITIMATE_TRANSACTION_VERIFIED_CLEAR';

  if (isSafe) {
    return (
      <div className="bg-panel" style={{ padding: 'var(--space-6)', borderRadius: 'var(--radius-md)', border: '1px solid var(--status-safe)', backgroundColor: 'var(--status-safe-bg)' }}>
        <h3 style={{ color: 'var(--status-safe)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', fontSize: '1.125rem' }}>
          <CheckCircle /> ZERO HARM: NO INTERVENTION REQUIRED
        </h3>
        <p style={{ color: 'var(--text-secondary)' }}>
          This transaction has been verified as legitimate. Interventions have been suppressed to protect citizen funds.
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
      <div className="bg-panel" style={{ padding: 'var(--space-6)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
        <h3 style={{ fontSize: '1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Building className="text-primary" size={18} /> Bank Intervention
        </h3>
        {bankIntervention.required ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="text-muted">Status:</span>
              <span className="text-warning" style={{ fontWeight: 600 }}>{bankIntervention.status}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="text-muted">Target Amount:</span>
              <span style={{ fontFamily: 'var(--font-mono)' }}>{bankIntervention.amount}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span className="text-muted">CFCFRMS Ref:</span>
              <span style={{ fontFamily: 'var(--font-mono)' }}>{bankIntervention.refId}</span>
            </div>
            <button 
              onClick={() => alert(`SIMULATION: Triggering Lien on ${bankIntervention.amount} via CFCFRMS ${bankIntervention.refId}`)}
              style={{ padding: '0.75rem', backgroundColor: 'var(--status-warning)', color: '#000', border: 'none', borderRadius: 'var(--radius-sm)', fontWeight: 700, fontSize: '0.75rem', cursor: 'pointer', width: '100%' }}
            >
              TRIGGER MANUAL LIEN
            </button>
          </div>
        ) : (
          <div className="text-muted">Not Required</div>
        )}
      </div>

      <div className="bg-panel" style={{ padding: 'var(--space-6)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
        <h3 style={{ fontSize: '1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Shield className="text-critical" size={18} /> LEA Dispatch
        </h3>
        {leaIntervention.required ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="text-muted">Status:</span>
              <span className="text-critical" style={{ fontWeight: 600 }}>{leaIntervention.status}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="text-muted">Assigned Unit:</span>
              <span>{leaIntervention.unit}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span className="text-muted">ETA:</span>
              <span className="text-critical" style={{ fontWeight: 'bold' }}>{leaIntervention.eta}</span>
            </div>
            <button 
              onClick={() => alert(`SIMULATION: Dispatching ${leaIntervention.unit}`)}
              style={{ padding: '0.75rem', backgroundColor: 'var(--status-critical)', color: '#fff', border: 'none', borderRadius: 'var(--radius-sm)', fontWeight: 700, fontSize: '0.75rem', cursor: 'pointer', width: '100%' }}
            >
              PRIORITY DISPATCH
            </button>
          </div>
        ) : (
          <div className="text-muted">Not Required</div>
        )}
      </div>
    </div>
  );
}
