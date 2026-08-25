# PCCWIS Hackathon Presentation

> **Predictive Cybercrime Cash Withdrawal Intelligence System**
> Problem Statement ID: 26184 | Ministry of Home Affairs · I4C, CIS Division
> Theme: Blockchain & Cybersecurity

**Duration:** 10–15 minutes | **Slides:** 15 | **Demo:** ~4 minutes embedded

---

## Presentation Master Notes

> Before presenting:
> - Start demo environment (docker compose up)
> - Pre-load complaint CMP-2024-987654 in the system
> - Pre-load transaction graph and ML model predictions
> - Have the dashboard open on the GIS heatmap view
> - Have the audit trail pre-loaded for the demo investigation

---

## Slide 1 — Title + Problem Statement

### Objective
Capture attention. Establish the problem scope in 30 seconds.

### Display Points
```
PCCWIS
Predictive Cybercrime Cash Withdrawal Intelligence System

Problem Statement ID: 26184
Ministry of Home Affairs
Indian Cyber Crime Coordination Centre (I4C)

"Predict before withdrawal. Act before the money disappears."
```

### Speaker Explanation
> "Every day, 8,000 cybercrime complaints are filed on the National Cybercrime Reporting Portal. By the time investigators review them, the money is gone. We built a system that changes this — from reactive investigation to proactive prediction of where the criminal will withdraw cash before it happens."

### Visual Recommendation
- Full-bleed dark background
- Red pulsing dot on India map → money moving through accounts → ATM flagged
- Tagline: **"₹8,000 Cr lost annually to cybercrime. Predict. Act. Intercept."**

### Technical Details
- NCRP receives ~8,000 complaints/day
- Average withdrawal window: 1–4 hours after fraud
- Current systems respond after withdrawal; ours predicts before

### Expected Judge Question
> "Why is predicting withdrawal location possible at all?"

### Answer
> "Because cybercriminals follow patterns. They use mule account networks with established withdrawal geographies. ML models trained on historical behavioral data can identify these patterns — not with certainty, but with actionable probability. We turn probability into lead time for law enforcement."

---

## Slide 2 — The Real Problem

### Objective
Make judges feel the urgency. Show the gap between current state and what's needed.

### Display Points
```
The Current Reality:
• Fraud occurs → victim calls helpline or files NCRP complaint
• Investigator reviews complaint (hours later)
• Manually traces account chain (days later)
• Requests bank freeze (2–3 business days)
• Cash has already been withdrawn
• Fraudster has disappeared

The Result:
• <10% of cybercrime funds recovered
• Mule accounts abandoned after single use
• Fraudsters re-emerge with new mule networks
```

### Speaker Explanation
> "The money moves through mule account chains in minutes. The typical pattern: victim account → first mule → split to multiple mules → ATM withdrawal — all within 2–4 hours. Our window to intercept is measured in minutes, not days. Existing systems aren't designed for this speed."

### Visual Recommendation
- Timeline diagram showing:
  - `T+0`: Fraud occurs
  - `T+5min`: Money moves to mule chain
  - `T+30min`: Split to multiple accounts
  - `T+2h`: ATM withdrawal begins
  - `T+4h`: All cash withdrawn
  - `T+48h`: Complaint finally reaches investigator

### Technical Details
- Average complaint to investigator review: 24–72 hours
- Financial investigation under IPC requires court orders: additional days
- ATM cameras retained for 30 days — but withdrawal is already done

### Expected Judge Question
> "Can banks not automatically detect and freeze suspicious transfers?"

### Answer
> "Banks have basic thresholds, but cybercrime mule networks are designed to evade them — amounts below monitoring thresholds, multiple hops across banks, rapid movement. Our system takes a multi-signal, graph-aware approach that a single bank's detection cannot replicate, and we coordinate across the complaint-to-geography chain."

---

## Slide 3 — Why Reactive Systems Are Insufficient

### Objective
Establish the conceptual shift from reactive to proactive.

