import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { ShieldCheck, ShieldAlert, Cpu } from 'lucide-react';

interface ConsensusProps {
  weights: { financial: number; forensic: number; geoSpatial: number };
  verdict: string;
  overallRisk: number;
}

export function ConsensusGauge({ weights, verdict, overallRisk }: ConsensusProps) {
  const data = [
    { name: 'Financial Ledger', value: weights.financial, color: '#2563EB' },
    { name: 'Forensic Profiler', value: weights.forensic, color: '#06B6D4' },
    { name: 'Geo-Spatial ML', value: weights.geoSpatial, color: '#10B981' },
  ];

  const isClear = verdict === 'LEGITIMATE_TRANSACTION_VERIFIED_CLEAR';
  const isBorderline = verdict === 'BORDERLINE_RE_EVALUATION';

  return (
    <div className="bg-navy-panel" style={{ borderRadius: 'var(--radius-md)', border: '1px solid var(--border-navy)', padding: 'var(--space-6)' }}>
      <h2 style={{ fontSize: '1.25rem', marginBottom: 'var(--space-6)', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
        <Cpu className="text-primary" /> Swarm Intelligence Consensus
      </h2>

      <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
        <div style={{ width: '160px', height: '160px', position: 'relative' }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={70}
                paddingAngle={5}
                dataKey="value"
                stroke="none"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: 'var(--bg-navy-panel)', border: '1px solid var(--border-navy)', borderRadius: '4px' }}
                itemStyle={{ color: '#fff' }}
              />
            </PieChart>
          </ResponsiveContainer>
          
          <div style={{ 
            position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, 
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' 
          }}>
            <span style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{overallRisk}%</span>
            <span className="text-muted" style={{ fontSize: '0.75rem' }}>Risk</span>
          </div>
        </div>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {data.map(agent => (
            <div key={agent.name} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: agent.color }} />
                <span style={{ fontSize: '0.875rem' }}>{agent.name}</span>
              </div>
              <span style={{ fontWeight: 600, fontSize: '0.875rem', fontFamily: 'var(--font-mono)' }}>{agent.value}%</span>
            </div>
          ))}
        </div>
      </div>

      <div style={{ 
        marginTop: 'var(--space-6)', 
        padding: 'var(--space-4)', 
        backgroundColor: isClear ? 'var(--status-safe-bg)' : isBorderline ? 'var(--status-warning-bg)' : 'var(--status-critical-bg)', 
        borderRadius: 'var(--radius-sm)', 
        border: `1px solid ${isClear ? 'var(--status-safe)' : isBorderline ? 'var(--status-warning)' : 'var(--status-critical)'}`,
        display: 'flex', alignItems: 'flex-start', gap: 'var(--space-3)' 
      }}>
        {isClear ? (
          <ShieldCheck className="text-safe" style={{ flexShrink: 0 }} />
        ) : (
          <ShieldAlert className={isBorderline ? "text-warning" : "text-critical"} style={{ flexShrink: 0 }} />
        )}
        <div>
          <div style={{ 
            fontWeight: 600, 
            color: isClear ? 'var(--status-safe)' : isBorderline ? 'var(--status-warning)' : 'var(--status-critical)', 
            marginBottom: '0.25rem' 
          }}>
            {verdict.replace(/_/g, ' ')}
          </div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            {isClear 
              ? 'Multi-agent consensus indicates legitimate behavior. Interventions paused.' 
              : isBorderline 
              ? 'Borderline evidence. ReAct reasoning mode active for deep evaluation.' 
              : 'Multi-agent consensus confirms malicious activity with high confidence. Proceeding to intervention phase.'}
          </div>
        </div>
      </div>
    </div>
  );
}
