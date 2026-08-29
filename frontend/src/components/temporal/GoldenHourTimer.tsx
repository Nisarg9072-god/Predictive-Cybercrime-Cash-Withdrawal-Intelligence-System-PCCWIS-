import { useState, useEffect } from 'react';
import { Timer, AlertTriangle, ShieldCheck } from 'lucide-react';

interface GoldenHourProps {
  isSafe: boolean;
  selectedAtm: any;
}

export function GoldenHourTimer({ isSafe, selectedAtm }: GoldenHourProps) {
  // If safe, we don't need a ticking timer
  const initialMinutes = isSafe ? 0 : 15;
  const [timeLeft, setTimeLeft] = useState(initialMinutes * 60);

  useEffect(() => {
    // Reset timer when selected ATM changes (for demo purposes)
    setTimeLeft(initialMinutes * 60);
  }, [selectedAtm, initialMinutes]);

  useEffect(() => {
    if (isSafe || timeLeft <= 0) return;
    const interval = setInterval(() => {
      setTimeLeft(prev => prev - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [timeLeft, isSafe]);

  if (isSafe) {
    return (
      <div style={{ backgroundColor: 'var(--status-safe-bg)', padding: '1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--status-safe)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--status-safe)' }}>
            <ShieldCheck size={18} /> Zero-Harm Principle Active
          </h3>
        </div>
        <p style={{ color: 'var(--status-safe)', fontSize: '0.875rem' }}>
          Legitimate transaction verified. No predictive hotspots or interventions required.
        </p>
      </div>
    );
  }

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const percentage = (timeLeft / (initialMinutes * 60)) * 100;
  
  let color = 'var(--status-safe)';
  if (percentage < 30) color = 'var(--status-critical)';
  else if (percentage < 60) color = 'var(--status-warning)';

  const currentProbability = selectedAtm ? selectedAtm.probability : 44.8;
  // Make the future expected window slightly higher to show urgency
  const expectedProbability = selectedAtm ? Math.min(99, selectedAtm.probability + 20) : 71.7;

  return (
    <div className="bg-navy-panel" style={{ padding: '1.25rem', borderRadius: 'var(--radius-md)', border: `1px solid ${color}` }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h3 style={{ fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: color }}>
          <Timer size={18} /> Golden Hour Window
        </h3>
        <span style={{ fontSize: '1.5rem', fontWeight: 'bold', color: color, fontFamily: 'var(--font-mono)' }}>
          {formatTime(timeLeft)}
        </span>
      </div>
      
      <div style={{ width: '100%', height: '8px', backgroundColor: 'var(--bg-secondary)', borderRadius: '4px', marginBottom: '1rem' }}>
        <div style={{ width: `${percentage}%`, height: '100%', backgroundColor: color, borderRadius: '4px', transition: 'width 1s linear, background-color 0.5s' }} />
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span className="text-muted" style={{ fontSize: '0.75rem' }}>Current Probability</span>
          <span style={{ fontWeight: 600, fontSize: '1.125rem' }}>{currentProbability}%</span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span className="text-muted" style={{ fontSize: '0.75rem' }}>Expected (15m window)</span>
          <span className="text-critical" style={{ fontWeight: 600, fontSize: '1.125rem' }}>{expectedProbability}%</span>
        </div>
      </div>
      
      {percentage < 30 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '1rem', color: 'var(--status-critical)', fontSize: '0.875rem', fontWeight: 500 }}>
          <AlertTriangle size={16} /> HIGH URGENCY: INTERVENTION REQUIRED
        </div>
      )}
    </div>
  );
}