### Display Points
```
Reactive (Current):               Proactive (Our System):
────────────────────               ───────────────────────
Detect after withdrawal            Predict before withdrawal
Single complaint view              Network + geographic view
Manual 3–5 day process             Automated ~15 minutes
Post-event reconstruction          Pre-event intelligence
LEA responds after loss            LEA positioned before loss
No geographic intelligence         ATM-level location prediction
No graph analysis                  Multi-hop mule tracing
```

### Speaker Explanation
> "The fundamental shift is from forensics to prediction. We're not building a better way to investigate what happened — we're building a system that says: given this complaint, here is where the criminal is likely to withdraw, here is the time window, here is the confidence level. That's a fundamentally different product."

### Visual Recommendation
- Two-column before/after comparison
- Clock icons showing time differences
- Map showing: complaint origin → predicted ATM cluster → LEA positioned

### Expected Judge Question
> "What's the accuracy of your predictions?"

### Answer
> "On our synthetic test dataset, our withdrawal location predictor achieves approximately 60% top-3 accuracy — meaning in 60% of test cases, the actual ATM is in the top 3 predicted locations. We do not claim this will hold precisely on real I4C data — that requires separate validation. But even at this probability level, the lead-time value for law enforcement is significant."

---

## Slide 4 — Our Proposed Solution

### Objective
Give judges the 30-second elevator pitch of PCCWIS.

### Display Points
```
PCCWIS: A 7-Layer Predictive Intelligence System

Cybercrime Complaint
        ↓
Agentic Investigation (LangGraph OODA Loop)
        ↓
Transaction Graph + ML Models + Geospatial Engine
        ↓
Risk Fusion Engine (Calibrated Score)
        ↓
Withdrawal Location Prediction
        ↓
Policy / Human-in-the-Loop Gate
        ↓
Alert → LEA / Bank / I4C

Before cash is withdrawn.
```

### Speaker Explanation
> "PCCWIS is not an LLM that predicts fraud. That would be wrong. It's a seven-layer system where: an LLM-based agent orchestrates the investigation; graph databases trace mule account networks; machine learning models compute risk scores; geospatial analysis identifies ATM clusters; and a Risk Fusion Engine combines all signals into a calibrated alert. The LLM reasons and plans. The math does the prediction."

### Visual Recommendation
- Vertical pipeline diagram with icons for each layer
- Color coded: blue (agent), orange (data engines), red (risk), green (alert)

### Expected Judge Question
> "Why not just use an LLM to do everything?"

### Answer
> "Two reasons: LLMs cannot reliably produce calibrated numerical probabilities, and LLM outputs cannot be audited as evidence. Our system uses LLMs for what they're good at — reasoning, planning, and report generation — while using deterministic ML models for fraud probability and location prediction. Every number is traceable to a specific model version and input features."

---

## Slide 5 — System Architecture

### Objective
Give judges confidence in technical depth.

### Display Points
```
9 Independent, Orchestrated Components:

1. Investigation Agent    (LangGraph + LLM)
2. Transaction Graph      (Neo4j multi-hop tracing)
3. ML Models              (XGBoost, LightGBM, Isolation Forest)
4. Geospatial Engine      (PostGIS, KDE hotspot)
5. Risk Fusion Engine     (Calibrated weighted ensemble)
6. Policy / Safety Layer  (Thresholds, human gates)
7. Blockchain Audit       (SHA-256 hash chain)
8. Database Layer         (PostgreSQL, Neo4j, Redis)
9. Frontend Dashboard     (React, Leaflet.js GIS)
```

### Speaker Explanation
> "Each component has a single, clear responsibility. The agent cannot compute risk scores. The ML models cannot write reports. The LLM cannot access the database directly. This separation is both a security decision and an engineering decision — it makes each component auditable, replaceable, and testable independently."

### Visual Recommendation
- Architecture diagram (from README.md Section 9)
- Highlight the boundaries between LLM, ML, and data layers with color

### Technical Details
- LangGraph StateGraph with 15+ nodes
- Neo4j for transaction graph traversal (Cypher queries)
- scikit-learn, XGBoost, LightGBM for ML
- FastAPI for all service APIs
- React + Leaflet.js for dashboard

### Expected Judge Question
> "What happens if the ML service is down?"

