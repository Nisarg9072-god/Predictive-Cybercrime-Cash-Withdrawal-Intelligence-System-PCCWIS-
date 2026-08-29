import { Shield, Hash, Search } from 'lucide-react';

export function AuditTrail() {
  const mockLogs = [
    { time: '2026-08-29 10:14:22', user: 'SYSTEM', action: 'NCRP_INGEST', case: 'SCENARIO_001', hash: '8f4e92a...c3b1', status: 'SUCCESS' },
    { time: '2026-08-29 10:15:01', user: 'AGENT_TRACER', action: 'GRAPH_EXPAND', case: 'SCENARIO_001', hash: 'e2b51a0...9d7f', status: 'SUCCESS' },
    { time: '2026-08-29 10:16:33', user: 'AGENT_RISK', action: 'SCORE_EVAL', case: 'SCENARIO_001', hash: '4a1c88d...2e5b', status: 'SUCCESS' },
    { time: '2026-08-29 10:18:10', user: 'AGENT_GEO', action: 'HOTSPOT_PREDICT', case: 'SCENARIO_001', hash: '9b7f33e...1a4c', status: 'SUCCESS' },
    { time: '2026-08-29 10:19:45', user: 'SYSTEM', action: 'INTERLOCK_TRIGGER', case: 'SCENARIO_001', hash: '5c2d99f...8b0a', status: 'WARNING' },
    { time: '2026-08-29 10:20:00', user: 'Insp. Rahul S.', action: 'DOSSIER_GENERATE', case: 'SCENARIO_001', hash: '3d6e11a...7f2c', status: 'SUCCESS' },
    { time: '2026-08-29 10:35:12', user: 'SYSTEM', action: 'NCRP_INGEST', case: 'SCENARIO_006', hash: '1f8a44b...9e3d', status: 'SUCCESS' },
    { time: '2026-08-29 10:36:00', user: 'AGENT_TRACER', action: 'GRAPH_EXPAND', case: 'SCENARIO_006', hash: '7c9e12f...4b2a', status: 'SUCCESS' },
    { time: '2026-08-29 10:38:22', user: 'SWARM_CONSENSUS', action: 'ZERO_HARM_CLEAR', case: 'SCENARIO_006', hash: '2a4b88c...9d1e', status: 'SUCCESS' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '1.5rem' }}>
      
      <div className="bg-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
            <Shield className="text-primary" /> Immutable Audit Trail
          </h1>
          <p className="text-muted">Global system event log and cryptographic signatures</p>
        </div>
      </div>

      <div className="bg-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        
        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--border-strong)', display: 'flex', justifyContent: 'flex-end', alignItems: 'center', backgroundColor: 'var(--bg-primary)' }}>
          <div style={{ position: 'relative' }}>
            <Search size={14} className="text-muted" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
            <input type="text" placeholder="Search hash, user, case..." style={{ padding: '0.4rem 1rem 0.4rem 2rem', width: '250px', fontSize: '0.875rem' }} />
          </div>
        </div>

        <div style={{ overflowY: 'auto', flex: 1 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead style={{ position: 'sticky', top: 0, backgroundColor: 'var(--bg-panel)', zIndex: 1 }}>
              <tr style={{ borderBottom: '2px solid var(--border-strong)', textAlign: 'left', color: 'var(--text-muted)' }}>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.75rem' }}>Timestamp</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.75rem' }}>Actor</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.75rem' }}>Action</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.75rem' }}>Investigation ID</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.75rem' }}>SHA-256 Signature</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.75rem' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {mockLogs.map((log, i) => (
                <tr key={i} style={{ borderBottom: '1px solid var(--border-subtle)', transition: 'background 0.2s' }} onMouseOver={e => e.currentTarget.style.backgroundColor = 'var(--bg-panel-hover)'} onMouseOut={e => e.currentTarget.style.backgroundColor = 'transparent'}>
                  <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>{log.time}</td>
                  <td style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>{log.user}</td>
                  <td style={{ padding: '1rem 1.5rem', color: 'var(--primary-color)' }}>{log.action}</td>
                  <td style={{ padding: '1rem 1.5rem', fontFamily: 'var(--font-mono)' }}>{log.case}</td>
                  <td style={{ padding: '1rem 1.5rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Hash size={14} /> {log.hash}
                  </td>
                  <td style={{ padding: '1rem 1.5rem' }}>
                    <span style={{ color: log.status === 'SUCCESS' ? 'var(--status-safe)' : 'var(--status-warning)', fontWeight: 700, fontSize: '0.75rem' }}>
                      {log.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
