import { NavLink } from 'react-router-dom';
import { 
  Shield, Search, Map, FolderOpen, 
  FileText, ShieldAlert, FileBarChart, HardDrive, LogOut, Radar, FilePlus, Scale
} from 'lucide-react';
import { useInvestigation } from '../../context/InvestigationContext';
import './Layout.css';

interface SidebarProps {
  isCollapsed: boolean;
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isCollapsed, isOpen, onClose }: SidebarProps) {
  const { isDemoMode } = useInvestigation();

  const commandNavItems = [
    { path: '/command-center', label: 'Command Center', icon: Radar },
    { path: '/alerts', label: 'Live Alerts', icon: ShieldAlert },
    { path: '/intelligence-map', label: 'Intelligence Map', icon: Map },
  ];

  const investigationNavItems = [
    { path: '/complaints', label: 'Complaints', icon: FileText },
    { path: '/complaints/new', label: 'New Complaint', icon: FilePlus },
    { path: '/investigation', label: 'Investigation', icon: Search },
  ];

  const interventionsNavItems = [
    { path: '/dossier', label: 'Legal Dossier', icon: Scale },
    { path: '/audit', label: 'Audit Trail', icon: FolderOpen },
  ];

  const reportsNavItems = [
    { path: '/reports', label: 'Intelligence Reports', icon: FileBarChart },
    { path: '/system', label: 'System Monitoring', icon: HardDrive },
  ];

  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''} ${isOpen ? 'mobile-open' : ''}`}>
      <div className="sidebar-header">
        <Shield className="sidebar-logo" size={24} />
        <span className="sidebar-title">CYBER-INTERCEPT</span>
      </div>
      
      <nav className="sidebar-nav">
        <div className="nav-section"><span>Command</span></div>
        {commandNavItems.map((item) => (
          <NavLink key={item.path} to={item.path} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title={isCollapsed ? item.label : undefined} onClick={onClose}>
            <item.icon size={16} />
            <span>{item.label}</span>
          </NavLink>
        ))}

        <div className="nav-section"><span>Investigation</span></div>
        {investigationNavItems.map((item) => (
          <NavLink key={item.path} to={item.path} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title={isCollapsed ? item.label : undefined} onClick={onClose}>
            <item.icon size={16} />
            <span>{item.label}</span>
          </NavLink>
        ))}

        <div className="nav-section"><span>Interventions</span></div>
        {interventionsNavItems.map((item) => (
          <NavLink key={item.path} to={item.path} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title={isCollapsed ? item.label : undefined} onClick={onClose}>
            <item.icon size={16} />
            <span>{item.label}</span>
          </NavLink>
        ))}

        <div className="nav-section"><span>Reports & System</span></div>
        {reportsNavItems.map((item) => (
          <NavLink key={item.path} to={item.path} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title={isCollapsed ? item.label : undefined} onClick={onClose}>
            <item.icon size={16} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="system-status" title={isCollapsed ? (isDemoMode ? 'Simulated Intelligence Feed' : 'I4C Core Connected') : undefined}>
          <div className={`status-indicator ${isDemoMode ? 'demo' : 'online'}`}></div>
          <span>{isDemoMode ? 'Simulated Intelligence Feed' : 'I4C Core Connected'}</span>
        </div>
        <NavLink to="/" className="nav-item" style={{ marginTop: 'var(--space-2)', color: 'var(--status-critical)' }} title={isCollapsed ? 'Secure Logout' : undefined} onClick={onClose}>
          <LogOut size={16} />
          <span>Secure Logout</span>
        </NavLink>
      </div>
    </aside>
  );
}