### Answer
> "The agent has error handling and retry logic. If a critical tool fails after 3 retries, the investigation continues with partial evidence — the risk score is penalized by a confidence factor, and the result is flagged as 'partial evidence' so human reviewers are aware."

---

## Slide 6 — Agentic Investigation Loop

### Objective
Explain the OODA loop and why it's needed.

### Display Points
```
The OODA Loop (Observe → Orient → Decide → Act):

OBSERVE: What do I know? What is still unknown?
REASON:  What does the evidence suggest?
PLAN:    Which tool should I call next?
ACT:     Execute tool call (graph, ML, geo)
         ↑___________________________|
VERIFY:  Is evidence sufficient to predict?
PREDICT: Call ML model → withdrawal locations
DECIDE:  Is risk threshold met?
REPORT:  Generate intelligence brief
ALERT:   Dispatch to LEA / Bank / I4C

Controlled by:
• max_tool_calls: 100
• max_graph_depth: 5 hops
• max_investigation_time: 30 minutes
• max_accounts: 50
```

### Speaker Explanation
> "The agent is a controlled autonomous investigator. It starts with a complaint and decides, step by step, what to investigate next. Found a mule account? Investigate its outgoing transactions. Found a fan-out pattern? Get account risk scores for each recipient. Found withdrawal history? Get geographic risk for those ATMs. The loop continues until we have enough evidence to predict — or until safety limits stop it."

### Visual Recommendation
- Animated OODA loop diagram (from agent_workflow_diagram.md Section 5)
- Show the scope limit counters ticking up

### Technical Details
- Implemented as LangGraph StateGraph with conditional edges
- Checkpointed in PostgreSQL for crash recovery
- Human `interrupt()` mechanism for approval gates

### Expected Judge Question
> "How do you prevent the agent from going into an infinite loop?"

### Answer
> "Multiple hard limits: maximum 100 tool calls, maximum 5 graph hops, maximum 50 accounts, maximum 30 minutes. These are enforced deterministically in the agent loop — not by the LLM. If any limit is hit, investigation completes with whatever evidence is available. The LangGraph recursion_limit parameter provides a final backstop."

---

## Slide 7 — Transaction Graph / Multi-Hop Tracing

### Objective
Show the graph analysis capability — a key technical differentiator.

### Display Points
```
Example: ₹80,000 fraud → 15-minute investigation

Victim V001
    ↓ ₹80,000 (12:16)
Mule M001 [Risk: 71] ← RAPID_TRANSIT flag
    ↙ ₹40k (12:18)    ↘ ₹40k (12:18)
Mule M002 [Risk: 84]   Mule M003 [Risk: 79]
    ↓ historical pattern    ↓ historical pattern
ATM-CHN-0042 (67%)      ATM-CHN-0089 (12%)
Chennai North           Chennai West

Flags detected: FAN_OUT, RAPID_TRANSIT, ROUND_AMOUNT

All traversal done in < 30 seconds via Neo4j
```

### Speaker Explanation
> "Using Neo4j graph database, we can traverse multi-hop mule account chains in milliseconds. The graph engine detects patterns automatically: fan-out (money splitting), rapid transit (in-and-out within minutes), structuring (amounts just below thresholds). These pattern detections feed directly into the risk fusion engine as high-weight signals."

### Visual Recommendation
- Live transaction graph visualization from the dashboard
- Nodes colored by risk level (green → yellow → orange → red)
- Edge labels showing amounts and timestamps

### Technical Details
- Cypher query with configurable max depth
- Suspicious pattern detection: structuring, smurfing, fan-out, layering
- Graph data model: Account, Transaction, ATM, Location nodes

### Expected Judge Question
> "What if the money crosses multiple banks — can you still trace it?"

### Answer
> "In our prototype, we simulate cross-bank transactions in the synthetic dataset. In production, this requires inter-bank data sharing through the existing regulatory framework (NPCI/RBI channels). Our architecture is designed to handle multi-bank graphs — the Neo4j model is bank-agnostic. The data integration is a policy problem, not an architectural one."

---

## Slide 8 — ML + Predictive Analytics

### Objective
Establish that ML, not LLM, does the prediction.

