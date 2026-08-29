import { useState } from 'react';
import { Map, Target, Clock } from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';
import { RiskMap } from '../components/map/RiskMap';

export function IntelligenceMap() {
  const { activeScenario } = useInvestigation();
  const [selectedLocation, setSelectedLocation] = useState<any>(null);

  if (!activeScenario) {
    return (
      <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        No active investigation selected. Return to Command Center.
      </div>
    );
  }

  const isSafe = activeScenario.verdict === 'LEGITIMATE_TRANSACTION_VERIFIED_CLEAR';
  const hotspots = activeScenario.predictedAtms;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%' }}>
      
      <div className="bg-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
            <Map className="text-primary" /> Predictive Intelligence & GIS
          </h1>
          <p className="text-muted" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            Predictive ATM Hotspot Analysis for ID: {activeScenario.id}
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '1.5rem', flex: 1 }}>
        {/* Map Container */}
        <div className="bg-panel" style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden', padding: '0.25rem' }}>
          <div style={{ flex: 1, borderRadius: 'var(--radius-sm)', overflow: 'hidden' }}>
            <RiskMap 
              locations={hotspots} 
              onLocationSelect={setSelectedLocation} 
            />
          </div>
        </div>

        {/* Right Intelligence Panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', overflowY: 'auto' }}>
          
          {/* Temporal Decay Chart (Mock) */}
          <div className="bg-panel" style={{ padding: '1.5rem' }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
              <Clock size={16} className="text-primary" /> Temporal Prediction (Cashout)
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                <span className="text-muted">Current</span>
                <span style={{ fontWeight: 600 }}>12%</span>
              </div>
              <div style={{ width: '100%', height: '4px', backgroundColor: 'var(--bg-primary)', borderRadius: '2px' }}><div style={{ width: '12%', height: '100%', backgroundColor: 'var(--primary-color)' }}></div></div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginTop: '0.5rem' }}>
                <span className="text-muted">+ 15 min</span>
                <span className="text-warning" style={{ fontWeight: 600 }}>64%</span>
              </div>
              <div style={{ width: '100%', height: '4px', backgroundColor: 'var(--bg-primary)', borderRadius: '2px' }}><div style={{ width: '64%', height: '100%', backgroundColor: 'var(--status-warning)' }}></div></div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginTop: '0.5rem' }}>
                <span className="text-muted">+ 30 min</span>
                <span className="text-critical" style={{ fontWeight: 600 }}>98%</span>
              </div>
              <div style={{ width: '100%', height: '4px', backgroundColor: 'var(--bg-primary)', borderRadius: '2px' }}><div style={{ width: '98%', height: '100%', backgroundColor: 'var(--status-critical)' }}></div></div>
            </div>
          </div>

          <div className="bg-panel" style={{ padding: '1.5rem', flex: 1 }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
              <Target size={16} className="text-primary" /> ATM Hotspot Ranking
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {hotspots.map((atm, i) => (
                <div key={atm.id} 
                  onClick={() => setSelectedLocation(atm)}
                  style={{ 
                    padding: '1rem', 
                    backgroundColor: selectedLocation?.id === atm.id ? 'var(--bg-panel-hover)' : 'var(--bg-primary)', 
                    border: '1px solid',
                    borderColor: selectedLocation?.id === atm.id ? 'var(--primary-color)' : 'var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)', 
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.875rem' }}>#{i+1} {atm.name}</span>
                    <span className={atm.riskScore > 80 ? 'text-critical' : 'text-primary'} style={{ fontWeight: 700, fontSize: '0.875rem' }}>
                      {atm.riskScore} RSK
                    </span>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    <div>Confidence: <span style={{ color: 'var(--text-primary)' }}>{atm.probability}%</span></div>
                    <div>ETA: <span style={{ color: 'var(--text-primary)' }}>{atm.probability > 70 ? '13 min' : '35 min'}</span></div>
                  </div>
                </div>
              ))}
            </div>
            
            {isSafe && (
              <div style={{ marginTop: '1.5rem', padding: '1rem', backgroundColor: 'var(--status-safe-bg)', border: '1px solid var(--status-safe)', borderRadius: 'var(--radius-sm)', color: 'var(--status-safe)', fontSize: '0.875rem', textAlign: 'center' }}>
                ZERO-HARM PRINCIPLE ACTIVE. No hotpot intervention required.
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
