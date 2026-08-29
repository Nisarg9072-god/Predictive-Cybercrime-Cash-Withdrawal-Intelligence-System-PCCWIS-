import { useState, useEffect } from 'react';
import { Bell, Settings, Crosshair, Menu } from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';
import './Layout.css';

export function Header({ onToggleSidebar }: { onToggleSidebar: () => void }) {
  const { activeScenario } = useInvestigation();
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="top-header">
      <div className="header-left">
        <button className="icon-btn" onClick={onToggleSidebar} aria-label="Toggle Sidebar">
          <Menu size={20} />
        </button>
        <div className="header-brand">
          <span className="header-brand-title">MINISTRY OF HOME AFFAIRS</span>
          <span className="header-brand-subtitle">INDIAN CYBER CRIME COORDINATION CENTRE (I4C)</span>
        </div>
        
        <div className="header-badges">

          {activeScenario && (
            <div className="header-scenario-badge">
              <Crosshair size={14} /> {activeScenario.id}
            </div>
          )}
        </div>
      </div>
      
      <div className="header-right">
        <div className="header-datetime">
          <span className="header-time">
            {time.toLocaleTimeString('en-US', { hour12: false })} IST
          </span>
          <span className="header-date">
            {time.toLocaleDateString('en-US', { day: '2-digit', month: 'short', year: 'numeric' })}
          </span>
        </div>

        <div className="header-actions">
          <button className="icon-btn">
            <Bell size={18} />
            {activeScenario && <span className="notification-dot"></span>}
          </button>
          <button className="icon-btn">
            <Settings size={18} />
          </button>
        </div>
        
        <div className="header-user">
          <div className="avatar">IO</div>
          <div className="user-info">
            <span className="user-name">Insp. Rahul Sharma</span>
            <span className="user-role">I4C Lead Investigator</span>
          </div>
        </div>
      </div>
    </header>
  );
}