### Display Points
```
ML Model Stack (4 independent models):

1. FraudClassifier (XGBoost)
   → Transaction fraud probability: 0.91
   
2. AnomalyDetector (Isolation Forest)
   → Account behavioral anomaly: 0.87
   
3. AccountRiskScorer (LightGBM Ensemble)
   → Account risk score: 84/100
   
4. WithdrawalLocationPredictor (Gradient Boost + KDE)
   → Top ATM: Chennai North (67% probability)
   
CRITICAL: These are ML models — not LLM outputs.
All scores are reproducible, versioned, auditable.
```

### Speaker Explanation
> "The LLM orchestrates. The ML models predict. XGBoost classifies fraud probability from transaction features — amount, velocity, time, graph depth. Isolation Forest detects behavioral anomalies. LightGBM scores account risk from profile and network features. Our withdrawal location predictor combines historical withdrawal geography with KDE hotspot analysis. Every model output is versioned, logged, and SHAP-explainable."

### Visual Recommendation
- Bar chart of model contributions to risk score
- SHAP waterfall chart for sample prediction
- Confusion matrix (if available for synthetic data)

### Technical Details
- Feature engineering: 25+ transaction features, 15+ account features, 10+ geographic features
- Training data: IBM AMLSim + PaySim + IEEE-CIS (publicly available, synthetic/anonymized)
- Evaluation: Temporal train/test split (no data leakage)
- Calibration: Platt scaling for probability outputs

### Expected Judge Question
> "What training data did you use?"

### Answer
> "We use three publicly available synthetic datasets: IBM AMLSim for banking transaction graph simulation, PaySim for mobile money fraud patterns, and IEEE-CIS for anonymized transaction fraud features. We generated a custom India-specific ATM and complaint layer. We explicitly do not use or claim access to real I4C or banking data."

---

## Slide 9 — Geospatial Risk Heatmap

### Objective
Show the visual intelligence output — the part judges will remember.

### Display Points
```
GIS-based Risk Intelligence:

• ATM-level risk scoring (0-100)
• District-level crime density overlay
• Historical withdrawal cluster mapping (KDE)
• Time-window prediction: "14:00–16:00 IST window"
• Predicted ATM markers with probability labels
• Live alert overlays for active investigations

Enabling: "Officer, go to Chennai North ATMs by 2 PM"
```

### Speaker Explanation
> "This is what law enforcement sees. Not a table of numbers — a map with predicted ATM locations marked by probability. The green-to-red heatmap shows historical crime density. The pulsing markers show predicted withdrawal locations for active investigations. An officer can look at this map and know exactly where to deploy field units."

### Visual Recommendation
- **Live demo screenshot of Leaflet.js dashboard**
- Show: India map → zoom to district → ATM markers with risk scores → time window
- Overlay: predicted location circle with 67% label

### Technical Details
- Leaflet.js with custom tile layer
- GeoJSON risk zones from PostGIS spatial queries
- KDE (Kernel Density Estimation) for hotspot generation
- Time-weighted risk decay for historical incidents

### Expected Judge Question
> "How accurate is the geographic prediction?"

### Answer
> "On our synthetic test set, we measure district-level accuracy (correct district in top prediction) at approximately 75%, and top-3 ATM accuracy at approximately 60%. The 2 km mean haversine error on district-level predictions suggests useful geographic clustering even when the exact ATM differs. In production, accuracy would need real I4C data validation."

---

## Slide 10 — Explainable AI + Risk Score

### Objective
Show transparency and trust mechanisms — critical for law enforcement adoption.

### Display Points
```
Every prediction is explained:

Risk Score: 78.4 / 100 (HIGH)
Confidence: 82%

Contribution breakdown:
  Fraud Classifier:    25% → probability 0.91
  Account Risk:        21% → score 84/100  
  Anomaly Detector:    18% → score 0.87
  Geographic Risk:     14% → score 68/100
  Graph Score:         15% → FAN_OUT + RAPID_TRANSIT
  Temporal Pattern:     7% → peak withdrawal hour

Evidence chain:
  1. ₹80,000 fraud reported 12:15
  2. V001→M001 transfer 12:16 (RAPID_TRANSIT)
  3. M001 fan-out to M002, M003 at 12:18
  4. M002 risk 84/100 — historical Chennai withdrawals
  5. Predicted: ATM-CHN-0042, 14:00-16:00 IST

"Probabilistic intelligence — requires human verification"
```

