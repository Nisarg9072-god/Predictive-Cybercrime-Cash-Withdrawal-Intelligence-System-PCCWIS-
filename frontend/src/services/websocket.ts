export type StepPhase = 
  | 'OBSERVE'
  | 'LAYER-1 TRACE'
  | 'BFS / NETWORK ANALYSIS'
  | 'FORENSICS'
  | 'EVALUATE / CONSENSUS'
  | 'PREDICT'
  | 'INTERVENE';

export type StepStatus = 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'ERROR';

export interface InvestigationEvent {
  type: 'STEP_UPDATE' | 'INVESTIGATION_COMPLETE';
  step: number;
  phase: StepPhase;
  status: StepStatus;
  merkle_hash?: string;
  message?: string;
}

export type WebSocketCallback = (event: InvestigationEvent) => void;

class HybridWebSocketService {
  private callbacks: WebSocketCallback[] = [];
  private ws: WebSocket | null = null;
  private isConnected = false;
  private isDemoMode = false;
  private simulationInterval: ReturnType<typeof setInterval> | null = null;
  
  private steps: StepPhase[] = [
    'OBSERVE',
    'LAYER-1 TRACE',
    'BFS / NETWORK ANALYSIS',
    'FORENSICS',
    'EVALUATE / CONSENSUS',
    'PREDICT',
    'INTERVENE'
  ];

  connect(url: string) {
    if (this.isDemoMode) {
      console.log(`[DEMO MODE] Mock WS Connected to ${url}`);
      this.isConnected = true;
      return;
    }

    try {
      this.ws = new WebSocket(url);
      
      this.ws.onopen = () => {
        console.log(`Connected to live WS: ${url}`);
        this.isConnected = true;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as InvestigationEvent;
          this.emit(data);
        } catch (e) {
          console.error("Failed to parse WS message", e);
        }
      };

      this.ws.onerror = () => {
        console.warn(`Real WebSocket unavailable at ${url}. Falling back to DEMO MODE.`);
        this.isDemoMode = true;
        this.isConnected = true;
        window.dispatchEvent(new Event('demo-mode-activated'));
      };

      this.ws.onclose = () => {
        this.isConnected = false;
      };
    } catch (e) {
      console.warn(`WebSocket connection failed, falling back to DEMO MODE.`);
      this.isDemoMode = true;
      this.isConnected = true;
      window.dispatchEvent(new Event('demo-mode-activated'));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
    this.stopSimulation();
  }

  onMessage(callback: WebSocketCallback) {
    this.callbacks.push(callback);
  }

  private emit(event: InvestigationEvent) {
    this.callbacks.forEach(cb => cb(event));
  }

  startInvestigation(complaintId: string) {
    if (!this.isConnected) return;
    
    if (this.isDemoMode) {
      this.runMockInvestigation(complaintId);
    } else {
      // Send command to real backend
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ action: 'START_INVESTIGATION', complaintId }));
      }
    }
  }

  private runMockInvestigation(complaintId: string) {
    console.log(`[DEMO MODE] Starting investigation for ${complaintId}...`);
    
    let currentStepIndex = 0;
    
    // First, emit all as queued
    this.steps.forEach((phase, index) => {
      this.emit({
        type: 'STEP_UPDATE',
        step: index + 1,
        phase,
        status: 'QUEUED',
      });
    });

    // Start the first step
    this.emit({
      type: 'STEP_UPDATE',
      step: currentStepIndex + 1,
      phase: this.steps[currentStepIndex],
      status: 'RUNNING',
      message: 'Initializing agent...'
    });

    this.simulationInterval = setInterval(() => {
      // Complete current step
      this.emit({
        type: 'STEP_UPDATE',
        step: currentStepIndex + 1,
        phase: this.steps[currentStepIndex],
        status: 'COMPLETED',
        merkle_hash: Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
      });

      currentStepIndex++;

      if (currentStepIndex >= this.steps.length) {
        this.stopSimulation();
        this.emit({
          type: 'INVESTIGATION_COMPLETE',
          step: currentStepIndex,
          phase: 'INTERVENE',
          status: 'COMPLETED'
        });
        return;
      }

      // Start next step
      this.emit({
        type: 'STEP_UPDATE',
        step: currentStepIndex + 1,
        phase: this.steps[currentStepIndex],
        status: 'RUNNING',
        message: 'Agent processing...'
      });

    }, 3000); // 3 seconds per step for demo purposes
  }

  private stopSimulation() {
    if (this.simulationInterval) {
      clearInterval(this.simulationInterval);
      this.simulationInterval = null;
    }
  }
}

// Export a singleton instance
export const wsService = new HybridWebSocketService();
