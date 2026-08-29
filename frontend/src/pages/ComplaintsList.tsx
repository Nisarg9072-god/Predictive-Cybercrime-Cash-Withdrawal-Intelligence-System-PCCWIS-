import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Filter, Search, ChevronRight } from 'lucide-react';
import { useInvestigation } from '../context/InvestigationContext';

export function ComplaintsList() {
  const navigate = useNavigate();
  const { loadScenario, mockComplaints } = useInvestigation();
  const [filter, setFilter] = useState('ALL');
  const [search, setSearch] = useState('');

  const complaints = mockComplaints.map(s => ({
    id: s.id,
    title: s.title,
    date: s.complaintDetails?.dateReported || '2026-08-29 09:14 IST',
    amount: s.complaintDetails?.amountLost || (s.title.includes('Digital Arrest') ? '₹45,00,000' : '₹1,20,000'),
    category: s.title.includes('Digital Arrest') ? 'Impersonation' : 'Financial Fraud',
    risk: s.riskLevel,
    state: s.complaintDetails?.location || s.title.split(' ')[0],
    status: s.verdict === 'LEGITIMATE_TRANSACTION_VERIFIED_CLEAR' ? 'CLEARED' : 'PENDING'
  }));

  const filteredComplaints = complaints.filter(c => {
    if (filter !== 'ALL' && c.risk !== filter) return false;
    if (search && !c.id.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const handleOpen = async (id: string) => {
    await loadScenario(id);
    navigate('/command-center');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '1.5rem' }}>
      
      <div className="bg-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
            <FileText className="text-primary" /> Active Complaints (NCRP Stream)
          </h1>
          <p className="text-muted">Live synchronization with National Cyber Crime Reporting Portal</p>
        </div>
        
        <button onClick={() => navigate('/complaints/new')} style={{ padding: '0.75rem 1.5rem', backgroundColor: 'var(--primary-color)', color: '#000', borderRadius: 'var(--radius-sm)', fontWeight: 700, fontSize: '0.875rem' }}>
          + MANUAL FIR INTAKE
        </button>
      </div>

      <div className="bg-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        
        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--border-strong)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: 'var(--bg-primary)' }}>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <Filter size={16} className="text-muted" />
            <select value={filter} onChange={e => setFilter(e.target.value)} style={{ padding: '0.25rem', backgroundColor: 'transparent', border: 'none', color: 'var(--text-primary)', outline: 'none', fontWeight: 600 }}>
              <option value="ALL">ALL RISK LEVELS</option>
              <option value="CRITICAL">CRITICAL RISK</option>
              <option value="HIGH">HIGH RISK</option>
            </select>
          </div>
          
          <div style={{ position: 'relative' }}>
            <Search size={14} className="text-muted" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
            <input 
              type="text" 
              placeholder="Search Ack No..." 
              value={search}
              onChange={e => setSearch(e.target.value)}
              style={{ padding: '0.4rem 1rem 0.4rem 2rem', width: '200px' }} 
            />
          </div>
        </div>

        <div style={{ overflowY: 'auto', flex: 1 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead style={{ position: 'sticky', top: 0, backgroundColor: 'var(--bg-panel)', zIndex: 1 }}>
              <tr style={{ borderBottom: '2px solid var(--border-strong)', textAlign: 'left', color: 'var(--text-muted)' }}>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.75rem' }}>Ack ID</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.75rem' }}>Reported</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.75rem' }}>Category</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.75rem' }}>Location</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.75rem' }}>Amount</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.75rem' }}>Risk Target</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.75rem', textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredComplaints.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    No complaints match your filters.
                  </td>
                </tr>
              ) : (
                filteredComplaints.map(c => (
                  <tr key={c.id} style={{ borderBottom: '1px solid var(--border-subtle)', transition: 'background 0.2s' }} onMouseOver={e => e.currentTarget.style.backgroundColor = 'var(--bg-panel-hover)'} onMouseOut={e => e.currentTarget.style.backgroundColor = 'transparent'}>
                    <td style={{ padding: '1rem 1.5rem', fontWeight: 600, fontFamily: 'var(--font-mono)', color: 'var(--primary-color)' }}>{c.id}</td>
                    <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>{c.date}</td>
                    <td style={{ padding: '1rem 1.5rem' }}>{c.category}</td>
                    <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>{c.state}</td>
                    <td style={{ padding: '1rem 1.5rem', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{c.amount}</td>
                    <td style={{ padding: '1rem 1.5rem' }}>
                      <span className={`text-${c.risk === 'CRITICAL' ? 'critical' : c.risk === 'HIGH' ? 'warning' : 'safe'}`} style={{ fontWeight: 700, fontSize: '0.75rem', padding: '0.25rem 0.5rem', border: `1px solid var(--status-${c.risk === 'CRITICAL' ? 'critical' : c.risk === 'HIGH' ? 'warning' : 'safe'})`, borderRadius: 'var(--radius-sm)' }}>
                        {c.risk}
                      </span>
                    </td>
                    <td style={{ padding: '1rem 1.5rem', textAlign: 'right' }}>
                      <button onClick={() => handleOpen(c.id)} style={{ padding: '0.4rem 1rem', backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-strong)', color: 'var(--text-primary)', borderRadius: 'var(--radius-sm)', fontSize: '0.75rem', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        Open <ChevronRight size={14} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