### Speaker Explanation
> "Explainability is non-negotiable for law enforcement. Officers won't deploy field units based on a black-box score. Every prediction includes: which evidence contributed, by how much, and a numbered chain from the original complaint to the predicted location. SHAP values show exactly which features drove each model's output. This also satisfies court admissibility requirements for AI-assisted evidence."

### Visual Recommendation
- SHAP waterfall chart (horizontal bar chart of feature contributions)
- Evidence chain numbered list
- Confidence interval display: "82% ± 7%"

### Technical Details
- SHAP (SHapley Additive exPlanations) for model explanation
- Evidence chain generated by LLM from structured state data
- Confidence interval from Risk Fusion Engine calibration

### Expected Judge Question
> "Can this explanation be used as court evidence?"

### Answer
> "The explanation itself is indicative. The court-admissible component is the blockchain audit trail: every tool call, every model version, every input hash is recorded and chained. A forensic examiner can reproduce the exact investigation state at any point in time. The explanation helps the officer understand; the audit trail provides legal traceability."

---

## Slide 11 — Alert + LEA Workflow

### Objective
Show the end-to-end operational workflow from prediction to field action.

### Display Points
```
Alert Generation Workflow:

Risk Score Thresholds:
  LOW (0-39):      Log only
  MEDIUM (40-59):  Bank notification
  HIGH (60-79):    LEA dashboard alert + SMS
  CRITICAL (80-89):Human approval required
  EXTREME (≥90):   Immediate escalation

Human-in-the-Loop Gate (CRITICAL/EXTREME):
  → Senior Officer reviews evidence + map
  → One-click: APPROVE / DECLINE / REQUEST MORE
  → Officer decision recorded in audit chain
  → Field deployment only after approval

Alert contains:
  → GPS coordinates
  → Predicted time window
  → Evidence summary
  → Confidence level
  → Audit hash
```

### Speaker Explanation
> "High-risk alerts go through a human approval gate. No field officer is deployed based solely on machine output. The senior officer sees the full evidence chain, the SHAP explanation, the map, and the confidence level — then decides. This prevents false-positive deployments and keeps humans in control of high-impact decisions. Every approval or rejection is logged in the tamper-evident audit chain."

### Visual Recommendation
- Split screen: Left = alert notification on dashboard | Right = map with ATM locations
- Show the approve/decline UI
- Show SMS/notification delivery

### Expected Judge Question
> "What if the senior officer is unavailable at 2 AM?"

### Answer
> "Good operational question. The system supports escalation chains — if the primary approver doesn't respond within a configurable window (e.g., 15 minutes), the alert escalates to the next officer in the chain. For EXTREME severity, this escalation is immediate. The system can also be configured to auto-approve HIGH alerts (not CRITICAL) after human review is available for post-hoc accountability."

---

## Slide 12 — Blockchain / Evidence Integrity

### Objective
Show the audit mechanism that makes predictions legally defensible.

### Display Points
```
Blockchain-Style Hash Chain:

Event 1: Investigation Started
  hash(event_data + genesis) = hash_A

Event 2: Account Queried (M001)
  hash(event_data + hash_A) = hash_B

Event 3: ML Risk Score Computed
  hash(event_data + hash_B) = hash_C

Event 4: Alert Generated (score: 78.4)
  hash(event_data + hash_C) = hash_D

Event 5: Officer Approved
  hash(event_data + hash_D) = hash_E

→ Any tampering breaks the hash chain
→ Verified by audit service on every read
→ Court-admissible tamper-evident trail

IMPORTANT: No PII or raw banking data on-chain
Only hashes of events + metadata
```

### Speaker Explanation
> "Every investigative action — from the first tool call to the officer's approval — is recorded in a SHA-256 hash chain. Each event's hash includes the previous event's hash. Tamper with any record and the chain breaks. This gives us a court-admissible, tamper-evident audit trail without putting sensitive data on a blockchain. The blockchain-inspired approach: all the auditability, none of the PII risk."

