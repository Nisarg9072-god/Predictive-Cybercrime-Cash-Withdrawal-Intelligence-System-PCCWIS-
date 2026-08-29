import React, { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import { apiService } from '../services/api';
import type { ScenarioData } from '../services/api';

interface InvestigationContextType {
  activeScenario: ScenarioData | null;
  isLoading: boolean;
  isDemoMode: boolean;
  mockComplaints: ScenarioData[];
  loadScenario: (scenarioId: string) => Promise<void>;
  clearScenario: () => void;
  addComplaint: (scenario: ScenarioData) => void;
}

const InvestigationContext = createContext<InvestigationContextType | undefined>(undefined);

export function InvestigationProvider({ children }: { children: ReactNode }) {
  const [activeScenario, setActiveScenario] = useState<ScenarioData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDemoMode, setIsDemoMode] = useState(apiService.isDemoMode);
  const [mockComplaints, setMockComplaints] = useState<ScenarioData[]>(Object.values(apiService.getAllMockScenarios()));

  // Listen for demo mode activations
  React.useEffect(() => {
    const handleDemoMode = () => setIsDemoMode(true);
    window.addEventListener('demo-mode-activated', handleDemoMode);
    return () => window.removeEventListener('demo-mode-activated', handleDemoMode);
  }, []);

  const loadScenario = async (scenarioId: string) => {
    setIsLoading(true);
    try {
      const data = await apiService.runInvestigation(scenarioId);
      setActiveScenario(data);
    } catch (error) {
      console.error('Failed to load scenario', error);
    } finally {
      setIsLoading(false);
    }
  };

  const clearScenario = () => {
    setActiveScenario(null);
  };

  const addComplaint = (scenario: ScenarioData) => {
    setMockComplaints(prev => [scenario, ...prev]);
  };

  return (
    <InvestigationContext.Provider value={{ activeScenario, isLoading, isDemoMode, mockComplaints, loadScenario, clearScenario, addComplaint }}>
      {children}
    </InvestigationContext.Provider>
  );
}

export function useInvestigation() {
  const context = useContext(InvestigationContext);
  if (context === undefined) {
    throw new Error('useInvestigation must be used within an InvestigationProvider');
  }
  return context;
}
