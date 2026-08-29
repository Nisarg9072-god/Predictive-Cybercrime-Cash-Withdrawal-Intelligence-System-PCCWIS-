import { useEffect, useState } from 'react';
import { Check, Circle, Loader2 } from 'lucide-react';
import type { StepPhase, StepStatus } from '../../services/websocket';
import { useInvestigation } from '../../context/InvestigationContext';
import './InvestigationTimeline.css';

interface StepState {
  phase: StepPhase;
  status: StepStatus;
  merkle_hash?: string;
}

const INITIAL_STEPS: StepState[] = [
  { phase: 'OBSERVE', status: 'QUEUED' },
  { phase: 'LAYER-1 TRACE', status: 'QUEUED' },
  { phase: 'BFS / NETWORK ANALYSIS', status: 'QUEUED' },
  { phase: 'FORENSICS', status: 'QUEUED' },
  { phase: 'EVALUATE / CONSENSUS', status: 'QUEUED' },
  { phase: 'PREDICT', status: 'QUEUED' },
  { phase: 'INTERVENE', status: 'QUEUED' },
];

export function InvestigationTimeline() {
  const [steps, setSteps] = useState<StepState[]>(INITIAL_STEPS);
  const [isComplete, setIsComplete] = useState(false);

  const { activeScenario } = useInvestigation();

  useEffect(() => {
    if (!activeScenario) {
      setSteps(INITIAL_STEPS);
      setIsComplete(false);
      return;
    }

    // SIMULATED PROGRESSION FOR DEMO
    setSteps(INITIAL_STEPS);
    setIsComplete(false);
    
    let currentStep = 0;
    
    const interval = setInterval(() => {
      setSteps(prev => {
        const next = [...prev];
        
        // Mark previous step as complete
        if (currentStep > 0 && currentStep <= next.length) {
          next[currentStep - 1] = { 
            ...next[currentStep - 1], 
            status: 'COMPLETED',
            merkle_hash: '0x' + Math.random().toString(16).slice(2, 10).toUpperCase()
          };
        }

        // Mark current step as running
        if (currentStep < next.length) {
          next[currentStep] = { ...next[currentStep], status: 'RUNNING' };
        } else {
          setIsComplete(true);
          clearInterval(interval);
        }

        currentStep++;
        return next;
      });
    }, 1500); // Step progresses every 1.5s for demo

    return () => clearInterval(interval);
  }, [activeScenario]);

  const renderIcon = (status: StepStatus) => {
    switch (status) {
      case 'COMPLETED': return <Check size={14} />;
      case 'RUNNING': return <Loader2 size={14} className="spin" />;
      default: return <Circle size={10} />;
    }
  };

  return (
    <div className="timeline-container">
      <div className="timeline-header">
        <span>Investigation Timeline</span>
        {isComplete && <span className="text-safe" style={{ fontSize: '0.875rem' }}>COMPLETED</span>}
      </div>
      
      <div className="timeline-steps">
        {steps.map((step, index) => (
          <div key={step.phase} className={`timeline-step ${step.status.toLowerCase()}`}>
            <div className="timeline-icon-wrapper">
              {renderIcon(step.status)}
            </div>
            
            <div className="timeline-content">
              <div className="timeline-title">
                <span>{index + 1}. {step.phase}</span>
                <span className={`timeline-status status-${step.status.toLowerCase()}`}>
                  {step.status}
                </span>
              </div>
              
              {step.merkle_hash && (
                <div className="timeline-meta">
                  Hash: {step.merkle_hash}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
