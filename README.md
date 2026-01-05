# Car Part Scraper - 4G63/G4JS/Hyundai 2.0L DOHC Head Finder

Automated scraper for finding compatible cylinder heads on car-part.com with AI-powered parsing and price tracking.

## Features

- 🔍 Searches 11 vehicle configurations (4G63, G4JS, Hyundai 2.0L DOHC heads)
- 🤖 AI-powered parsing using local Ollama (llama3.1:8b)
- 💾 PostgreSQL database with price history tracking
- 🌐 Web UI at https://4g63.drag.rocks
- 📅 Daily automated searches at 7am EST
- 📊 REST API with interactive docs
- 💰 100% free (no API costs)

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL 15
- **AI:** Ollama (llama3.1:8b)
- **Frontend:** Jinja2 templates + Bootstrap 5
- **Deployment:** Kubernetes (K3s) + Flux CD

## Quick Start

```bash
# Clone the repo
git clone <repo-url>
cd car-part-scraper

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/carparts"
export OLLAMA_URL="http://localhost:11434"

# Run locally
python -m uvicorn app.main:app --reload

# Visit http://localhost:8000
```

## API Endpoints

- `GET /` - Web dashboard
- `GET /api/parts` - List all parts
- `GET /api/parts/{id}` - Get part details
- `GET /api/search/4g63` - Search 4G63 heads
- `GET /api/search/g4js` - Search G4JS heads
- `GET /api/search/hyundai2l` - Search Hyundai 2.0L heads
- `POST /api/search/manual` - Manual search
- `GET /api/stats` - Statistics
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## Deployment

Deployed via GitOps (Flux CD) to K3s cluster:
- **URL:** https://4g63.drag.rocks
- **Namespace:** car-scraper
- **Database:** PostgreSQL with persistent storage
- **AI:** Ollama service in ai namespace

See `../homelab-gitops/k3s/apps/car-part-scraper/` for K8s manifests.

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy .
```

## Vehicle Configurations

### 4G63 DOHC (3 configs)
- 1990-1994 Eclipse/Talon 2.0L Turbo
- 1995-1999 Eclipse/Talon 2.0L Turbo
- 1997-2006 Lancer Evolution (I-IX)

### G4JS DOHC (4 configs)
- 2001-2005 Hyundai Tiburon
- 2002-2006 Hyundai Elantra GT
- 2003-2008 Hyundai Tiburon SE/GT
- 2005-2010 Kia Spectra5

### Hyundai 2.0L DOHC (4 configs)
- 1992-1998 Sonata 2.0L
- 1988-1992 Grandeur 2.0L
- 1997-2002 Santamo 2.0L
- 1991-1995 Scoupe 2.0L

## License

MIT
