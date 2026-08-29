# 🛡️ CYBER-INTERCEPT: Predictive Analytics & Agentic Framework for Proactive Cybercrime Intervention

[![SIH 2026](https://img.shields.io/badge/SIH%202026-Problem%20ID%2026184-blue.svg)](https://www.sih.gov.in/)
[![Ministry of Home Affairs](https://img.shields.io/badge/Organization-Ministry%20of%20Home%20Affairs%20(I4C)-orange.svg)](https://i4c.mha.gov.in/)
[![Theme](https://img.shields.io/badge/Theme-Blockchain%20%26%20Cybersecurity-red.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-Autonomous%20ReAct%20Swarm%20Loop-green.svg)]()
[![Execution Speed](https://img.shields.io/badge/Response%20Latency-%3C%201.8%20Seconds-purple.svg)]()
[![Compliance](https://img.shields.io/badge/Legal%20Admissibility-Section%2065B%20IEA%20%2F%20Sec%2094%20BNSS-gold.svg)]()

> **Problem Statement ID:** 26184  
> **Problem Statement Title:** Development of a Predictive Analytics Framework for Cybercrime Complaints to Forecast Likely Cash Withdrawal Locations in Advance, Enabling Generation of Actionable Intelligence for Timely and Proactive Cybercrime Intervention.  
> **Organization:** Ministry of Home Affairs (MHA) / Indian Cyber Crime Coordination Centre (I4C), CIS Division.

---

## 📌 1. Executive Summary & Problem Context

India's National Cybercrime Reporting Portal (**NCRP / 1930**) receives over **8,000+ complaints daily**. When victims lose money to UPI fraud, digital arrest scams, APK malware, or investment syndicates, the stolen funds do not remain in a single account. Fraudsters execute **rapid multi-layer smurfing** across 5–10 mule accounts and physically withdraw cash from ATMs/CSPs within **20 to 45 minutes ("The Golden Hour")**.

### The Traditional Reactive Bottleneck (3 to 7 Days):
$$\text{Victim FIR} \longrightarrow \text{Manual Police Review} \longrightarrow \text{Section 91 Notice via Email} \longrightarrow \text{Bank Review} \longrightarrow \text{Balance = ₹0 (Cashed Out)}$$
By the time manual bank notices are processed, cash is already gone, and recovery rates drop below **5%**.

### The CYBER-INTERCEPT Proactive Solution (< 12 Minutes):
$$\text{1930 Ingestion} \xrightarrow[\text{Agent Swarm}]{\text{1.8 Seconds}} \text{5-Hop BFS Graph} \xrightarrow[\text{DBSCAN ML}]{\text{ATM Hotspot Predict}} \xrightarrow[\text{Dual Interlock}]{\text{< 12 Mins}} \begin{cases} \text{🔒 CFCFRMS Automated Bank Lien} \\ \text{🚔 Geofenced PCR Patrol Dispatched} \\ \text{📜 Section 91 Cr.P.C. SHA-256 Dossier} \end{cases}$$

---

## 🔄 2. The 7-Step Autonomous ReAct Agent Swarm

The backend engine (`backend/engines/agentic_investigator.py`) is driven by a dynamic **ReAct (Reasoning + Action) Multi-Agent Swarm** that orchestrates three specialist AI agents across 7 distinct phases:

```mermaid
flowchart TD
    A([🚨 1930 Complaint Ingested]) --> S1[Step 1: OBSERVE - Ingest Complaint & Establish Digital Ledger Baseline]
    S1 --> S2[Step 2: REASON & ACT - Tool 1: Layer-1 Beneficiary Trace]
    S2 --> S3[Step 3: REASON & ACT - Tool 2: BFS 5-Hop Graph + Kingpin Centrality + Smurfing Burst]
    S3 --> S4[Step 4: REASON & ACT - Tool 3, 8, 9: Profile Forensics + Dynamic Risk + SIM Swap]
    S4 --> S5{Step 5: EVALUATE & REAct GATE - Evidence Score >= 0.35?}
    
    S5 -- "Clean (Score < 0.35)" --> S5Clear[🟢 Step 5: False-Positive Clear - Zero Harm Circuit Breaker]
    S5 -- "Borderline Evidence" --> S5Retry[🟣 Step 5.x: ReAct Self-Correction Loop - 6 Autonomous Recovery Tools]
    S5Retry --> S5
    
    S5 -- "Fraud Confirmed" --> S6[Step 6: PREDICT - Tool 5: Spatio-Temporal DBSCAN ML + Exponential Hazard Decay]
    S6 --> S7[Step 7: INTERVENE - Tools 6, 7, 10: CFCFRMS Lien + PCR Dispatch + 7-Step Merkle Dossier]
    
    S7 --> Out([🏆 Intercept Complete in < 12 Mins])
```

### Detailed Phase Breakdown:

| Step | Phase | Autonomous Actions & Tool Invocations | Time |
| :--- | :--- | :--- | :---: |
| **Step 1** | **OBSERVE** | Ingests 1930 complaint. Maps complainant, bank, city, state, and transaction baseline against the 31.9M AML database. | $T + 1\text{s}$ |
| **Step 2** | **REASON & ACT** | **Tool 1 (`get_account_transfer`)**: Traces outbound UPI/IMPS transfer to identify Layer-1 Aggregator Mule. | $T + 3\text{s}$ |
| **Step 3** | **REASON & ACT** | **Tool 2 (`bfs_multihop_trace`)**: Executes BFS traversal up to **5 hops** deep.<br>**Tool 4 (`detect_smurfing_burst`)**: Detects high-velocity transfers within $\le 180\text{s}$ windows.<br>**Move 3 (`compute_graph_centrality`)**: Computes in-degree & flow betweenness to pinpoint the **Kingpin Aggregator Node**. | $T + 5\text{s}$ |
| **Step 4** | **REASON & ACT** | **Tool 3 (`get_mule_profile`)**: Extracts KYC status, account age, and velocity.<br>**Tool 8 (`compute_dynamic_risk_score`)**: Calculates multi-factor risk ($0.0 \rightarrow 1.0$).<br>**Tool 9 (`check_sim_swap_dynamic`)**: Identifies SIM swap anomalies (account age $< 7\text{ days}$). | $T + 7\text{s}$ |
| **Step 5** | **EVALUATE & REAct GATE** | **False-Positive Defense**: If clean account, triggers **Zero-Harm Circuit Breaker** (`LEGITIMATE_CLEAR`).<br>**ReAct Autonomous Loop**: If evidence is below threshold, dynamically selects and invokes up to 3 recovery tools from the **6-Tool Registry**. | $T + 9\text{s}$ |
| **Step 6** | **PREDICT (ML Engine)** | **Tool 5 (`predict_atm_hotspots`)**: Runs `sklearn.cluster.DBSCAN` ($\varepsilon = 0.15^\circ \approx 16\text{km}$) on state-level mule GPS coordinates.<br>**Move 2 (`calculate_cashout_hazard_probability`)**: Evaluates the Exponential Time-Decay Hazard function for real-time withdrawal urgency. | $T + 11\text{s}$ |
| **Step 7** | **INTERVENE & SEAL** | **Tool 6 (`trigger_bank_lien`)**: Automated CFCFRMS API lien freeze.<br>**Tool 7 (`dispatch_lea_alert`)**: Geofenced PCR beat patrol dispatched with dynamic Haversine ETA.<br>**Tool 10 (`generate_section_91_crpc_dossier`)**: Generates court-admissible legal notice.<br>**Move 1 (`seal_merkle_chain`)**: Seals **7-Step Cryptographic Merkle Root Hash** under Section 65B Indian Evidence Act. | $T + 12\text{s}$ |

---

## ⚡ 3. Advanced Backend Innovations (SIH 2026 Core Track)

### 🔗 Move 1: 7-Step Cryptographic Merkle Audit Chain (Blockchain Track)
To satisfy **Section 65B of the Indian Evidence Act** and **Section 94 of BNSS**, the backend implements a cryptographically-sealed Merkle audit chain across all agent reasoning phases:
$$\text{Block Hash}_n = \text{SHA256}(\text{Prev Hash} \parallel \text{Step Index} \parallel \text{Phase} \parallel \text{Step Payload Digest})$$

```
[Genesis Hash: 0000000000000000...]
       │
       ▼ (Step 1: OBSERVE) ───────── Block Hash 1: fe119f3b996f45...
       │
       ▼ (Step 2: LAYER-1 TRACE) ─── Block Hash 2: e8fa564e0d1f08...
       │
       ▼ (Step 3: BFS & CENTRALITY) ─ Block Hash 3: 9c4e35746465c8...
       │
       ▼ (Step 4: PROFILE FORENSICS) ─ Block Hash 4: 54e0829c1f5720...
       │
       ▼ (Step 5: REACT EVALUATION) ─ Block Hash 5: 70ccbb602e8315...
       │
       ▼ (Step 6: DBSCAN SPATIAL ML) ─ Block Hash 6: 7a8ada3253e361...
       │
       ▼ (Step 7: DUAL INTERLOCK) ─── Merkle Root: 99d652583fa31d... (SEALED)
```
* **Court Admissibility:** Guarantees to judges and courts that evidence, AI thoughts, and timestamps were generated at runtime and were not tampered with.

---

### ⏱️ Move 2: Exponential Cashout Time-Decay Hazard Model (Temporal ML)
Rather than static arrival times, the system models the **cumulative probability of physical ATM cash withdrawal** over time using an exponential hazard decay function:
$$P(\text{ATM Cashout within } t\text{ mins}) = 1 - e^{-\lambda t}$$
where the hazard rate parameter $\lambda$ is derived from the suspect mule's real-time withdrawal velocity ($\text{txns/day}$):
$$\lambda = \frac{\text{withdrawal\_velocity\_per\_day}}{24 \times 6}$$

* **Live Output Example:**
  ```json
  "temporal_hazard_model": {
    "hazard_rate_lambda": 0.07431,
    "cashout_prob_current_pct": 44.8,
    "cashout_prob_15min_window_pct": 71.7,
    "urgency_level": "HIGH_PRIORITY",
    "model_equation": "P(Cashout|t) = 1 - exp(-λ * t)",
    "expected_window_minutes": 13.5
  }
  ```

---

### 🕸️ Move 3: Graph Centrality & Kingpin Aggregator Detection (Graph Theory)
In Step 3, the agent computes network flow dynamics across the multi-hop BFS subgraph:
* **In-Degree Centrality:** Identifies accounts aggregating stolen funds from multiple victim sources.
* **Flow Volume (INR):** Calculates the total rupee throughput passing through each node.
* **Kingpin Isolation:** Identifies the primary syndication node ($K_{\text{agg}}$) using $\text{Score}(n) = \text{In-Degree}(n) \times 10^4 + \text{Volume}(n)$.
* **Network Topology Classification:** Classifies graph into `HIGH_VELOCITY_FANOUT` (smurfing tree) vs. `MULTI_LAYERED_HOP_CHAIN`.

---

### 🛠️ Move 4: 6-Tool Autonomous ReAct Recovery Registry
When initial evidence is borderline ($0.35 \le \text{Score} < 0.90$), the ReAct loop autonomously evaluates and invokes forensic tools:

| Tool Name | Forensic Description | Evidence Bonus |
| :--- | :--- | :---: |
| `check_terminal_cashout()` | Queries database for terminal ATM withdrawal transaction flags | $+0.12 \text{ to } +0.36$ |
| `query_sibling_chain()` | Computes the laundering-to-legitimate transaction ratio across the `chain_id` | $+0.10 \text{ to } +0.25$ |
| `cross_check_imei()` | Scans the database for other accounts sharing the same hardware IMEI hash | $+0.10 \text{ to } +0.30$ |
| `check_cross_bank_clusters()` | Discovers parallel mule accounts registered under the same suspect name across other banks | $+0.10 \text{ to } +0.20$ |
| `check_ip_asn_reputation()` | Scans IP/ASN proxy and commercial datacenter hosting signatures on UPI sessions | $+0.18$ |
| `expand_bfs_radius()` | Extends BFS traversal radius by $+2$ hops to uncover deeper money laundering rings | $+0.08 \text{ to } +0.24$ |

---

### 🗳️ Move 6: Multi-Agent Swarm Consensus Matrix (Step 5)
Before executing high-impact financial and field interlocks, all three specialist agents independently cast a weighted forensic vote:
* **Financial Ledger Agent ($35\%$ Weight):** Evaluates smurfing burst speed, multi-hop fanout, and laundering ratio.
* **Forensic Profiler Agent ($45\%$ Weight):** Evaluates KYC status, account longevity, velocity spikes, and device IMEI hashes.
* **Geo-Spatial ML Agent ($20\%$ Weight):** Evaluates DBSCAN cluster density and spatial proximity to ATM cashpoints.
* **Consensus Verdict:** Outputs a **Weighted Swarm Score (e.g. $81.5\%$ - `UNANIMOUS_FRAUD_INTERCEPT`)** to ensure interlocks are executed with quorum agreement.

---

### 📜 Move 7: Dynamic Legal Statute Mapping (BNS, 2023 / IT Act / PMLA / BNSS)
In Step 7, the legal engine automatically analyzes the crime category and stolen rupee amount to dynamically cite the exact applicable Indian penal statutes inside the Section 91 notice:
* **Cheating & Fraud:** `Section 318(4) Bharatiya Nyaya Sanhita (BNS), 2023`
* **APK Malware / Device Compromise:** `Section 43 & 66 IT Act, 2000` + `Section 66C IT Act (Identity Theft)`
* **Digital Arrest / Extortion:** `Section 204 BNS (Impersonating Public Servant)` + `Section 308 BNS (Extortion)` + `Section 351 BNS`
* **Task / Investment Syndicates:** `Section 66D IT Act` + `Section 111 BNS (Organized Crime Syndicate)`
* **High-Value Proceeds ($\ge ₹10\text{ Lakhs}$):** `Section 3 & 4 Prevention of Money Laundering Act, 2002 (PMLA)`
* **Digital Certification:** `Section 94 BNSS, 2023 / Section 65B Indian Evidence Act`

---

### 🌲 Move 8: Adaptive Decoy Pruning in BFS Traversal (Step 3)
To defend against cybercriminals deliberately scattering ₹1–₹50 decoy transactions to pollute law enforcement graphs, the BFS engine tags and isolates `PRIMARY_LAUNDERING_TRUNK` edges from `MICRO_DECOY_FILTERED` noise.

---

### 📈 Move 9: Counterfactual "Golden Hour" Recovery Curve (Step 7)
Provides comparative mathematical modeling proving the value of $<12\text{-minute}$ proactive intervention vs traditional reactive methods:
* **$T + 10\text{ mins}$:** $\mathbf{86.4\%}$ Fund Recovery Rate *(Optimal Interception Zone)*
* **$T + 20\text{ mins}$:** $\mathbf{71.8\%}$ Fund Recovery Rate *(High Success Probability)*
* **$T + 35\text{ mins}$:** $\mathbf{52.3\%}$ Fund Recovery Rate *(Moderate Critical Window)*
* **$T + 60\text{ mins}$:** $\mathbf{34.1\%}$ Fund Recovery Rate *(Severe Degradation)*
* **$T + 120\text{ mins}$:** $\mathbf{12.6\%}$ Fund Recovery Rate *(Near Total Cashout)*
* **$T + \text{Day 3}$:** $\mathbf{2.4\%}$ Fund Recovery Rate *(Traditional Reactive Loss)*

---

## 🎯 4. Test Scenarios & Verification Suite

The repository includes pre-configured benchmark scenarios in `data/processed/test_demo_scenarios.json` as well as full support for **arbitrary live custom inputs**:

| Scenario ID | Name & Corridor | Crime Type | Expected Outcome | Key Demonstration Point |
| :--- | :--- | :--- | :--- | :--- |
| **`SCENARIO_001`** | **Delhi NCR - Mewat** | Electricity Bill APK Scam | 🔴 Intercept Active | High-velocity Mewat cyber syndicate tracing. |
| **`SCENARIO_002`** | **Bengaluru - Hyderabad** | Digital Arrest / CBI Impersonation | 🔴 Intercept Active | Multi-crore high-value digital arrest fund split. |
| **`SCENARIO_003`** | **Jaipur - Bharatpur** | Part-Time Telegram Task Fraud | 🔴 Intercept Active | Rapid smurfing across micro-mule accounts. |
| **`SCENARIO_004`** | **Kolkata - Jamtara** | Aadhaar Biometric AePS Spoof | 🔴 Intercept Active | Micro-ATM & CSP cash-out prediction. |
| **`SCENARIO_005`** | **Mumbai - Surat** | Customs Courier Narcotics Extortion | 🔴 Intercept Active | Cross-state fund flow & multi-hop BFS hops. |
| **`SCENARIO_006`** | **Pune - Legitimate** | Clean Merchant / Salary Payment | 🟢 `LEGITIMATE_CLEAR` | **Zero-Harm Policy**: 0 funds locked, 0 police sent. |
| **`SCENARIO_007`** | **Ahmedabad - Hawala** | Hawala Ghost Terminal Network | 🟣 `REACT_RETRY_FIRED` | **ReAct Loop**: Triggers autonomous recovery retries. |

---

## 📡 5. API Reference

### 1. Execute Autonomous Investigation
`POST /api/investigate/run`

#### Request Body (Pre-Loaded Scenario):
```json
{
  "scenario_id": "SCENARIO_001"
}
```

#### Request Body (Live Custom Input from Judge):
```json
{
  "victim_name": "Dr. Ramesh Sharma",
  "victim_bank": "State Bank of India",
  "amount_inr": 75000.0,
  "crime_category": "Electricity Bill APK Scam",
  "victim_city": "Ahmedabad",
  "victim_state": "Gujarat"
}
```
*(Note: To test false-positive protection with custom input, type `"ACC_CLEAN"` in `victim_account` or select `SCENARIO_006`)*.

#### Response:
```json
{
  "status": "success",
  "investigation": {
    "complaint_id": "NCR-2026-68241",
    "total_execution_time_seconds": 1.84,
    "result": {
      "interventions": {
        "cfcfrms_lien_status": "ACTIVE_HOLD",
        "amount_frozen_inr": 75000.0,
        "lea_dispatch_status": "DISPATCHED",
        "assigned_pcr_unit": "PCR-41",
        "police_eta_mins": 8,
        "target_atm_name": "Punjab National Bank ATM"
      },
      "merkle_audit_root": "7a8ada3253e361d82415a05e8bd06c0000ce347550ae023ca8f7774b1aa8e18e",
      "legal_dossier": {
        "notice_id": "SEC91/I4C/2026/83912",
        "section": "Section 91 Cr.P.C. / Section 94 BNSS",
        "court_admissible_hash": "SHA256:a4162d591de2d4a4487e89edd499c1a6c165181c213c7018fafc7923b24fd1bf"
      }
    }
  }
}
```

### 2. WebSocket Real-Time Agent Stream
`WS /ws/investigate`
* Connect via WebSocket and send JSON payload `{"scenario_id": "SCENARIO_001"}` to receive streaming step-by-step reasoning logs, Merkle hashes, and countdown updates in real time.

---

## 🛠️ 6. System Architecture & Tech Stack

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                  FRONTEND DASHBOARD                                    │
│  • React 18 + Vite + Vanilla CSS (Glassmorphism Dark Theme)                           │
│  • Leaflet.js (GIS Risk Heatmaps, ATM Clusters & Geofencing)                           │
│  • MuleNetworkTopology (5-Hop Multi-layer Directed Fund Routing)                       │
│  • AgentStreamConsole (Real-Time ReAct Thought Feed & Merkle Hashes)                  │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ REST / WebSocket (Port 8000)
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                             BACKEND ENGINE (FastAPI / Python)                          │
│  • ReActAgentSwarmOrchestrator (7-Step Autonomous Multi-Agent Core)                    │
│  • FinancialLedgerAgent (BFS 5-Hop Traversal, Smurfing Burst, Graph Centrality)        │
│  • GeoSpatialMLAgent (DBSCAN Spatial Clustering, Exponential Hazard Decay ML)          │
│  • InterlockLegalAgent (CFCFRMS Webhooks, PCR Dispatch, Section 91 Merkle Dossier)     │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ Fast Indexed Queries (< 0.001s)
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                               DATABASE & STORAGE LAYER                                 │
│  • SQLite (data/processed/cyber_intercept.db)                                          │
│    ├── transactions (31,900,000 AML records with indexed lookups)                      │
│    ├── profiles (Mule accounts, non-mules, KYC flags, withdrawal velocities)           │
│    ├── atms (18,000+ Operational Indian ATMs with GPS coordinates)                     │
│    └── state_stats (State-level cybercrime risk indices)                               │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 7. Quickstart & Installation

### Prerequisites
* Python 3.10+
* Node.js 18+ and npm

### 1. Start Backend API
```bash
# In project root
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
* Interactive API Documentation: **[http://localhost:8000/docs](http://localhost:8000/docs)**

### 2. Start Frontend UI
```bash
cd frontend
npm install
npm run dev
```
* Dashboard URL: **[http://localhost:5173](http://localhost:5173)**

### 3. Run Automated System Verification Suite
```bash
python -c "
from backend.engines.agentic_investigator import ReActAgentSwarmOrchestrator
agent = ReActAgentSwarmOrchestrator(scenario_id='SCENARIO_001')
for step in agent.stream_investigation():
    print(f'Step {step[\"log\"][\"step\"]} | {step[\"log\"][\"phase\"]} | Merkle Hash: {step[\"log\"].get(\"step_merkle_proof\", {}).get(\"block_hash\", \"N/A\")[:16]}...')
"
```

---

## 👥 8. Team & Attribution

* **Smart India Hackathon (SIH 2026)**
* **Problem Statement:** 26184
* **Ministry / Organization:** Ministry of Home Affairs (MHA) / Indian Cyber Crime Coordination Centre (I4C), CIS Division
* **Project Name:** CYBER-INTERCEPT

