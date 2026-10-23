# Multimodal Construction Intelligence Platform

**React + Vite frontend · FastAPI/Python backend · Optional Gemini multimodal AI**

This repository contains a runnable full-stack MVP aligned with the Skill Wallet project brief. It brings construction site safety screening, crack-observation workflows, rough planning/quantity estimates, indicative property valuation, and a construction knowledge assistant into one dashboard.

> **Safety and accuracy notice:** This is an educational MVP, not a certified engineering, structural-safety, estimating, or property-valuation system. AI can be wrong. Qualified professionals must verify any real-world decisions. Demo mode does not interpret image pixels.

## Capabilities

- Construction safety screening from written site observations
- Image upload workflow for crack observations (JPG/PNG/WEBP, configurable size limit)
- Optional multimodal image/text analysis through Google Gemini
- Rough material quantities and indicative cost range from area, floor count and finish level
- Indicative property value from user-entered local rate, age and condition
- Construction knowledge assistant with demo answers and optional Gemini responses
- Pydantic request/response models and validation
- FastAPI interactive API docs and health endpoint
- Responsive React dashboard, loading/error states, image preview and structured results
- Backend API tests
- Dockerfiles and Docker Compose configuration
- README, environment examples and Git ignore rules

## Folder layout

```text
Construction_Intelligence_Platform/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── services.py
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   └── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10 or newer (Python 3.11 recommended)
- Node.js 20 or newer and npm
- Git for publishing
- VS Code or another editor

## Run locally on Windows

### A. Backend

Open a terminal at the extracted project root:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

If PowerShell blocks environment activation, run this in that terminal and retry activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Keep the backend terminal running. Check:
- Health: http://127.0.0.1:8000/health
- Interactive API documentation: http://127.0.0.1:8000/docs

Expected health response:

```json
{"status":"ok","service":"construction-intelligence-api"}
```

### B. Frontend

Open a second terminal at the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL Vite prints, normally http://localhost:5173.

### C. Test the workflows

1. **Site safety:** submit `Worker near an unprotected roof edge without a harness`.
2. **Crack analysis:** select a JPG/PNG/WEBP image under the configured upload limit. In demo mode, the API confirms receipt but does not visually inspect the image.
3. **Planning & costs:** enter area `1200`, floors `1`, finish `standard`.
4. **Property valuation:** enter area `1000`, rate `4000`, age `5`, condition `good`.
5. **Site assistant:** ask `What should I check before starting work at height?`.
6. Test empty/invalid form values and confirm the UI displays an error instead of crashing.

## Optional: enable Gemini AI

The app starts in **demo mode** and does not require an API key. For AI text and multimodal image analysis:

1. Create your own Gemini API key using Google AI Studio.
2. Edit `backend/.env`:
   ```env
   AI_PROVIDER=gemini
   GEMINI_API_KEY=YOUR_PRIVATE_KEY
   GEMINI_MODEL=gemini-2.5-flash
   MAX_UPLOAD_MB=8
   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   ```
3. Restart the backend.

Keep the key private. Never commit `.env`, API keys, access tokens, or private site imagery. Provider model names, quotas, availability and pricing can change. Check current provider documentation. AI outputs need professional review.

## Run automated backend tests

From a terminal:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -q
```

Tests cover health, safety screening, planning, invalid inputs, valuation, assistant responses, and upload validation. A successful local test run is required before treating the app as verified.

## Docker option

Docker Desktop must be installed and running. Create `backend/.env` by copying `backend/.env.example`, then from the project root:

```powershell
docker compose up --build
```

Frontend: http://localhost:8080  
Backend docs: http://localhost:8000/docs

Stop containers with `Ctrl+C`, then run `docker compose down`. The frontend's API URL is embedded at build time; change the Docker build argument for a deployed backend.

## GitHub publishing

Create a new **empty** repository on GitHub. Then, from the project root:

```powershell
git init
git status
git add .
git status
git commit -m "Build construction intelligence platform"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/construction-intelligence-platform.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username. Review the `git status` output before committing. Ensure no `.env`, `.venv`, `node_modules`, API key, or private data is staged. `.gitignore` excludes common local secrets and generated files.

## Deployment outline

Deploy the frontend and backend as separate services:

### Frontend (Vercel or Netlify)
- Root/build directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Environment variable: `VITE_API_BASE_URL=https://YOUR_DEPLOYED_BACKEND_URL`
- Rebuild after changing this variable.

### Backend (a Python web-service host)
- Root directory: `backend`
- Build/install command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Configure `AI_PROVIDER`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `MAX_UPLOAD_MB`, and `CORS_ORIGINS` in the host's environment settings.
- `CORS_ORIGINS` must include the exact deployed frontend origin, with no trailing path.

Provider dashboards and free-tier policies change, so follow current deployment-provider instructions. Verify the live health endpoint, API docs, and frontend-to-backend requests before submitting deployment URLs.

## Estimation assumptions and known limitations

- Demo safety analysis uses simple keyword screening; it is not a complete hazard analysis.
- Demo crack analysis does not interpret image pixels.
- Gemini can make mistakes and may not identify every hazard or crack.
- Cement/steel quantities and cost rates are rough illustrative thumb rules; they are not a bill of quantities or quotation.
- Property valuation is a simple formula using the supplied rate and adjustment factors, not a market appraisal.
- Weather advisory uses the text entered by the user; live weather is not fetched.
- No user accounts, persistent database, audit log, or production access control are included in this MVP.
- Do not use the app to certify safety, diagnose structural integrity, or replace approved project documents and professional judgment.

## Final pre-submission checklist

- [ ] Both services start locally
- [ ] `/health` responds successfully
- [ ] All UI workflows return results
- [ ] Upload validation and invalid input handling work
- [ ] `pytest -q` passes
- [ ] `npm run build` succeeds
- [ ] README includes your actual screenshots and test notes
- [ ] No secrets are in GitHub
- [ ] Deployed app and API have been checked from a browser
