# 🛡️ Cyber-Craft — Frontend

> **AI-Powered Cybercrime Prediction & Intelligence Platform**

Cyber-Craft is a modern cybersecurity intelligence platform designed to support cybercrime analysis, prediction, investigation, threat monitoring, and intelligence-driven decision making.

This repository contains the **frontend application** responsible for the user interface, authentication experience, command center, cybercrime intelligence modules, analytics, reports, alerts, and investigator workflows.

---

## 📌 Overview

The Cyber-Craft frontend provides a centralized interface for monitoring and analyzing cybercrime-related information.

The application is designed around the workflow:

**Predict → Detect → Analyze → Investigate → Respond**

The UI combines:

* Artificial Intelligence
* Cybercrime prediction
* Threat intelligence
* Investigation workflows
* Data analytics
* Alerts and monitoring
* Intelligence reporting

with a professional, enterprise-oriented cybersecurity interface.

---

# ✨ Features

## 🏠 Landing Page

The landing page introduces the Cyber-Craft platform with:

* Government/cybersecurity-oriented visual identity
* AI-powered cybercrime messaging
* Hero section
* Platform overview
* Navigation to the Command Center
* Responsive design

---

## 🔐 Authentication

### Login

```text
/login
```

Features:

* Professional authentication interface
* Blurred Home-page background
* Secure-looking cybersecurity visual design
* Email/password form
* Authentication handling
* Navigation to the main platform

### Register

```text
/register
```

Features:

* User registration interface
* Full name
* Email
* Password
* Confirm password
* Authentication integration
* Login navigation

Both authentication pages use the same visual design system.

---

# 🖥️ Command Center

```text
/command-center
```

The Command Center is the primary operational dashboard.

It provides an overview of the cybercrime intelligence environment through:

* Key statistics
* Threat information
* Prediction insights
* Analytics
* Risk indicators
* Alerts
* Intelligence information
* Data visualizations

The dashboard is designed to provide investigators with a quick understanding of the current cybersecurity situation.

---

# 🚨 Live Alerts

```text
/alerts
```

Provides an interface for monitoring active cybercrime/security alerts.

The interface supports:

* Alert visibility
* Severity indicators
* Critical/warning states
* Alert information
* Investigation-oriented navigation

---

# 🗺️ Intelligence Map

```text
/intelligence-map
```

Provides a geographic intelligence interface for visualizing cybercrime-related information and locations.

---

# 📄 Complaints

```text
/complaints
```

Provides access to complaint/case information.

The interface is designed for:

* Viewing complaints
* Reviewing case information
* Navigating investigation workflows

---

# ➕ New Complaint

```text
/complaints/new
```

Provides the interface for submitting a new cybercrime complaint/case.

The form follows the project's common input, validation, button, and card design system.

---

# 🔍 Investigation

```text
/investigation
```

Provides an investigator-oriented interface for reviewing and analyzing cybercrime cases.

---

# ⚖️ Legal Dossier

```text
/dossier
```

Provides access to legal/investigation dossier information associated with cases.

---

# 📁 Audit Trail

```text
/audit
```

Provides an audit-oriented view of system/investigation activity.

---

# 📊 Intelligence Reports

```text
/reports
```

Provides access to intelligence and analytical reporting.

The interface is designed for presenting structured cybercrime insights and report information.

---

# 🖥️ System Monitoring

```text
/system
```

Provides system-level monitoring information and operational status.

---

# 🎨 Design System

Cyber-Craft follows a consistent **AI + Cybersecurity + Enterprise Intelligence** visual language.

## Primary Colors

### Light surfaces

```text
#FFFFFF
#F7FBFF
#F0F7FC
#E8F3FA
```

### Professional Blue

```text
#2563EB
#1D4ED8
```

### Cyber Cyan

```text
#06B6D4
```

### Deep Navy

```text
#081A2F
#0B1F33
#0F2747
```

### Semantic Colors

```text
Safe / Low       → Green
Warning / Medium → Amber
Critical / High  → Red
AI / Prediction  → Blue / Cyan
```

Colors should be reused through the existing design tokens rather than creating unrelated colors for individual components.

---

# 🧭 Navigation

The main navigation is organized into operational sections.

