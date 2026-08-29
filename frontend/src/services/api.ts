export interface MacroStats {
  activeInvestigations: number;
  highRiskAlerts: number;
  successfulInterventions: number;
}

export interface ScenarioData {
  id: string;
  title: string;
  description: string;
  verdict: 'UNANIMOUS_FRAUD_INTERCEPT' | 'LEGITIMATE_TRANSACTION_VERIFIED_CLEAR' | 'BORDERLINE_RE_EVALUATION';
  riskLevel: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'SAFE';
  swarmWeights: { financial: number; forensic: number; geoSpatial: number };
  overallRisk: number;
  expectedWindow: number;
  predictedAtms: { id: string; name: string; lat: number; lng: number; riskScore: number; probability: number }[];
  networkNodes: { id: string; label: string; riskType: string; amount?: string; details?: string }[];
  networkEdges: { source: string; target: string; amount: string; riskType: string; timestamp?: string }[];
  bankIntervention: { required: boolean; status: string; amount?: string; refId?: string };
  leaIntervention: { required: boolean; status: string; unit?: string; eta?: string };
  complaintDetails?: {
    victimName: string;
    contact: string;
    amountLost: string;
    dateReported: string;
    utr: string;
    location: string;
  };
}

// Simulated Database of Scenarios
export const MOCK_SCENARIOS: Record<string, ScenarioData> = {
  'SCENARIO_001': {
    id: 'SCENARIO_001', title: 'Delhi NCR – Mewat Corridor (APK Scam)', description: 'Electricity bill APK installation scam leading to rapid multi-hop transfers.',
    verdict: 'UNANIMOUS_FRAUD_INTERCEPT', riskLevel: 'CRITICAL', overallRisk: 92.4,
    swarmWeights: { financial: 38, forensic: 42, geoSpatial: 20 }, expectedWindow: 12.5,
    predictedAtms: [
      { id: 'atm-1', name: 'PNB ATM, Sector 18, Noida', lat: 28.5355, lng: 77.3910, riskScore: 94, probability: 82 },
      { id: 'atm-2', name: 'HDFC ATM, Sector 15, Noida', lat: 28.5385, lng: 77.3880, riskScore: 65, probability: 15 }
    ],
    networkNodes: [
      { id: 'victim', label: 'Victim (SBI)', riskType: 'safe', details: 'A/C: 3190XXXX912' },
      { id: 'mule1', label: 'Mule L1', riskType: 'warning', details: 'A/C: 5521XXXX882' },
      { id: 'kingpin', label: 'Aggregator', riskType: 'critical', details: 'A/C: 9912XXXX111' },
      { id: 'cashout', label: 'Cash-out', riskType: 'critical', details: 'Location: Noida' }
    ],
    networkEdges: [
      { source: 'victim', target: 'mule1', amount: '₹1,50,000', riskType: 'warning', timestamp: '10:12:05' },
      { source: 'mule1', target: 'kingpin', amount: '₹1,50,000', riskType: 'critical', timestamp: '10:12:12' },
      { source: 'kingpin', target: 'cashout', amount: '₹1,50,000', riskType: 'critical', timestamp: '10:14:02' }
    ],
    bankIntervention: { required: true, status: 'ACTIVE HOLD', amount: '₹1,50,000', refId: 'CFC-2026-8812A' },
    leaIntervention: { required: true, status: 'DISPATCHED', unit: 'PCR-73 (Noida)', eta: '4 mins' },
    complaintDetails: { victimName: 'John Doe', contact: '+91-9876543210', amountLost: '₹1,50,000', dateReported: '2026-08-29 09:14', utr: 'UTR987654321012', location: 'Delhi NCR' }
  },
  'SCENARIO_002': {
    id: 'SCENARIO_002', title: 'Bengaluru – Digital Arrest / CBI Impersonation', description: 'High-value wire transfer driven by fear tactics impersonating customs/CBI.',
    verdict: 'UNANIMOUS_FRAUD_INTERCEPT', riskLevel: 'CRITICAL', overallRisk: 98.1,
    swarmWeights: { financial: 50, forensic: 40, geoSpatial: 10 }, expectedWindow: 8.5,
    predictedAtms: [
      { id: 'atm-b1', name: 'ICICI ATM, Koramangala', lat: 12.9352, lng: 77.6245, riskScore: 88, probability: 75 }
    ],
    networkNodes: [
      { id: 'victim', label: 'Victim (HDFC)', riskType: 'safe', details: 'A/C: 1120XXXX912' },
      { id: 'mule1', label: 'Shell Corp A', riskType: 'critical', details: 'A/C: 4421XXXX000' },
      { id: 'crypto', label: 'P2P Crypto Ex', riskType: 'critical', details: 'Binance OTC' }
    ],
    networkEdges: [
      { source: 'victim', target: 'mule1', amount: '₹45,00,000', riskType: 'critical', timestamp: '08:15:00' },
      { source: 'mule1', target: 'crypto', amount: '₹45,00,000', riskType: 'critical', timestamp: '08:18:22' }
    ],
    bankIntervention: { required: true, status: 'FUNDS FROZEN', amount: '₹45,00,000', refId: 'CFC-2026-112B' },
    leaIntervention: { required: true, status: 'DISPATCHED', unit: 'Cyber Cell BLR', eta: '12 mins' },
    complaintDetails: { victimName: 'Ramesh K.', contact: '+91-9988776655', amountLost: '₹45,00,000', dateReported: '2026-08-29 08:30', utr: 'UTR1122334455', location: 'Bengaluru' }
  },
  'SCENARIO_003': {
    id: 'SCENARIO_003', title: 'Jaipur – Telegram Task Fraud', description: 'Victim completed micro-tasks, then was duped into paying large premium deposits.',
    verdict: 'UNANIMOUS_FRAUD_INTERCEPT', riskLevel: 'HIGH', overallRisk: 84.5,
    swarmWeights: { financial: 30, forensic: 50, geoSpatial: 20 }, expectedWindow: 24.0,
    predictedAtms: [
      { id: 'atm-j1', name: 'Axis ATM, Malviya Nagar', lat: 26.8530, lng: 75.8047, riskScore: 78, probability: 60 }
    ],
    networkNodes: [
      { id: 'victim', label: 'Victim', riskType: 'safe' },
      { id: 'merchant', label: 'Fake Merchant', riskType: 'warning' },
      { id: 'agg', label: 'Aggregator', riskType: 'critical' }
    ],
    networkEdges: [
      { source: 'victim', target: 'merchant', amount: '₹1,20,000', riskType: 'warning' },
      { source: 'merchant', target: 'agg', amount: '₹1,20,000', riskType: 'critical' }
    ],
    bankIntervention: { required: true, status: 'PENDING LIEN', amount: '₹1,20,000', refId: 'CFC-2026-554' },
    leaIntervention: { required: false, status: 'NOT REQUIRED' },
    complaintDetails: { victimName: 'Priya S.', contact: '+91-8877665544', amountLost: '₹1,20,000', dateReported: '2026-08-28 22:10', utr: 'UTR555444333', location: 'Jaipur' }
  },
  'SCENARIO_004': {
    id: 'SCENARIO_004', title: 'Mumbai – Investment Scam', description: 'Fake stock trading app promising 300% returns.',
    verdict: 'BORDERLINE_RE_EVALUATION', riskLevel: 'HIGH', overallRisk: 75.0,
    swarmWeights: { financial: 40, forensic: 40, geoSpatial: 20 }, expectedWindow: 48.0,
    predictedAtms: [],
    networkNodes: [
      { id: 'victim', label: 'Victim', riskType: 'safe' },
      { id: 'mule', label: 'Mule A/C', riskType: 'critical' }
    ],
    networkEdges: [
      { source: 'victim', target: 'mule', amount: '₹8,50,000', riskType: 'critical' }
    ],
    bankIntervention: { required: true, status: 'FUNDS FROZEN', amount: '₹8,50,000', refId: 'CFC-2026-332' },
    leaIntervention: { required: false, status: 'NOT REQUIRED' },
    complaintDetails: { victimName: 'Amit V.', contact: '+91-7766554433', amountLost: '₹8,50,000', dateReported: '2026-08-28 15:20', utr: 'UTR999888777', location: 'Mumbai' }
  },
  'SCENARIO_005': {
    id: 'SCENARIO_005', title: 'Kolkata – Courier Extortion', description: 'Victim told a package containing illegal items was seized by customs.',
    verdict: 'UNANIMOUS_FRAUD_INTERCEPT', riskLevel: 'HIGH', overallRisk: 89.2,
    swarmWeights: { financial: 45, forensic: 35, geoSpatial: 20 }, expectedWindow: 6.5,
    predictedAtms: [
       { id: 'atm-k1', name: 'SBI ATM, Salt Lake', lat: 22.5866, lng: 88.4116, riskScore: 85, probability: 70 }
    ],
    networkNodes: [
      { id: 'victim', label: 'Victim', riskType: 'safe' },
      { id: 'mule1', label: 'Mule', riskType: 'warning' }
    ],
    networkEdges: [
      { source: 'victim', target: 'mule1', amount: '₹3,00,000', riskType: 'warning' }
    ],
    bankIntervention: { required: true, status: 'ACTIVE HOLD', amount: '₹3,00,000', refId: 'CFC-2026-221' },
    leaIntervention: { required: true, status: 'DISPATCHED', unit: 'Salt Lake PS', eta: '8 mins' },
    complaintDetails: { victimName: 'Sneha D.', contact: '+91-6655443322', amountLost: '₹3,00,000', dateReported: '2026-08-29 11:00', utr: 'UTR123123123', location: 'Kolkata' }
  },
  'SCENARIO_006': {
    id: 'SCENARIO_006', title: 'Pune – Legitimate Transaction', description: 'Clean salary payment or merchant settlement falsely flagged by heuristic rules. Zero-Harm principle applied.',
    verdict: 'LEGITIMATE_TRANSACTION_VERIFIED_CLEAR', riskLevel: 'SAFE', overallRisk: 4.2,
    swarmWeights: { financial: 12, forensic: 5, geoSpatial: 2 }, expectedWindow: 0,
    predictedAtms: [],
    networkNodes: [
      { id: 'employer', label: 'Corporate A/C', riskType: 'safe' },
      { id: 'employee', label: 'Employee Salary A/C', riskType: 'safe' }
    ],
    networkEdges: [
      { source: 'employer', target: 'employee', amount: '₹85,000', riskType: 'safe' }
    ],
    bankIntervention: { required: false, status: 'CLEARED' },
    leaIntervention: { required: false, status: 'NOT REQUIRED' },
    complaintDetails: { victimName: 'System Flag', contact: 'N/A', amountLost: '₹0', dateReported: '2026-08-29 12:00', utr: 'N/A', location: 'Pune' }
  },
  'SCENARIO_007': {
    id: 'SCENARIO_007', title: 'Mumbai – Hawala (ReAct Retry)', description: 'Borderline evidence. Initial trace failed. Agentic ReAct framework triggered re-evaluation and found hidden links.',
    verdict: 'BORDERLINE_RE_EVALUATION', riskLevel: 'HIGH', overallRisk: 78.5,
    swarmWeights: { financial: 45, forensic: 20, geoSpatial: 35 }, expectedWindow: 45.0,
    predictedAtms: [
      { id: 'atm-m1', name: 'Axis Bank ATM, Andheri East', lat: 19.1136, lng: 72.8697, riskScore: 81, probability: 65 }
    ],
    networkNodes: [
      { id: 'source', label: 'Suspect Shell', riskType: 'warning' },
      { id: 'mixer', label: 'Crypto/Hawala Layer', riskType: 'critical' },
      { id: 'cashout', label: 'Target ATM', riskType: 'critical' }
    ],
    networkEdges: [
      { source: 'source', target: 'mixer', amount: '₹5,00,000', riskType: 'warning' },
      { source: 'mixer', target: 'cashout', amount: '₹5,00,000', riskType: 'critical' }
    ],
    bankIntervention: { required: true, status: 'PENDING LIEN', amount: '₹5,00,000', refId: 'CFC-2026-991B' },
    leaIntervention: { required: true, status: 'PROCESSING', unit: 'Pending Assignment', eta: 'TBD' },
    complaintDetails: { victimName: 'Intel Target', contact: 'N/A', amountLost: '₹5,00,000', dateReported: '2026-08-29 02:15', utr: 'UTR444555666', location: 'Mumbai' }
  }
};

