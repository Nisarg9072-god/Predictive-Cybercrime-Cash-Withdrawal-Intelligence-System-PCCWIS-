import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Shield, AlertTriangle, ChevronRight } from 'lucide-react';
import './LandingPage.css';

export function LandingPage() {
  const [currentSlide, setCurrentSlide] = useState(0);

  const slides = [
    {
      title: 'AI-POWERED CYBERCRIME PREDICTION',
      subtitle: 'Securing India’s Digital Future',
      desc: 'Empowering a safer and digitally resilient India through Artificial Intelligence and Machine Learning. Our platform analyzes cybercrime patterns, identifies emerging threats, and delivers predictive insights to strengthen cybersecurity and protect citizens in the digital era.',
      btn: 'EXPLORE PLATFORM',
      link: '/command-center',
      image: '/src/assets/images/amrit_mahotsav_banner_80_tall.png',
      slideClass: 'carousel-slide-independence'
    },
    {
      title: 'CYBER-INTERCEPT',
      subtitle: 'AI-Assisted Cybercrime Intelligence',
      desc: 'Transforming cybercrime complaints into actionable intelligence through financial transaction tracing, risk analysis and geospatial investigation.',
      btn: 'EXPLORE PLATFORM',
      link: '/command-center',
      image: '/src/assets/images/carousel_1.jpg'
    },
    {
      title: 'PREDICTIVE GEO-SPATIAL INTELLIGENCE',
      subtitle: 'Digital Evidence Processing',
      desc: 'Identify high-risk geographical locations and visualize predicted ATM cash-out hotspots.',
      btn: 'INTELLIGENCE MAP',
      link: '/intelligence-map',
      image: '/src/assets/images/carousel_3.jpg'
    }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 5000);
    return () => clearInterval(timer);
  }, [slides.length]);

  return (
    <div className="landing-page-root">

      {/* Government Strip */}
      <div className="gov-strip" style={{ backgroundColor: '#2196F3', padding: '0.4rem 2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', paddingRight: '0.75rem', borderRight: '1px solid rgba(255, 255, 255, 0.6)' }}>
            <span style={{ fontWeight: 700, fontSize: '0.85rem' }}>भारत सरकार</span>
            <span style={{ fontSize: '0.7rem', fontWeight: 600 }}>GOVERNMENT OF INDIA</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', paddingLeft: '0.75rem' }}>
            <span style={{ fontWeight: 700, fontSize: '0.85rem' }}>गृह मंत्रालय</span>
            <span style={{ fontSize: '0.7rem', fontWeight: 600 }}>MINISTRY OF HOME AFFAIRS</span>
          </div>
        </div>
      </div>

      {/* Brand Header */}
      <header className="gov-brand-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <img src="/src/assets/images/i4c_logo.png" alt="I4C Logo" style={{ height: '75px', objectFit: 'contain' }} />
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', borderLeft: '2px solid var(--gov-border)', paddingLeft: '1.5rem' }}>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--gov-blue-dark)', margin: 0, letterSpacing: '0.5px' }}>
              સાયબર ક્રાઈમ ઈન્ટેલિજન્સ અને પ્રિડિક્ટિવ ઈન્વેસ્ટિગેશન પ્લેટફોર્મ
            </h1>
            <h2 style={{ fontSize: '0.9rem', color: 'var(--gov-text-muted)', margin: '0.25rem 0 0 0', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Cybercrime Intelligence & Predictive Investigation Platform
            </h2>
          </div>
        </div>

        {/* Independence Day Banner */}
        <div style={{ display: 'flex', alignItems: 'center', marginLeft: 'auto' }}>
          <img src="/src/assets/images/amrit_mahotsav_80.jpg" alt="Azadi Ka Amrit Mahotsav" style={{ height: '70px', objectFit: 'contain' }} />
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
            LOGIN
          </Link>
          <Link to="/complaints/new" style={{ backgroundColor: 'var(--gov-red)', color: 'white', padding: '1rem 1.5rem', fontWeight: 600, fontSize: '0.875rem', textDecoration: 'none' }}>
            REGISTER COMPLAINT
          </Link>
        </div>
      </nav>

      {/* Carousel */}
      <div className="carousel-container">
        {slides.map((slide, index) => (
          <div key={index} className={`carousel-slide ${index === currentSlide ? 'active' : ''} ${slide.slideClass || ''}`} style={{
            backgroundImage: `url('${slide.image}')`
          }}>
            <div className="carousel-overlay"></div>
            <div className="carousel-content">
              <h2 style={{ fontSize: '1.5rem', fontWeight: 400, marginBottom: '1.5rem', maxWidth: '800px', lineHeight: 1.1 }}>
                {slide.title}
              </h2>
              <h3 style={{ fontSize: '1.5rem', fontWeight: 400, marginBottom: '1.5rem', color: '#B3E5FC' }}>
                {slide.subtitle}
              </h3>
              <p style={{ fontSize: '1.125rem', marginBottom: '2.5rem', maxWidth: '600px', lineHeight: 1.6, color: '#E1F5FE' }}>
                {slide.desc}
              </p>
              <Link to={slide.link} className="gov-btn-primary">
                {slide.btn} <ChevronRight size={18} />
              </Link>
            </div>
          </div>
        ))}
        <div style={{ position: 'absolute', bottom: '20px', left: '0', width: '100%', display: 'flex', justifyContent: 'center', gap: '8px', zIndex: 10 }}>
          {slides.map((_, i) => (
            <button key={i} onClick={() => setCurrentSlide(i)} style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: i === currentSlide ? 'white' : 'rgba(255,255,255,0.4)', border: 'none', cursor: 'pointer' }} aria-label={`Go to slide ${i + 1}`} />
          ))}
        </div>
      </div>

      {/* Report Cybercrime CTA */}
      <section style={{ backgroundColor: 'var(--gov-white)', borderBottom: '1px solid var(--gov-border)' }}>
        <div className="gov-section" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '3rem 2rem' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1.5rem' }}>
            <AlertTriangle color="var(--gov-red)" size={48} />
            <div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--gov-text-dark)', marginBottom: '0.5rem' }}>REPORT CYBERCRIME</h2>
              <p style={{ maxWidth: '600px', fontSize: '1rem', color: 'var(--gov-text-muted)' }}>
                Have you encountered a cybercrime incident? Report the incident through the CYBER-INTERCEPT complaint intake system and provide the relevant incident details for investigation.
              </p>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <Link to="/complaints/new" className="gov-btn-danger">
              REGISTER COMPLAINT
            </Link>
            <Link to="/login" className="gov-btn-outline" style={{ color: 'var(--gov-blue)', borderColor: 'var(--gov-blue)' }}>
              TRACK COMPLAINT
            </Link>
          </div>
        </div>
      </section>

      {/* Alternating Content Layout 1 */}
      <section style={{ backgroundColor: 'var(--gov-bg)', borderBottom: '1px solid var(--gov-border)' }}>
        <div className="gov-section" style={{ display: 'flex', alignItems: 'center', gap: '4rem', padding: '4rem 2rem' }}>
          <div style={{ flex: 1 }}>
            <img src="/src/assets/images/content_1.jpg" alt="Cybercrime Intelligence" style={{ width: '100%', borderRadius: '4px', boxShadow: '0 10px 25px rgba(0,0,0,0.1)' }} />
          </div>
          <div style={{ flex: 1 }}>
            <h2 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--gov-blue-dark)', marginBottom: '1rem', borderBottom: '3px solid var(--gov-blue)', paddingBottom: '0.5rem', display: 'inline-block' }}>
              CYBERCRIME INTELLIGENCE
            </h2>
            <p style={{ fontSize: '1.125rem', color: 'var(--gov-text-muted)', marginBottom: '2rem', lineHeight: 1.6 }}>
              Analyze reported cybercrime incidents and identify relationships between complaints, financial entities and suspicious activity using a centralized analytical workspace.
            </p>
            <Link to="/command-center" className="gov-btn-primary">EXPLORE <ChevronRight size={16} /></Link>
          </div>
        </div>
      </section>

      {/* Alternating Content Layout 2 */}
      <section style={{ backgroundColor: 'var(--gov-white)', borderBottom: '1px solid var(--gov-border)' }}>
        <div className="gov-section" style={{ display: 'flex', alignItems: 'center', gap: '4rem', padding: '4rem 2rem' }}>
          <div style={{ flex: 1 }}>
            <h2 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--gov-blue-dark)', marginBottom: '1rem', borderBottom: '3px solid var(--gov-blue)', paddingBottom: '0.5rem', display: 'inline-block' }}>
              FINANCIAL TRANSACTION TRACING
            </h2>
            <p style={{ fontSize: '1.125rem', color: 'var(--gov-text-muted)', marginBottom: '2rem', lineHeight: 1.6 }}>
              Trace suspicious transaction flows across multiple layers to identify potential mule accounts and cash-out patterns. Visualize multi-hop banking relationships for immediate intervention.
            </p>
            <Link to="/investigation" className="gov-btn-primary">VIEW INVESTIGATION <ChevronRight size={16} /></Link>
          </div>
          <div style={{ flex: 1 }}>
            <img src="/src/assets/images/content_2.jpg" alt="Financial Transaction Tracing" style={{ width: '100%', borderRadius: '4px', boxShadow: '0 10px 25px rgba(0,0,0,0.1)' }} />
          </div>
        </div>
      </section>

      {/* Alternating Content Layout 3 */}
      <section style={{ backgroundColor: 'var(--gov-bg)', borderBottom: '1px solid var(--gov-border)' }}>
        <div className="gov-section" style={{ display: 'flex', alignItems: 'center', gap: '4rem', padding: '4rem 2rem' }}>
          <div style={{ flex: 1 }}>
            <img src="/src/assets/images/content_3.jpg" alt="Predictive GIS Intelligence" style={{ width: '100%', borderRadius: '4px', boxShadow: '0 10px 25px rgba(0,0,0,0.1)' }} />
          </div>
          <div style={{ flex: 1 }}>
            <h2 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--gov-blue-dark)', marginBottom: '1rem', borderBottom: '3px solid var(--gov-blue)', paddingBottom: '0.5rem', display: 'inline-block' }}>
              PREDICTIVE GIS INTELLIGENCE
            </h2>
            <p style={{ fontSize: '1.125rem', color: 'var(--gov-text-muted)', marginBottom: '2rem', lineHeight: 1.6 }}>
              Identify high-risk geographical locations and visualize predicted ATM cash-out hotspots. Deploy law enforcement resources efficiently based on real-time spatial analysis.
            </p>
            <Link to="/reports" className="gov-btn-primary">INTELLIGENCE MAP <ChevronRight size={16} /></Link>
          </div>
        </div>
      </section>

      {/* Process Section */}
      <section style={{ backgroundColor: 'var(--gov-white)', borderBottom: '1px solid var(--gov-border)' }}>
        <div className="gov-section">
          <h2 className="gov-section-title">HOW CYBER-INTERCEPT WORKS</h2>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginTop: '3rem' }}>
            {[
              { id: '01', title: 'COMPLAINT', desc: 'Cybercrime complaint enters the investigation workflow.' },
              { id: '02', title: 'ANALYZE', desc: 'Relevant financial and digital entities are identified.' },
              { id: '03', title: 'TRACE', desc: 'Transaction relationships are analyzed across multiple hops.' },
              { id: '04', title: 'PREDICT', desc: 'Potential high-risk locations are identified through geospatial intelligence.' },
              { id: '05', title: 'INVESTIGATE', desc: 'Analysts review the complete intelligence picture.' },
              { id: '06', title: 'INTERVENE', desc: 'Recommended intervention actions are presented.' }
            ].map((step, i) => (
              <div key={i} style={{ flex: '1 1 150px', textAlign: 'center', position: 'relative' }}>
                <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: '48px', height: '48px', backgroundColor: 'var(--gov-blue)', color: 'white', borderRadius: '50%', fontWeight: 700, fontSize: '1.25rem', marginBottom: '1rem' }}>
                  {step.id}
                </div>
                <h4 style={{ color: 'var(--gov-blue-dark)', fontSize: '0.875rem', fontWeight: 700, marginBottom: '0.5rem' }}>{step.title}</h4>
                <p style={{ fontSize: '0.75rem', color: 'var(--gov-text-muted)' }}>{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

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
          <Link to="/">HOME</Link> | <Link to="/about">ABOUT</Link> | <Link to="/investigation">INVESTIGATION</Link> | <Link to="/reports">REPORTS</Link> | <Link to="/login">CONTACT</Link>
        </div>
        <p style={{ fontSize: '0.75rem', color: '#666', borderTop: '1px solid #333', paddingTop: '1.5rem', maxWidth: '600px', margin: '0 auto' }}>
          © 2026 CYBER-INTERCEPT. All Rights Reserved. <br />
          This platform is a demonstration/prototype environment.
        </p>
      </footer>
    </div>
  );
}
