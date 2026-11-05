# AI-Powered Virtual Business Card Generator (Google Cloud SLW Booth Demo)

This live demonstration app showcases Google Cloud Gemini Enterprise Agent Platform and Cloud Run by turning booth visitors' professional roles and lifestyle keywords into personalized, shareable "Virtual Persona Business Cards".

---

## 🌟 Key Features
- **Interactive Kiosk Input**: Visitors select role (e.g. CTO, Developer, Marketer), company, and lifestyle keywords (e.g. Coding Wizard, Marathon Enthusiast).
- **Instant Gemini AI Persona Creation**: Generates unique persona titles, 2-sentence bio stories, and superpower badges.
- **Interactive 3D Virtual Card**: Responsive card with 3D tilt effect, customizable visual themes (Google Cloud, Cyberpunk, Cosmic, Minimal), and PNG download.
- **Mobile Delivery via QR Code**: Dynamic QR code points directly to `/card/{card_id}` for instant smartphone viewing and saving.
- **Verified Lead Capture & Dashboard**: Admin view (`/admin`) tracks captured booth leads with CSV export for sales follow-up.

---

## 🚀 Local Development & Execution

### 1. Requirements
- Python 3.9+ installed
- Virtual environment with dependencies (`fastapi`, `uvicorn`, `google-genai`, `qrcode`, `jinja2`, `pillow`)

### 2. Run Server
```bash
# Navigate to project directory
cd /Users/syjjang/.gemini/antigravity/scratch/virtual-card-generator

# Activate virtual environment (if created)
source ../venv/bin/activate

# (Optional) Set Gemini API Key
export GEMINI_API_KEY="your-gemini-api-key"

# Start FastAPI Uvicorn Server
uvicorn app.main:app --reload --port 8000
```

### 3. Open in Browser
- **Booth Kiosk Main View**: `http://localhost:8000`
- **Lead Capture Dashboard**: `http://localhost:8000/admin`
- **Mobile Card View Example**: `http://localhost:8000/card/demo`

---

## ☁️ Google Cloud Run Deployment Guide

To deploy this application to Google Cloud Run and get a public URL:

### Step 1: Authenticate Google Cloud CLI
```bash
gcloud auth login
gcloud config set project YOUR_GCP_PROJECT_ID
```

### Step 2: Build & Deploy directly to Cloud Run
```bash
gcloud run deploy virtual-card-generator \
  --source . \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Once deployment finishes, `gcloud` will output your live HTTPS URL (e.g., `https://virtual-card-generator-xyz-an.a.run.app`).
