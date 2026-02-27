# Gram Meter Project Overview

## 1) What this project is
Gram Meter is a smart energy monitoring platform prototype with:
- User dashboard (consumption, billing, alerts, profile)
- Admin dashboard (`/admin`) for supervisory monitoring
- Backend APIs for auth, meter analytics, alerts, billing, notifications
- Live simulated meter feeds for demo/prototype workflows

## 2) Current runtime architecture
- Frontend: Vite + React (`frontend`), served on `http://localhost:5173`
- Backend: Django + DRF (`backend`), served on `http://localhost:8000`
- Live feeder: `Admin console/virtual_meter_gov.py` generates streaming demo data
- Optional integrations: AWS SNS/Twilio paths remain optional; Fast2SMS is the active SMS provider

## 3) Startup flow
Use:
- `start_project.bat`

This script:
1. Cleans old listeners
2. Prepares Python environment and dependencies
3. Starts Django backend
4. Starts main frontend
5. Starts virtual meter feeder
6. Opens the main dashboard (`http://localhost:5173/dashboard`)

Admin is accessed in the same frontend app via:
- `http://localhost:5173/admin`

## 4) Dataflow (high level)
1. Virtual feeder generates meter telemetry
2. Backend ingests/processes readings and business rules
3. Backend stores/aggregates data and exposes it via API
4. Frontend user/admin pages fetch from backend endpoints
5. Alerts/OTP use configured provider flow (Fast2SMS active)

## 5) AI module role
AI is an assistive layer (analytics/anomaly-style insights where enabled), not the sole source of dashboard data.
Core dashboards primarily depend on backend data pipelines and aggregations.

## 6) Key directories
- `backend/` — Django APIs, auth, meters, billing, notifications, analytics
- `frontend/` — User + admin routes in one app
- `Admin console/` — Virtual meter generator assets and scripts
- `ML/` — Supporting ML/analytics scripts and artifacts
- `logs/` — Runtime logs

## 7) Current status summary
- Single-app admin routing (`/admin`) is active
- Standalone admin console web app startup on `5174` is removed from startup path
- Fast2SMS is configured as default SMS provider
- Unified one-click startup is available via `start_project.bat`

## 8) Prototype readiness
This is a strong prototype for demonstration/submission with live flow. For production-grade deployment, add stronger observability, automated tests, and security/deployment hardening.