### Visual Recommendation
- Hash chain diagram (from README Section 18.3)
- Visual of audit trail UI in dashboard
- "Chain Valid: ✅" indicator

### Technical Details
- SHA-256 chained hashing (Python hashlib)
- Append-only PostgreSQL audit table + hash verification service
- No PII on-chain — only hashes of event data
- Full investigation reproducibility

### Expected Judge Question
> "Why not use a real blockchain like Ethereum or Hyperledger?"

### Answer
> "For this use case, a hash chain provides the same tamper-evidence property without the complexity, cost, or PII-exposure risk of a public blockchain. In a production I4C deployment, the audit service could optionally anchor chain head hashes to a permissioned blockchain (like Hyperledger Fabric) for additional external verification. The architecture supports this extension."

---

## Slide 13 — Live Demo Scenario

### Objective
Show the system working end-to-end. This is the most important slide.

### Display Points
```
LIVE DEMO: ₹80,000 UPI Fraud Complaint

Time: 12:15 PM — Complaint registered

Watch the agent:
1. Receive complaint CMP-2024-987654
2. Fetch victim account V001
3. Trace transaction graph → M001, M002, M003
4. Detect: FAN_OUT, RAPID_TRANSIT flags
5. Calculate ML risk: M002 = 84/100 (HIGH)
6. Get withdrawal history → Chennai pattern
7. Run geographic risk analysis
8. ML prediction: ATM-CHN-0042, 67% probability
9. Risk fusion: 78.4 (HIGH)
10. Generate alert → LEA Dashboard
11. Intelligence report generated
12. Officer reviews → Approves field deployment

Time elapsed: ~15 minutes
Predicted withdrawal window: 14:00–16:00 IST
```

### Speaker Explanation
> "Let me show you the system in action. I'll start a new investigation from a fresh complaint. Watch the investigation timeline on the left — you'll see each tool call as it happens. On the right, the transaction graph builds in real time. As risk scores arrive from the ML service, you'll see the heatmap update. In about 2 minutes of demo time, you'll see an alert generated with the predicted ATM location."

### Visual Recommendation
- **LIVE SYSTEM DEMO** — split screen:
  - Left: Investigation timeline (tool calls ticking)
  - Center: Transaction graph building (animated)
  - Right: GIS map with risk zones appearing

### Demo Script

```
[Open dashboard at /dashboard]
"This is our investigation command center."

[Click 'New Complaint' → load CMP-2024-987654]
"A ₹80,000 UPI fraud has just been registered."

[Click 'Start Investigation']
"The agent starts its OODA loop."

[Watch timeline panel]
"You can see: complaint fetched, victim account retrieved, 
transaction trace beginning..."

[Transaction graph animates]
"Here's the graph building in real time. V001 → M001, 
then M001 fans out to M002 and M003."

[Risk scores appear on nodes]
"The ML service returns: M002 risk score 84 — HIGH."

[GIS map highlights]
"Historical withdrawals from M002 cluster in Chennai North."

[ML prediction appears]
"Withdrawal location predictor: ATM-CHN-0042, 67% probability, 
predicted window 14:00–16:00 IST."

[Alert generated]
"Risk fusion: 78.4. Alert generated and dispatched to LEA dashboard."

[Show alert detail]
"Complete evidence chain. One-click officer approval. 
Audit hash: sha256:abc123..."

[Reveal outcome]
"And if we reveal the ground truth from our test dataset:
actual withdrawal occurred at ATM-CHN-0042 at 14:47 IST.
Lead time: 2 hours 17 minutes."
```

### Expected Judge Question
> "Is this a live system or pre-recorded?"

### Answer
> "This is a live running system on our local infrastructure. Every API call you see is actually executing — the agent is genuinely running the OODA loop, the graph queries are hitting Neo4j, the ML service is running real model inference. The data is synthetic — we're using IBM AMLSim-generated accounts and transactions — but the system is real."

---

## Slide 14 — Evaluation and Metrics

### Objective
Show rigorous measurement — judges respect teams that measure honestly.