```text
COMMAND
├── Command Center
├── Live Alerts
└── Intelligence Map

INVESTIGATION
├── Complaints
├── New Complaint
└── Investigation

INTERVENTIONS
├── Legal Dossier
└── Audit Trail

REPORTS & SYSTEM
├── Intelligence Reports
└── System Monitoring
```

The sidebar supports a professional **expanded/collapsed navigation experience**.

### Expanded

Displays:

* Icons
* Navigation labels
* Section headings

### Collapsed

Displays:

* Navigation icons
* Tooltips
* More dashboard workspace

### Responsive

On smaller screens, the navigation behaves as an off-canvas/drawer interface.

---

# 🧩 Frontend Architecture

The frontend follows a component-based React architecture.

Conceptually:

```text
User
 │
 ▼
React Application
 │
 ├── Pages
 │
 ├── Reusable Components
 │
 ├── Layout
 │
 ├── Routing
 │
 └── Services / API Layer
 │
 ▼
Backend API
 │
 ▼
Application Data / ML Services
```

The frontend is responsible for presentation, user interaction, routing, authentication UI, API communication, and visualization.

Business logic and data processing should remain in the appropriate backend/service layer.

---

# 📂 Project Structure

The exact structure may evolve as development continues, but the frontend follows this general organization:

```text
frontend/
│
├── public/
│
├── src/
│   │
│   ├── assets/
│   │
│   ├── components/
│   │
│   ├── pages/
│   │
│   ├── services/
│   │
│   ├── layouts/
│   │
│   ├── routes/
│   │
│   ├── styles/
│   │
│   ├── App.*
│   └── main.*
│
├── package.json
├── vite.config.*
├── tsconfig.*
└── README.md
```

> The actual folder structure should always be treated as the source of truth when adding new modules.

---

# 🔌 Frontend ↔ Backend Flow

The frontend communicates with the backend through the existing API/service layer.

General flow:

```text
User Action
     │
     ▼
React Component
     │
     ▼
Frontend Service / API Layer
     │
     ▼
Backend API
     │
     ├── Database
     │
     └── ML / Prediction Services
     │
     ▼
API Response
     │
     ▼
React State
     │
     ▼
Dashboard / UI
```

Do not bypass the existing API architecture when implementing new functionality.

---

# 🤖 AI / Cybercrime Prediction

The frontend is designed to present AI-driven cybercrime intelligence.

Where prediction functionality is available through the backend, the UI may present information such as:

* Crime category
* Risk level
* Prediction confidence
* Probability
* Threat severity
* Contributing information
* Analytical insights

The frontend must display **real API/model results** when available.

Do not replace model responses with hardcoded values.

---

# 📈 Data Visualization

The dashboard uses visualizations to make cybercrime intelligence easier to understand.

Charts and analytics should follow the same visual language:

```text
Primary → Blue
Secondary → Cyan
Neutral → Light Blue / Gray
Safe → Green
Warning → Amber
Critical → Red
```

Avoid unnecessary rainbow charts or unrelated colors.

---

# 📱 Responsive Design

The frontend is designed for:

* Desktop
* Laptop
* Tablet
* Mobile

Responsive layouts should prevent:

* Horizontal scrolling
* Overlapping cards
* Broken navigation
* Clipped charts
* Overflowing tables
* Header collisions
* Form overflow

Important information should remain accessible across screen sizes.

---

# 🧱 UI Guidelines

When creating new frontend components:

### Use consistent spacing

Prefer existing project spacing variables/tokens.

### Use reusable components

Do not duplicate the same UI implementation unnecessarily.

### Maintain alignment

Cards, headings, charts, tables, and controls should follow the same grid.

### Maintain typography

Use the existing typography hierarchy.

### Maintain colors

Reuse existing design tokens.

### Maintain interaction states

Buttons and controls should have:

* Default
* Hover
* Active
* Disabled
* Loading

states where appropriate.

---

# 🚦 Loading, Error & Empty States

Data-driven components should provide meaningful states.

### Loading

Use a professional loading indicator or skeleton.

### Empty

Explain that no data is currently available.

### Error

Display a useful error message and provide retry functionality where appropriate.

Avoid leaving users with completely blank sections.

---

# ⚙️ Installation

