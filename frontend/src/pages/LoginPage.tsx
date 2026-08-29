import { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Shield, Lock, Key, AlertTriangle, ArrowLeft } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import './LandingPage.css'; // Reusing global/landing fonts and tokens

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);

  const queryParams = new URLSearchParams(location.search);
  const redirectUrl = queryParams.get('redirect') || '/command-center';

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      login();
      navigate(redirectUrl);
    }, 800);
  };

  return (
    <div className="landing-page-root" style={{
      width: '100vw',
      minHeight: '100dvh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative',
      overflow: 'hidden',
      boxSizing: 'border-box',
      padding: '1rem'
    }}>

      {/* Blurred Background with Subtle Navy/Cyan Tint */}
      <div style={{
        position: 'absolute',
        inset: 0,
        backgroundImage: `url('/src/assets/images/carousel_1.jpg')`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        filter: 'blur(12px)',
        transform: 'scale(1.05)',
        zIndex: 1
      }} />
      <div style={{
        position: 'absolute',
        inset: 0,
        background: 'linear-gradient(135deg, rgba(6, 29, 76, 0.85) 0%, rgba(11, 41, 91, 0.75) 100%)',
        zIndex: 2
      }} />

      {/* Authentication Card Wrapper */}
      <div style={{
        width: '100%',
        maxWidth: '440px',
        position: 'relative',
        zIndex: 10,
        display: 'flex',
        flexDirection: 'column',
        maxHeight: '100%'
      }}>

        {/* Back Link */}
        <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
          <Link to="/" style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            color: '#B3E5FC',
            textDecoration: 'none',
            fontWeight: 600,
            fontSize: '0.875rem',
            transition: 'color 0.2s ease'
          }}>
            <ArrowLeft size={16} /> Back to Portal
          </Link>
        </div>

        {/* The Card */}
        <div style={{
          backgroundColor: 'rgba(255, 255, 255, 0.98)',
          border: '1px solid rgba(135, 206, 250, 0.3)',
          borderRadius: '12px',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          maxHeight: 'calc(100dvh - 6rem)'
        }}>

          <div style={{
            backgroundColor: 'var(--gov-blue-dark)',
            padding: '1.25rem',
            textAlign: 'center',
            color: 'var(--gov-white)',
            borderBottom: '3px solid var(--gov-blue)'
          }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: '0.5rem' }}>
              <Shield color="#81D4FA" size={36} />
            </div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '0.5px', marginBottom: '0.25rem', margin: 0 }}>CYBER-INTERCEPT</h1>
            <p style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1.5px', color: '#B3E5FC', margin: 0, fontWeight: 600 }}>Login</p>
          </div>

          <form onSubmit={handleLogin} style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 0.75rem', backgroundColor: '#FFF5F5', border: '1px solid #FED7D7', borderRadius: '6px', color: '#C53030', fontSize: '0.7rem', fontWeight: 700 }}>
              <AlertTriangle size={14} style={{ flexShrink: 0 }} />
              UNAUTHORIZED ACCESS IS PROHIBITED
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 700, color: 'var(--gov-blue-dark)', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Officer ID / Username
              </label>
              <div style={{ position: 'relative' }}>
                <Lock size={14} color="#94A3B8" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                <input
                  type="text"
                  defaultValue="IO-7729-NCRP"
                  style={{
                    width: '100%',
                    padding: '0.65rem 0.75rem 0.65rem 2.25rem',
                    border: '1px solid #CBD5E1',
                    borderRadius: '6px',
                    fontSize: '0.9rem',
                    boxSizing: 'border-box',
                    color: '#334155',
                    fontWeight: 500,
                    outline: 'none',
                    transition: 'border-color 0.2s ease'
                  }}
                  onFocus={(e) => e.target.style.borderColor = 'var(--gov-blue)'}
                  onBlur={(e) => e.target.style.borderColor = '#CBD5E1'}
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.7rem', fontWeight: 700, color: 'var(--gov-blue-dark)', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Password / Secure Token
              </label>
              <div style={{ position: 'relative' }}>
                <Key size={14} color="#94A3B8" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                <input
                  type="password"
                  defaultValue="********"
                  style={{
                    width: '100%',
                    padding: '0.65rem 0.75rem 0.65rem 2.25rem',
                    border: '1px solid #CBD5E1',
                    borderRadius: '6px',
                    fontSize: '0.9rem',
                    boxSizing: 'border-box',
                    color: '#334155',
                    fontWeight: 500,
                    outline: 'none',
                    transition: 'border-color 0.2s ease'
                  }}
                  onFocus={(e) => e.target.style.borderColor = 'var(--gov-blue)'}
                  onBlur={(e) => e.target.style.borderColor = '#CBD5E1'}
                />
              </div>
            </div>

            <button
              type="submit"
              style={{
                marginTop: '0.5rem',
                justifyContent: 'center',
                padding: '0.75rem',
                opacity: loading ? 0.7 : 1,
                width: '100%',
                backgroundColor: 'var(--gov-blue)',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '0.85rem',
                fontWeight: 700,
                letterSpacing: '0.5px',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                transition: 'background-color 0.2s ease'
              }}
              onMouseOver={(e) => !loading && (e.currentTarget.style.backgroundColor = 'var(--gov-blue-dark)')}
              onMouseOut={(e) => !loading && (e.currentTarget.style.backgroundColor = 'var(--gov-blue)')}
              disabled={loading}
            >
              <Shield size={16} /> {loading ? 'AUTHENTICATING...' : 'SECURE LOGIN'}
            </button>

            <div style={{ textAlign: 'center', marginTop: '0.5rem', borderTop: '1px solid #E2E8F0', paddingTop: '1rem' }}>
              <p style={{ margin: 0, fontSize: '0.8rem', color: '#64748B', fontWeight: 500 }}>
                Don't have an account?{' '}
                <Link to="/register" style={{ color: 'var(--gov-blue)', fontWeight: 700, textDecoration: 'none' }}>
                  Register
                </Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
