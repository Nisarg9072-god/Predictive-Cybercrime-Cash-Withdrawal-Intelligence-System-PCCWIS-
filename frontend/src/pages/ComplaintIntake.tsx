import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FilePlus, ShieldAlert, Cpu } from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';
import { MOCK_SCENARIOS } from '../services/api';

export function ComplaintIntake() {
  const navigate = useNavigate();
  const { loadScenario, addComplaint } = useInvestigation();
  const [loading, setLoading] = useState(false);
  const [selectedDemo, setSelectedDemo] = useState(MOCK_SCENARIOS.SCENARIO_001.id);
  const [amountLost, setAmountLost] = useState('1,50,000');
  const [city, setCity] = useState('Bengaluru');
  const [state, setState] = useState('Karnataka');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    // Simulate API delay for intake
    setTimeout(async () => {
      // Get base scenario to clone
      const baseScenario = MOCK_SCENARIOS[selectedDemo as keyof typeof MOCK_SCENARIOS];
      
      if (baseScenario) {
        // In a real app we'd construct a new ID, but for demo we just load the base scenario
        // after adding it to the complaints list (if it wasn't there already, though it is by default)
        const customScenario = {
          ...baseScenario,
          complaintDetails: {
            ...baseScenario.complaintDetails,
            dateReported: new Date().toLocaleString(),
            amountLost: `₹${amountLost}`,
            location: `${city}, ${state}`,
            victimName: baseScenario.complaintDetails?.victimName || 'Unknown',
            contact: baseScenario.complaintDetails?.contact || 'N/A',
            utr: baseScenario.complaintDetails?.utr || 'N/A'
          }
        };
        addComplaint(customScenario);
        await loadScenario(selectedDemo);
      }
      
      navigate('/command-center');
    }, 1200);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '1.5rem', alignItems: 'center' }}>
      
      <div style={{ width: '100%', maxWidth: '900px', marginTop: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
          <FilePlus className="text-primary" size={32} />
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.25rem' }}>NCRP Manual Intake</h1>
            <p className="text-muted">Initiate predictive intelligence stream from raw complaint data</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="bg-panel" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          
          <div style={{ padding: '1rem', backgroundColor: 'var(--bg-primary)', border: '1px solid var(--primary-color)', borderRadius: 'var(--radius-sm)' }}>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--primary-color)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>
              Select Demo Target Scenario
            </label>
            <select 
              value={selectedDemo}
              onChange={e => setSelectedDemo(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', fontSize: '0.875rem', backgroundColor: 'var(--bg-panel)', color: 'var(--text-primary)' }}
            >
              {Object.values(MOCK_SCENARIOS).map(s => (
                <option key={s.id} value={s.id}>{s.id} - {s.title}</option>
              ))}
            </select>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
              (Note: Forms below are for visual structure. Submission will load the selected demo scenario.)
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            
            {/* Victim Details */}
            <div>
              <h3 style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>VICTIM DETAILS</h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Victim Name</label>
                  <input type="text" defaultValue="John Doe" style={{ width: '100%' }} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Victim Account</label>
                    <input type="text" defaultValue="3190xxxx912" style={{ width: '100%', fontFamily: 'var(--font-mono)' }} />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Bank</label>
                    <input type="text" defaultValue="HDFC Bank" style={{ width: '100%' }} />
                  </div>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Contact Information</label>
                  <input type="text" defaultValue="+91-9876543210" style={{ width: '100%' }} />
                </div>
              </div>
            </div>

            {/* Crime Details */}
            <div>
              <h3 style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>CRIME DETAILS</h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Amount Lost (₹)</label>
                    <input type="text" value={amountLost} onChange={e => setAmountLost(e.target.value)} style={{ width: '100%', fontFamily: 'var(--font-mono)' }} />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Crime Category</label>
                    <select style={{ width: '100%' }}>
                      <option>Financial Fraud</option>
                      <option>Investment Scam</option>
                      <option>Digital Arrest</option>
                    </select>
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem' }}>City</label>
                    <input type="text" value={city} onChange={e => setCity(e.target.value)} style={{ width: '100%' }} />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem' }}>State</label>
                    <input type="text" value={state} onChange={e => setState(e.target.value)} style={{ width: '100%' }} />
                  </div>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Transaction Reference / UTR</label>
                  <input type="text" defaultValue="UTR987654321012" style={{ width: '100%', fontFamily: 'var(--font-mono)' }} />
                </div>
              </div>
            </div>

          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--status-warning)', fontSize: '0.75rem', fontWeight: 600 }}>
              <ShieldAlert size={16} /> Data will be ingested into predictive AI stream immediately
            </div>
            <button 
              type="submit" 
              disabled={loading}
              style={{ padding: '0.75rem 2rem', backgroundColor: 'var(--primary-color)', color: '#000', borderRadius: 'var(--radius-sm)', fontWeight: 700, fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
            >
              {loading ? <><Cpu size={16} className="spin" /> INGESTING DATA...</> : <><Cpu size={16} /> START PREDICTIVE INVESTIGATION</>}
            </button>
          </div>

        </form>
      </div>

    </div>
  );
}
