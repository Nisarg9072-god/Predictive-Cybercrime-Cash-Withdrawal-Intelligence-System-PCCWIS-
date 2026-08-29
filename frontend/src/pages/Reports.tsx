import { FileBarChart, TrendingUp, TrendingDown, Target, Shield } from 'lucide-react';

export function Reports() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '1.5rem' }}>
      
      <div className="bg-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
            <FileBarChart className="text-primary" /> Intelligence Reports
          </h1>
          <p className="text-muted">Global operations summary and predictive effectiveness metrics</p>
        </div>
        <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          Last 24 Hours
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem' }}>
        <div className="bg-panel" style={{ padding: '1.5rem' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Complaints Processed</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
            <span style={{ fontSize: '2rem', fontWeight: 700 }}>2,481</span>
            <span className="text-safe" style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center' }}><TrendingUp size={12} /> 12%</span>
          </div>
        </div>
        <div className="bg-panel" style={{ padding: '1.5rem' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Hotspots Predicted</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
            <span style={{ fontSize: '2rem', fontWeight: 700 }}>142</span>
            <span className="text-safe" style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center' }}><TrendingUp size={12} /> 5%</span>
          </div>
        </div>
        <div className="bg-panel" style={{ padding: '1.5rem' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Funds Frozen (₹)</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
            <span style={{ fontSize: '2rem', fontWeight: 700 }}>18.4M</span>
            <span className="text-safe" style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center' }}><TrendingUp size={12} /> 22%</span>
          </div>
        </div>
        <div className="bg-panel" style={{ padding: '1.5rem' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>False Positives (Zero-Harm)</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
            <span style={{ fontSize: '2rem', fontWeight: 700 }}>0.01%</span>
            <span className="text-safe" style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center' }}><TrendingDown size={12} /> 0.05%</span>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', flex: 1 }}>
        <div className="bg-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
            <Target size={16} className="text-primary" /> State-wise High Risk Predictions
          </h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', flex: 1 }}>
            {[
              { state: 'Delhi NCR', val: 45, pct: '100%' },
              { state: 'Karnataka', val: 32, pct: '71%' },
              { state: 'Maharashtra', val: 28, pct: '62%' },
              { state: 'Rajasthan', val: 18, pct: '40%' },
              { state: 'West Bengal', val: 12, pct: '26%' },
            ].map(row => (
              <div key={row.state}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                  <span>{row.state}</span>
                  <span style={{ fontWeight: 600 }}>{row.val} Interventions</span>
                </div>
                <div style={{ height: '6px', backgroundColor: 'var(--bg-primary)', borderRadius: '3px' }}>
                  <div style={{ height: '100%', width: row.pct, backgroundColor: 'var(--primary-color)', borderRadius: '3px' }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
            <Shield size={16} className="text-primary" /> Intervention Efficacy
          </h2>
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ width: '150px', height: '150px', borderRadius: '50%', border: '16px solid var(--primary-color)', borderRightColor: 'var(--bg-primary)', margin: '0 auto 1.5rem auto', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>84%</span>
              </div>
              <p>Successful Intercept Rate within Golden Hour</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
