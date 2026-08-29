import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { InvestigationProvider } from './context/InvestigationContext'
import 'leaflet/dist/leaflet.css'
import './styles/global.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <InvestigationProvider>
        <App />
      </InvestigationProvider>
    </BrowserRouter>
  </StrictMode>,
)
