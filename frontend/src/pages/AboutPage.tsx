import { Shield, ArrowRight, ShieldCheck, Layers, Map, Network } from 'lucide-react';
import { Link } from 'react-router-dom';
import './LandingPage.css'; // Reuse the government theme CSS

export function AboutPage() {
  return (
    <div className="landing-page-root">
      
      {/* Government Strip */}
      <div className="gov-strip">
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span>भारत सरकार | GOVERNMENT OF INDIA</span>
          <span style={{ opacity: 0.5 }}>|</span>
          <span>गृह मंत्रालय | MINISTRY OF HOME AFFAIRS</span>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span>English</span>
          <span style={{ opacity: 0.5 }}>|</span>
          <span>A- A A+</span>
        </div>
      </div>

      {/* Brand Header */}
      <header className="gov-brand-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Shield color="var(--gov-blue)" size={48} />
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--gov-blue-dark)', margin: 0, letterSpacing: '0.5px' }}>
              CYBER-INTERCEPT
            </h1>
            <p style={{ fontSize: '0.875rem', color: 'var(--gov-text-muted)', margin: '0.25rem 0 0 0', fontWeight: 500 }}>
              Cybercrime Intelligence & Predictive Investigation Platform
            </p>
          </div>
        </div>
        
        {/* Independence Day Banner */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '0.5rem 1rem', border: '1px solid var(--gov-border)', borderRadius: '4px', backgroundColor: '#fafafa' }}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2px' }}>
            <div style={{ width: '40px', height: '8px', backgroundColor: '#FF9933' }}></div>
            <div style={{ width: '40px', height: '8px', backgroundColor: '#FFFFFF', borderLeft: '1px solid #ccc', borderRight: '1px solid #ccc' }}></div>
            <div style={{ width: '40px', height: '8px', backgroundColor: '#138808' }}></div>
          </div>
          <div>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--gov-blue-dark)', lineHeight: 1 }}>80</div>
            <div style={{ fontSize: '0.65rem', fontWeight: 600, color: 'var(--gov-text-muted)', textTransform: 'uppercase' }}>Years of Independence</div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="gov-nav">
        <div className="gov-nav-links">
          <Link to="/">HOME</Link>
          <Link to="/about">ABOUT</Link>
          <Link to="/investigation">INVESTIGATION</Link>
          <Link to="/reports">REPORTS</Link>
        </div>
        <div style={{ display: 'flex' }}>
          <Link to="/login" style={{ backgroundColor: 'rgba(0,0,0,0.2)', color: 'white', padding: '1rem 1.5rem', fontWeight: 600, fontSize: '0.875rem', textDecoration: 'none' }}>
            ANALYST LOGIN
          </Link>
          <Link to="/complaints/new" style={{ backgroundColor: 'var(--gov-red)', color: 'white', padding: '1rem 1.5rem', fontWeight: 600, fontSize: '0.875rem', textDecoration: 'none' }}>
            REGISTER COMPLAINT
          </Link>
        </div>
      </nav>

      {/* About Content */}
      <main style={{ flex: 1, backgroundColor: 'var(--gov-bg)', padding: '4rem 2rem' }}>
        <div style={{ maxWidth: '1000px', margin: '0 auto', backgroundColor: 'var(--gov-white)', border: '1px solid var(--gov-border)', borderTop: '4px solid var(--gov-blue)', borderRadius: '4px', padding: '3rem', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
          
          <h1 style={{ fontSize: '2.5rem', color: 'var(--gov-blue-dark)', marginBottom: '1.5rem', borderBottom: '1px solid var(--gov-border)', paddingBottom: '1rem' }}>
            About CYBER-INTERCEPT
          </h1>
          
          <div style={{ fontSize: '1.125rem', color: 'var(--gov-text-dark)', lineHeight: 1.8, marginBottom: '3rem' }}>
            <p style={{ marginBottom: '1.5rem' }}>
              <strong>CYBER-INTERCEPT</strong> is an advanced, AI-assisted cybercrime intelligence and predictive investigation platform designed to support law enforcement agencies in the structured analysis of cybercrime complaints.
            </p>
            <p>
              Developed as a centralized command center, the platform transforms raw incident reports into actionable intelligence by analyzing financial transaction networks, detecting mule accounts, and identifying geospatial risk indicators across multiple investigative hops.
            </p>
          </div>

          <h2 style={{ fontSize: '1.5rem', color: 'var(--gov-blue)', marginBottom: '1.5rem' }}>Platform Capabilities</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '2rem', marginBottom: '4rem' }}>
            
            <div style={{ display: 'flex', gap: '1rem' }}>
              <Network color="var(--gov-blue)" size={32} style={{ flexShrink: 0 }} />
              <div>
                <h4 style={{ fontWeight: 700, marginBottom: '0.5rem', color: 'var(--gov-text-dark)' }}>Financial Transaction Tracing</h4>
                <p style={{ fontSize: '0.875rem' }}>Visualize complex money flows and multi-hop transactions to uncover suspicious financial networks.</p>
              </div>
            </div>
            
            <div style={{ display: 'flex', gap: '1rem' }}>
              <Map color="var(--gov-blue)" size={32} style={{ flexShrink: 0 }} />
              <div>
                <h4 style={{ fontWeight: 700, marginBottom: '0.5rem', color: 'var(--gov-text-dark)' }}>Geospatial Risk Intelligence</h4>
                <p style={{ fontSize: '0.875rem' }}>Predict and visualize potential ATM cash-out hotspots utilizing historical financial footprints and geographical data.</p>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '1rem' }}>
              <Layers color="var(--gov-blue)" size={32} style={{ flexShrink: 0 }} />
              <div>
                <h4 style={{ fontWeight: 700, marginBottom: '0.5rem', color: 'var(--gov-text-dark)' }}>Investigation Support</h4>
                <p style={{ fontSize: '0.875rem' }}>Provide analysts with structured workflows, automated risk scoring, and evidence traceability.</p>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '1rem' }}>
              <ShieldCheck color="var(--gov-blue)" size={32} style={{ flexShrink: 0 }} />
              <div>
                <h4 style={{ fontWeight: 700, marginBottom: '0.5rem', color: 'var(--gov-text-dark)' }}>Intervention Workflows</h4>
                <p style={{ fontSize: '0.875rem' }}>Simulate bank-lien triggers and generate court-admissible audit trails for Section 65B compliance.</p>
              </div>
            </div>

          </div>

          <div style={{ backgroundColor: '#FFF3E0', borderLeft: '4px solid #FF9800', padding: '1.5rem', marginBottom: '2rem' }}>
            <h4 style={{ color: '#E65100', marginBottom: '0.5rem', fontSize: '1rem', fontWeight: 700 }}>DEMO / SIMULATION DISCLAIMER</h4>
            <p style={{ fontSize: '0.875rem', color: '#5D4037', margin: 0 }}>
              This platform currently operates as a demonstration and prototype environment designed for the Smart India Hackathon. It utilizes simulated mock data and frontend authentication for demonstration purposes. It is not currently deployed to process live national cybercrime data.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '1rem', marginTop: '3rem' }}>
            <Link to="/login" className="gov-btn-primary">
              ANALYST LOGIN <ArrowRight size={16} />
            </Link>
            <Link to="/complaints/new" className="gov-btn-danger">
              REGISTER COMPLAINT <ArrowRight size={16} />
            </Link>
          </div>

        </div>
      </main>

      {/* Footer */}
      <footer className="gov-footer">
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1.5rem' }}>
          <Shield color="var(--gov-white)" size={32} />
        </div>
        <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--gov-white)', letterSpacing: '1px' }}>
          CYBER-INTERCEPT
        </h3>
        <p style={{ color: '#999', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
          AI-Assisted Cybercrime Intelligence & Predictive Investigation Platform
        </p>
        <div style={{ marginBottom: '2rem', fontSize: '0.875rem' }}>
          <Link to="/">HOME</Link> | <Link to="/about">ABOUT</Link> | <Link to="/investigation">INVESTIGATION</Link> | <Link to="/reports">REPORTS</Link> | <Link to="/login">ANALYST LOGIN</Link>
        </div>
        <p style={{ fontSize: '0.75rem', color: '#666', borderTop: '1px solid #333', paddingTop: '1.5rem', maxWidth: '600px', margin: '0 auto' }}>
          © 2026 CYBER-INTERCEPT. All Rights Reserved. <br />
          This platform is a demonstration/prototype environment.
        </p>
      </footer>

    </div>
  );
}