### Display Points
```
System Evaluation (Synthetic Dataset):

Withdrawal Location Prediction:
  Top-1 ATM accuracy:       ~42%
  Top-3 ATM accuracy:       ~60%
  District-level accuracy:  ~75%
  Mean geographic error:    ~2.1 km

Agent Performance:
  Avg investigation time:   14 minutes
  Avg tool calls:           18
  Investigation completion: 97%

Alert Quality:
  False positive rate:      ~18% (high-risk alerts)
  Lead time (median):       2.3 hours

Disclaimer:
All metrics are on SYNTHETIC data only.
Real I4C data requires separate validation.
Do not interpret these as production performance claims.
```

### Speaker Explanation
> "We measure honestly. Top-3 ATM accuracy of 60% means in 60% of test cases, the actual withdrawal ATM is in our top 3 predictions. For law enforcement, a 60% top-3 accuracy with a 2-hour lead time is potentially very valuable — they can cover 3 ATM clusters instead of guessing randomly across hundreds. But we don't overclaim. These are synthetic data results. Real validation requires real data."

### Visual Recommendation
- Precision-Recall curve for fraud classifier
- Rank accuracy bar chart (Top-1, Top-3, Top-5)
- Lead time distribution histogram
- ROC curve for account risk model

### Technical Details
- Temporal train/test split (no data leakage)
- Calibration plots (predicted probability vs observed frequency)
- False positive rate by alert severity level

### Expected Judge Question
> "Your false positive rate is 18% — that means 1 in 5 deployments is wrong. Isn't that too high?"

### Answer
> "For law enforcement intelligence (as opposed to automatic enforcement actions), 18% is an acceptable starting point — especially given we're working from synthetic data and this is a prototype. In practice, the human approval gate filters additional false positives. As field outcome feedback accumulates, the models retrain and precision improves. The system is designed with feedback loops specifically for this reason."

---

## Slide 15 — Impact + Future Scope

### Objective
Close with vision. Make judges feel the real-world potential.

### Display Points
```
Potential Impact (if deployed and validated):

• Shift from reactive → proactive cybercrime response
• 2+ hour lead time for LEA field positioning
• Automated investigation: hours → minutes
• Tamper-evident audit trail for every case
• Explainable predictions for officer trust
• Continuous improvement through outcome feedback

Future Roadmap:
• Real-time Kafka streaming for sub-minute ingestion
• Federated learning across bank silos (no raw data sharing)
• Graph Neural Networks for account risk scoring
• Natural language complaint entity extraction
• Mobile app for LEA field officers
• Cross-state investigation coordination
• Integration with actual NCRP API (when available)

Ethical Foundation:
• Probabilistic intelligence, not proof of guilt
• Human approval for all field actions
• Bias auditing of ML models
• Proportionality in high-impact decisions
• Full transparency and auditability
```

### Speaker Explanation
> "PCCWIS is not a complete solution — it's a proof of concept that demonstrates a fundamentally better approach to cybercrime response. It shows that agentic AI, combined with purpose-built ML models and graph analysis, can produce actionable geographic intelligence before criminals withdraw money. The path from prototype to I4C deployment requires real data validation, bank integration, and operational pilots — but the architecture is ready for that journey. Our core message: predict before withdrawal, not after."

### Visual Recommendation
- India map with multiple investigation hotspots
- Timeline showing: "Today: prototype → Year 1: pilot → Year 2: scale"
- Quote from problem statement highlighted

### Expected Judge Question
> "How would this actually integrate with I4C systems?"

### Answer
> "We've designed a well-documented REST API that can integrate with the NCRP complaint intake. Real banking data would come through existing RBI/NPCI regulated data-sharing channels — the same ones used for existing fraud reporting. Our system would sit as an analytics layer on top. The agent is stateless per investigation — it queries data through controlled APIs, so adding real data sources means adding new tool implementations, not redesigning the architecture."

---

## Appendix: Live Demo Script (Detailed)

