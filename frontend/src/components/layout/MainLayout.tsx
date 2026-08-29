import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import './Layout.css';

export function MainLayout() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const toggleSidebar = () => {
    if (window.innerWidth <= 768) {
      setIsMobileOpen(!isMobileOpen);
    } else {
      setIsSidebarCollapsed(!isSidebarCollapsed);
    }
  };

  const closeMobileSidebar = () => setIsMobileOpen(false);

  return (
    <div className="layout-container">
      <Sidebar 
        isCollapsed={isSidebarCollapsed} 
        isOpen={isMobileOpen} 
        onClose={closeMobileSidebar} 
      />
      {isMobileOpen && <div className="sidebar-overlay" onClick={closeMobileSidebar} />}
      <div className="main-content">
        <Header onToggleSidebar={toggleSidebar} />
        <main className="page-container">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
