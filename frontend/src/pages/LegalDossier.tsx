import { FileSignature, Lock, Printer, Scale } from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';

export function LegalDossier() {
  const { activeScenario } = useInvestigation();

  if (!activeScenario) {
    return (
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', color: 'var(--text-muted)' }}>
        <Scale size={48} style={{ opacity: 0.5, marginBottom: '1rem' }} />
        <h2>No Active Investigation</h2>
        <p>Select a scenario to generate a statutory dossier.</p>
      </div>
    );
  }

  const handlePrint = () => {
    window.print();
  };

  return (
    <>
      <style>
        {`
          @media print {
            body * {
              visibility: hidden;
            }
            #dossier-print-area, #dossier-print-area * {
              visibility: visible;
            }
            #dossier-print-area {
              position: absolute;
              left: 0;
              top: 0;
              width: 100%;
              box-shadow: none !important;
              padding: 0 !important;
            }
            .no-print {
              display: none !important;
            }
          }
        `}
      </style>
      <div style={{ maxWidth: '1000px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Top Toolbar */}
      <div className="bg-panel no-print" style={{ padding: '1rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <FileSignature className="text-primary" size={24} />
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Statutory Legal Dossier</h1>
            <p className="text-muted" style={{ fontSize: '0.75rem' }}>Section 65B Indian Evidence Act / BNSS Compliant Format</p>
          </div>
        </div>
        
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button onClick={handlePrint} style={{ padding: '0.5rem 1rem', backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-strong)', color: 'var(--text-primary)', borderRadius: 'var(--radius-sm)', display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer' }}>
            <Printer size={16} /> Print / Export PDF
          </button>
          <div style={{ padding: '0.5rem 1rem', backgroundColor: 'var(--status-safe-bg)', border: '1px solid var(--status-safe)', borderRadius: 'var(--radius-sm)', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--status-safe)', fontWeight: 700, fontSize: '0.875rem' }}>
            <Lock size={16} /> EVIDENCE SEALED
          </div>
        </div>
      </div>

      {/* The "Paper" Document */}
      <div id="dossier-print-area" style={{ backgroundColor: '#ffffff', color: '#000000', padding: '4rem', minHeight: '800px', borderRadius: '4px', boxShadow: '0 0 10px rgba(0,0,0,0.5)', fontFamily: "'Times New Roman', serif" }}>
        
        <div style={{ textAlign: 'center', marginBottom: '3rem', borderBottom: '2px solid #000', paddingBottom: '1rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Government of India</h2>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>Ministry of Home Affairs - Indian Cyber Crime Coordination Centre</h3>
          <p style={{ marginTop: '1rem', fontStyle: 'italic' }}>CERTIFICATE UNDER SECTION 65B OF INDIAN EVIDENCE ACT, 1872</p>
          <p style={{ fontStyle: 'italic' }}>READ WITH BHARATIYA NAGARIK SURAKSHA SANHITA (BNSS)</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem', fontSize: '1rem' }}>
          <div>
            <p><strong>Investigation ID:</strong> {activeScenario.id}</p>
            <p><strong>Complaint Ack No:</strong> {activeScenario.id.replace('SCENARIO', 'ACK')}</p>
            <p><strong>Date of Generation:</strong> {new Date().toLocaleDateString()}</p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <p><strong>Generating Officer:</strong> Insp. Rahul Sharma</p>
            <p><strong>Generating Node:</strong> BLR-SEC-09</p>
            <p><strong>System Name:</strong> CYBER-INTERCEPT Predictive Engine</p>
          </div>
        </div>

        <div style={{ marginBottom: '2rem' }}>
          <h4 style={{ fontWeight: 'bold', borderBottom: '1px solid #000', paddingBottom: '0.25rem', marginBottom: '1rem' }}>1. CASE SUMMARY & PREDICTIVE INTELLIGENCE</h4>
          <p style={{ marginBottom: '1rem', lineHeight: '1.6' }}>
            This is to certify that the CYBER-INTERCEPT system was engaged in the investigation of complaint {activeScenario.id}. 
            The system successfully processed the financial vector, establishing a Layer-1 trace with an aggregated risk score of <strong>{activeScenario.overallRisk}%</strong>.
            The multi-agent consensus verdict is: <strong>{activeScenario.verdict.replace(/_/g, ' ')}</strong>.
          </p>
          <p style={{ marginBottom: '1rem', lineHeight: '1.6' }}>
            Geospatial predictive analytics identified the following ATM cashout hotspots:
          </p>
          <ul style={{ paddingLeft: '2rem', marginBottom: '1rem' }}>
            {activeScenario.predictedAtms.map((atm, i) => (
              <li key={i} style={{ marginBottom: '0.5rem' }}>
                {atm.name} - Probability: {atm.probability}% (Risk: {atm.riskScore})
              </li>
            ))}
          </ul>
        </div>

        <div style={{ marginBottom: '3rem' }}>
          <h4 style={{ fontWeight: 'bold', borderBottom: '1px solid #000', paddingBottom: '0.25rem', marginBottom: '1rem' }}>2. IMMUTABLE CRYPTOGRAPHIC AUDIT TRAIL</h4>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem', marginBottom: '1rem' }}>
            <thead>
              <tr style={{ backgroundColor: '#f0f0f0' }}>
                <th style={{ border: '1px solid #000', padding: '0.5rem', textAlign: 'left' }}>Phase</th>
                <th style={{ border: '1px solid #000', padding: '0.5rem', textAlign: 'left' }}>Timestamp (UTC)</th>
                <th style={{ border: '1px solid #000', padding: '0.5rem', textAlign: 'left' }}>Cryptographic Hash (SHA-256)</th>
              </tr>
            </thead>
            <tbody>
              <tr><td style={{ border: '1px solid #000', padding: '0.5rem' }}>OBSERVE</td><td style={{ border: '1px solid #000', padding: '0.5rem' }}>2026-08-29T10:12:05Z</td><td style={{ border: '1px solid #000', padding: '0.5rem', fontFamily: 'monospace' }}>8f4e92a...c3b1</td></tr>
              <tr><td style={{ border: '1px solid #000', padding: '0.5rem' }}>TRACE</td><td style={{ border: '1px solid #000', padding: '0.5rem' }}>2026-08-29T10:12:12Z</td><td style={{ border: '1px solid #000', padding: '0.5rem', fontFamily: 'monospace' }}>e2b51a0...9d7f</td></tr>
              <tr><td style={{ border: '1px solid #000', padding: '0.5rem' }}>PREDICT</td><td style={{ border: '1px solid #000', padding: '0.5rem' }}>2026-08-29T10:13:15Z</td><td style={{ border: '1px solid #000', padding: '0.5rem', fontFamily: 'monospace' }}>3d6e11a...7f2c</td></tr>
              <tr><td style={{ border: '1px solid #000', padding: '0.5rem' }}>INTERVENE</td><td style={{ border: '1px solid #000', padding: '0.5rem' }}>2026-08-29T10:13:30Z</td><td style={{ border: '1px solid #000', padding: '0.5rem', fontFamily: 'monospace' }}>1f8a44b...9e3d</td></tr>
            </tbody>
          </table>
          <p style={{ fontFamily: 'monospace', backgroundColor: '#f9f9f9', padding: '1rem', border: '1px solid #ccc' }}>
            <strong>FINAL MERKLE ROOT:</strong><br/>
            0x9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
          </p>
        </div>

        <div style={{ marginTop: '4rem', display: 'flex', justifyContent: 'space-between' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ width: '200px', borderBottom: '1px solid #000', marginBottom: '0.5rem' }}></div>
            <p>Digital Signature / Hash</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ width: '200px', borderBottom: '1px solid #000', marginBottom: '0.5rem' }}></div>
            <p>Signature of Authorized Officer</p>
            <p style={{ fontSize: '0.875rem' }}>Insp. Rahul Sharma, I4C</p>
          </div>
        </div>

      </div>
    </div>
    </>
  );
}
