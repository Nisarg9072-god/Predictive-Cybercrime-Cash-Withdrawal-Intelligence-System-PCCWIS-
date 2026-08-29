import { useNavigate } from 'react-router-dom';
import { Activity, Map, Target, Play, ShieldAlert, Cpu } from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';
import { MOCK_SCENARIOS } from '../services/api';
import { InvestigationTimeline } from '../components/investigation/InvestigationTimeline';
import { RiskMap } from '../components/map/RiskMap';
import { GoldenHourTimer } from '../components/temporal/GoldenHourTimer';
import { InterventionPanel } from '../components/intervention/InterventionPanel';
import { ConsensusGauge } from '../components/risk/ConsensusGauge';

export function CommandCenter() {
  const navigate = useNavigate();
  const { activeScenario, loadScenario, isDemoMode } = useInvestigation();
  const scenarios = Object.values(MOCK_SCENARIOS);

  const handleScenarioSelect = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const id = e.target.value;
    if (id) {
      await loadScenario(id);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 'var(--space-6)' }}>
      
      {/* Top Command Bar */}
      <div className="bg-panel" style={{ padding: 'var(--space-4) var(--space-6)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.65rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.25rem', fontWeight: 700 }}>
              Active Intelligence Scenario
            </label>
            <select 
              value={activeScenario?.id || ''} 
              onChange={handleScenarioSelect}
              style={{ padding: '0.4rem 0.75rem', fontSize: '0.875rem', fontWeight: 600, width: '350px', backgroundColor: 'var(--bg-primary)' }}
            >
              <option value="" disabled>-- Select Operational Scenario --</option>
              {scenarios.map(s => (
                <option key={s.id} value={s.id}>{s.id}: {s.title}</option>
              ))}
            </select>
          </div>
          
          {activeScenario && (
            <div style={{ display: 'flex', gap: 'var(--space-6)', paddingLeft: 'var(--space-6)', borderLeft: '1px solid var(--border-strong)' }}>
              <div>
                <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.25rem', fontWeight: 700 }}>Swarm Status</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', fontWeight: 600, color: 'var(--ai-color)' }}>
                  <Cpu size={14} /> ACTIVE COMPUTE
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.25rem', fontWeight: 700 }}>System Node</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', fontWeight: 600, color: isDemoMode ? 'var(--status-warning)' : 'var(--status-safe)' }}>
                  <Activity size={14} /> {isDemoMode ? 'DEMO SIMULATION' : 'I4C MAINNET'}
                </div>
              </div>
            </div>
          )}
        </div>
        
        {activeScenario && (
           <button 
             onClick={() => navigate('/investigation')}
             style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem', backgroundColor: 'var(--primary-color)', color: '#000', borderRadius: 'var(--radius-sm)', fontWeight: 700, fontSize: '0.875rem' }}
           >
             <Play size={16} fill="currentColor" /> DEEP INVESTIGATION
           </button>
        )}
      </div>

      {!activeScenario ? (
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', color: 'var(--text-muted)', border: '1px dashed var(--border-strong)', borderRadius: 'var(--radius-md)', padding: 'var(--space-8)' }}>
          <ShieldAlert size={48} style={{ opacity: 0.5, marginBottom: 'var(--space-4)' }} />
          <h2 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem' }}>Awaiting Operational Input</h2>
          <p>Select a scenario from the top command bar to initialize the predictive intelligence dashboard.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr 380px', gap: 'var(--space-6)', flex: 1, overflow: 'hidden' }}>
          
          {/* Left: Autonomous Stream */}
          <div className="bg-panel" style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{ padding: 'var(--space-4)', borderBottom: '1px solid var(--border-strong)', fontWeight: 700, fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Activity className="text-primary" size={16} /> AUTONOMOUS STREAM
            </div>
            <div style={{ padding: 'var(--space-4)', overflowY: 'auto', flex: 1 }}>
              <InvestigationTimeline />
            </div>
          </div>

          {/* Center: Live GIS Map */}
          <div className="bg-navy-panel" style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden', padding: 'var(--space-2)' }}>
            <div style={{ padding: 'var(--space-3)', fontWeight: 700, fontSize: '0.875rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Map className="text-primary" size={16} /> LIVE GIS INTELLIGENCE
              </div>
              <div style={{ display: 'flex', gap: '0.75rem', fontSize: '0.65rem', textTransform: 'uppercase' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><div style={{ width: '8px', height: '8px', backgroundColor: 'var(--status-critical)', borderRadius: '50%' }}></div> High Risk</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><div style={{ width: '8px', height: '8px', backgroundColor: 'var(--primary-color)', borderRadius: '50%' }}></div> ATM Node</span>
              </div>
            </div>
            <div style={{ flex: 1, borderRadius: 'var(--radius-sm)', overflow: 'hidden' }}>
              <RiskMap locations={activeScenario.predictedAtms} onLocationSelect={() => {}} />
            </div>
          </div>

          {/* Right: Case Intelligence Panel */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', overflowY: 'auto', paddingRight: 'var(--space-2)' }}>
            
            <GoldenHourTimer 
              isSafe={activeScenario.verdict === 'LEGITIMATE_TRANSACTION_VERIFIED_CLEAR'}
              selectedAtm={activeScenario.predictedAtms[0]}
            />

            <ConsensusGauge 
              weights={activeScenario.swarmWeights}
              verdict={activeScenario.verdict}
              overallRisk={activeScenario.overallRisk}
            />
            
            <div className="bg-navy-panel" style={{ padding: 'var(--space-5)' }}>
              <h3 style={{ fontSize: '0.875rem', fontWeight: 700, marginBottom: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: '0.5rem', textTransform: 'uppercase' }}>
                <Target className="text-primary" size={16} /> Top Predicted Hotspots
              </h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                {activeScenario.predictedAtms.map((atm, i) => (
                  <div key={atm.id} style={{ display: 'flex', justifyContent: 'space-between', padding: 'var(--space-3)', backgroundColor: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', borderLeft: `3px solid ${atm.riskScore > 80 ? 'var(--status-critical)' : 'var(--primary-color)'}` }}>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '0.8125rem', marginBottom: '0.25rem' }}>#{i+1} {atm.name}</div>
                      <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>CONFIDENCE: {atm.probability}%</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div className={atm.riskScore > 80 ? 'text-critical' : 'text-primary'} style={{ fontWeight: 700, fontSize: '0.875rem' }}>{atm.riskScore} RSK</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-navy-panel" style={{ padding: 'var(--space-5)' }}>
              <h3 style={{ fontSize: '0.875rem', fontWeight: 700, marginBottom: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: '0.5rem', textTransform: 'uppercase' }}>
                <ShieldAlert className="text-primary" size={16} /> Intervention Status
              </h3>
              <InterventionPanel />
            </div>

          </div>
        </div>
      )}
    </div>
  );
}