Clone the repository and enter the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

---

# ▶️ Development

Start the development server:

```bash
npm run dev
```

Vite will provide the local development URL in the terminal.

Typically:

```text
http://localhost:5173
```

---

# 🏗️ Production Build

Create a production build:

```bash
npm run build
```

The generated build will be placed in the configured Vite output directory.

---

# 🔍 Preview Production Build

If supported by the current Vite configuration:

```bash
npm run preview
```

---

# 🔐 Environment Variables

Environment-specific configuration should be stored in `.env` files.

Example:

```env
VITE_API_BASE_URL=http://localhost:YOUR_BACKEND_PORT
```

Use the actual variable names defined in the project.

### Important

Never commit:

```text
.env
.env.local
.env.production
```

if they contain secrets, passwords, API keys, tokens, or private credentials.

Use `.env.example` for safe configuration documentation.

---

# 🧪 Frontend Verification

Before considering frontend work complete:

## 1. Run the application

```bash
npm run dev
```

## 2. Test authentication

```text
/login
/register
```

## 3. Test major routes

```text
/command-center
/alerts
/intelligence-map
/complaints
/complaints/new
/investigation
/dossier
/audit
/reports
/system
```

## 4. Check browser console

Look for:

* Runtime errors
* Failed requests
* Broken imports
* React warnings

## 5. Test responsive layouts

Check:

* Desktop
* Laptop
* Tablet
* Mobile

## 6. Run production build

```bash
npm run build
```

The build should complete without genuine compilation errors.

---

# 🛠️ Development Guidelines

Before modifying an existing feature:

1. Understand the current implementation.
2. Check its dependencies.
3. Check whether other pages use the component.
4. Preserve existing functionality.
5. Reuse existing components where possible.
6. Follow the existing design system.
7. Test the affected route.
8. Check the browser console.
9. Run the build.

Avoid unnecessary rewrites of working components.

---

# 🚫 Important Rules

Do not:

* Break existing API integration
* Replace real API responses with fake data
* Remove working routes
* Remove working functionality
* Hardcode authentication credentials
* Commit API keys
* Introduce unnecessary libraries
* Create unrelated color systems
* Redesign completed pages without a requirement
* Push directly to `main`

---

# 🌿 Git Workflow

The project's working branch is:

```text
maitri
```

Check the current branch:

```bash
git branch
```

Switch if required:

```bash
git switch maitri
```

Check changes:

```bash
git status
```

Stage:

```bash
git add .
```

Commit:

```bash
git commit -m "Describe your frontend changes"
```

Push:

```bash
git push origin maitri
```

Do not push frontend work to `main`.

---

# 👥 Team Handoff

When working on the frontend:

### Before coding

Understand:

* Existing routes
* Existing components
* Existing API services
* Existing CSS/design tokens
* Existing authentication flow

### During development

Follow the current:

**White + Ice Blue + Blue + Cyan + Deep Navy**

design system.

### Before handing over

Verify:

```text
✓ Feature works
✓ Existing features still work
✓ API integration works
✓ Responsive layout works
✓ No unnecessary console errors
✓ No layout overflow
✓ Build passes
✓ Documentation updated if necessary
```

---

# 📌 Current Frontend Direction

Cyber-Craft should look and feel like a professional:

> **AI-Powered Cybercrime Prediction & Intelligence Command Platform**

The visual experience should combine:

**Enterprise Dashboard**

*

**Cybersecurity Intelligence**

*

**AI/ML Prediction**

*

**Investigator Workflow**

The design should remain:

* Professional
* Clean
* Trustworthy
* Data-focused
* Modern
* Responsive
* Enterprise-ready

Avoid turning the interface into a generic admin dashboard or neon cyberpunk/hacker interface.

---

# 🚀 Development Philosophy

Every new feature should fit into the existing product ecosystem.

The goal is not simply to add more screens.

The goal is to create a cohesive intelligence platform where investigators can:

**Predict → Detect → Analyze → Investigate → Respond**

while receiving clear, actionable, and visually organized information.

---

## 📄 Documentation

This README describes the frontend architecture, development workflow, visual system, navigation, and integration principles.

Update this file whenever major frontend architecture, routes, setup instructions, or development workflows change.