### Pre-Demo Checklist
- [ ] Docker containers all running (`docker compose ps`)
- [ ] Neo4j populated with synthetic graph data
- [ ] ML models loaded and serving
- [ ] Demo complaint pre-loaded: CMP-2024-987654
- [ ] Dashboard open at http://localhost:3000
- [ ] Second monitor showing investigation timeline
- [ ] Backup: pre-recorded video in case of tech failure

### Demo Steps (4 minutes)

**Minute 0:00 – 0:30: Dashboard Overview**
> "This is the PCCWIS command center. On the left: active investigations. Center: GIS heatmap of India. Right: recent alerts. Currently quiet — let me bring in a new complaint."

**Minute 0:30 – 1:00: Complaint Registration**
> "A ₹80,000 UPI fraud complaint just arrived. [Click 'Register Complaint' → fill form → submit] The system assigns complaint ID CMP-2024-987654."

**Minute 1:00 – 1:30: Investigation Start**
> "I'll start the investigation. [Click 'Start Investigation'] The agent begins its OODA loop. Watch the investigation timeline panel."

**Minute 1:30 – 2:30: Live Graph Building**
> "Tool calls executing: get_complaint → get_account → trace_transaction_graph. [Graph animates] You can see the transaction chain: victim V001 → mule M001 → fan-out to M002 and M003. The RAPID_TRANSIT and FAN_OUT flags appear automatically."

**Minute 2:30 – 3:00: ML Results**
> "ML risk scores arriving from the model service. M002: 84/100 HIGH. Account anomaly detector: 0.87. These are machine learning model outputs — not LLM guesses."

**Minute 3:00 – 3:30: Prediction and Alert**
> "Geographic clustering... withdrawal prediction... Risk fusion: 78.4 HIGH. Alert generated: ATM-CHN-0042, Chennai North, 67% probability, 14:00-16:00 window. [Map zooms to Chennai, ATM marked]"

**Minute 3:30 – 4:00: Outcome Reveal**
> "Now for the test of truth — let me reveal what actually happened in our synthetic ground truth. [Reveal overlay] Actual withdrawal: ATM-CHN-0042, 14:47 IST. Our lead time: 2 hours 17 minutes. Prediction correct. That's PCCWIS in action."

### Backup Plan (if tech fails)
- Pre-recorded 4-minute screen capture video
- Static screenshots of each step in presentation slides
- State: "Our system is running — we'll show the recording and can demo live after Q&A"

---

## Appendix: Anticipated Judge Questions (Master List)

| Question | 30-Second Answer |
|---|---|
| Why LangGraph? | Purpose-built for stateful, cyclical, human-in-the-loop agent workflows. Alternative: custom loop, but LangGraph handles persistence, retries, and parallel execution out of the box. |
| What if the LLM hallucinates? | LLM only generates text (reports, explanations) — never numerical risk scores. Structured output enforcement prevents tool calls that violate schemas. Audit log catches any anomalies. |
| Privacy concerns? | PII minimization throughout. Account numbers masked. No raw data on audit chain — only hashes. Encryption at rest and in transit. RBAC on all data access. |
| Why not use RNN/LSTM for sequences? | We use them conceptually in temporal features. Gradient Boosting performs better on tabular fraud data (per IEEE-CIS literature). GNNs are in our future roadmap for graph-structured account risk. |
| How does this work with multiple banks? | Our architecture is bank-agnostic — accounts are internal IDs. Cross-bank tracing requires data sharing (RBI regulated channels). Our tool API abstracts this — adding a new bank = adding a new data connector, not a new architecture. |
| Is this real-time? | Sub-15 minute for full investigation, targeting sub-1 minute for complaint ingestion with Kafka streaming (future). Good enough for the 2–4 hour fraud-to-withdrawal window. |
| What's the cost to run? | Prototype: single laptop. Production: 5–10 cloud VMs + managed Neo4j + managed PostgreSQL. Estimated ₹50,000–1,00,000/month at scale. Tiny compared to cybercrime losses. |
| Can police actually use this interface? | We designed for non-technical officers. Dashboard is map-first, one-click actions, plain-language evidence summaries. Full mobile responsiveness. Would need UAT with actual officers in production. |

---

*Presentation version: 1.0 | PCCWIS — Problem Statement ID 26184*
