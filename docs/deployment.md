# Deployment Guide

## Render.com (Demo / Staging)

Quick cloud deployment for demo purposes. Free tier available.

### Prerequisites
- GitHub repo: `alexzyb/LE`
- `render.yaml` in repo root (already included)

### Setup Steps
1. Go to https://render.com and sign in with GitHub
2. **New** → **Web Service** → connect `alexzyb/LE` repository
3. Configure:
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --workers 2 --timeout 120 --bind 0.0.0.0:$PORT src.app:server`
   - **Plan**: Free
4. Click **Deploy** → wait 2-3 minutes
5. Access via the provided URL (e.g. `https://land-energy-dashboard.onrender.com`)

### Notes
- **Auto-Deploy**: enabled by default — every push to `main` triggers redeployment
- **Free tier**: app sleeps after 15 min of inactivity, ~30s cold start on next visit
- **Database**: SQLite file is committed to git; resets to repo state on each deploy (fine for static demo data)
- **To disable auto-deploy**: Render Dashboard → Service → Settings → toggle off

### Local Testing with Gunicorn
```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:8050 src.app:server
```

---

## Azure (Production) — Future

_To be documented when ready for production deployment._

Considerations:
- Azure App Service or Azure Container Instances
- PostgreSQL instead of SQLite for persistent data
- Custom domain + HTTPS
- Docker containerisation
- Logging and monitoring (Application Insights)