const BASE_URL = 'http://localhost:8000/api';

class ApiService {
  isDemoMode = false;

  private async fetchOrFallback<T>(url: string, options: RequestInit, fallback: T, timeoutMs = 300_000): Promise<T> {
    if (this.isDemoMode) return fallback;
    // Abort controller gives a real timeout instead of silently hanging
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(url, { ...options, signal: controller.signal });
      clearTimeout(timer);
      if (!response.ok) throw new Error(`API Error ${response.status}`);
      return await response.json();
    } catch (error) {
      clearTimeout(timer);
      console.warn(`Real backend unavailable at ${url}. Falling back to DEMO MODE.`, error);
      this.isDemoMode = true;
      window.dispatchEvent(new Event('demo-mode-activated'));
      return fallback;
    }
  }

  async getMacroStats(): Promise<MacroStats> {
    return this.fetchOrFallback<MacroStats>(`${BASE_URL}/stats/macro`, { method: 'GET' }, {
      activeInvestigations: 124,
      highRiskAlerts: 18,
      successfulInterventions: 42
    });
  }

  async runInvestigation(scenarioId: string): Promise<ScenarioData> {
    const mockData = MOCK_SCENARIOS[scenarioId] || MOCK_SCENARIOS['SCENARIO_001'];
    return this.fetchOrFallback<ScenarioData>(
      `${BASE_URL}/investigate/run`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenarioId }),
      },
      mockData,
      300_000, // 5-minute timeout for agent run
    );
  }

  async freezeFunds(accountId: string) {
    return this.fetchOrFallback(
      `${BASE_URL}/interlock/freeze`,
      { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ accountId }) },
      { status: 'ACTIVE HOLD' },
    );
  }

  async dispatchLEA(atmId: string) {
    // Backend expects `accountId` for both freeze and dispatch
    return this.fetchOrFallback(
      `${BASE_URL}/interlock/dispatch`,
      { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ accountId: atmId }) },
      { status: 'DISPATCHED' },
    );
  }

  async generateDossier(caseId: string) {
    return this.fetchOrFallback(
      `${BASE_URL}/dossier/generate`,
      { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ caseId }) },
      { url: '/dossier-mock.pdf' },
    );
  }

  getAllMockScenarios(): Record<string, ScenarioData> {
    return MOCK_SCENARIOS;
  }
}

export const apiService = new ApiService();
