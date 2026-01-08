# Development Guide - EcoImmo France 2026

Complete guide for developers working on the EcoImmo France 2026 platform.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [API Development](#api-development)
- [Frontend Development](#frontend-development)
- [AI Models](#ai-models)
- [Database](#database)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Node.js** 18.17+ and **pnpm** 9+
- **Python** 3.13+
- **Docker** & **Docker Compose**
- **Git**
- **PostgreSQL** 16+ (via Docker or local)
- **Redis** 7+ (via Docker or local)

### Optional but Recommended

- **VS Code** with extensions:
  - Python
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense
- **Postman** or **Insomnia** for API testing

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
./quick-start.sh
```

This script will:
- Check all prerequisites
- Install dependencies (pnpm + pip)
- Generate demo images
- Show you how to start the services

### Option 2: Manual Setup

```bash
# 1. Install dependencies
pnpm install
cd apps/api && pip install -r requirements.txt && cd ../..

# 2. Setup environment
cp .env.example .env
# Edit .env and add your Mistral API key

# 3. Start services
docker-compose up -d  # Start PostgreSQL + Redis

# Terminal 1 - API
cd apps/api
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd apps/web
pnpm dev:turbo
```

### Option 3: Full Docker Setup

```bash
docker-compose up -d
```

## Project Structure

```
ecoimmo-france-2026/
├── apps/
│   ├── web/              # Next.js 16 Frontend
│   │   ├── app/          # App Router pages
│   │   │   ├── ai-doctor/      # AI Property Doctor demo
│   │   │   ├── page.tsx        # Homepage
│   │   │   └── layout.tsx      # Root layout
│   │   ├── components/   # React components
│   │   ├── utils/        # Utilities (API client)
│   │   └── package.json
│   │
│   └── api/              # FastAPI Backend
│       ├── app/
│       │   ├── main.py          # Entry point
│       │   ├── routers/         # API endpoints
│       │   ├── services/        # Business logic
│       │   │   ├── dpe_2026_calculator.py       # DPE calculator
│       │   │   ├── french_gov_data_fetcher.py   # DVF/DPE fetcher
│       │   │   ├── ai_property_vision.py        # Computer vision
│       │   │   ├── ai_valuation_engine.py       # XGBoost valuation
│       │   │   ├── ai_market_forecasting.py     # Prophet forecasting
│       │   │   └── ai_property_doctor.py        # Master orchestrator
│       │   ├── models/          # Database models
│       │   └── utils/           # Utilities
│       └── requirements.txt
│
├── packages/             # Shared packages (future)
├── docs/                # Documentation
├── scripts/             # Build/deployment scripts
├── docker-compose.yml   # Docker orchestration
├── turbo.json          # Turborepo config
└── README.md           # Main documentation
```

## Development Workflow

### 1. Starting Development

```bash
# Start all services in watch mode
pnpm dev

# Or start individually:
pnpm dev:web    # Frontend only (Turbopack - fast!)
pnpm dev:api    # API only (uvicorn --reload)
```

### 2. Making Changes

**Frontend (React/TypeScript)**:
- Components in `apps/web/components/`
- Pages in `apps/web/app/`
- Utilities in `apps/web/utils/`
- Styles: Tailwind CSS classes

**Backend (Python/FastAPI)**:
- API routes in `apps/api/app/routers/`
- Business logic in `apps/api/app/services/`
- Models in `apps/api/app/models/`

### 3. Code Quality

```bash
# Lint all code
pnpm lint

# Format all code
pnpm format

# Type checking
pnpm type-check

# Backend linting (from apps/api/)
black .
ruff check .
mypy app/
```

### 4. Committing Changes

```bash
git add .
git commit -m "feat: your feature description"
git push -u origin claude/ecoimmo-france-2026-blfJh
```

## Testing

### API Testing

```bash
# Run API test suite
./test-api.sh

# Or manually test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Swagger UI
```

### Python Tests

```bash
cd apps/api
pytest -v
pytest --cov=app tests/  # With coverage
```

### Frontend Tests

```bash
cd apps/web
pnpm test
pnpm test:watch
```

## API Development

### Adding a New Endpoint

1. **Create router** (`apps/api/app/routers/my_feature.py`):
```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/my-feature", tags=["My Feature"])

@router.get("/")
async def get_my_feature():
    return {"message": "Hello from my feature!"}
```

2. **Register router** (`apps/api/app/main.py`):
```python
from app.routers import my_feature

app.include_router(my_feature.router)
```

3. **Test it**:
```bash
curl http://localhost:8000/api/v1/my-feature/
```

### Using Services

```python
from app.services.dpe_2026_calculator import DPE2026Calculator

calculator = DPE2026Calculator()
result = calculator.calculate_full_dpe_2026(...)
```

## Frontend Development

### Adding a New Page

1. **Create page** (`apps/web/app/my-page/page.tsx`):
```tsx
export default function MyPage() {
  return (
    <div>
      <h1>My New Page</h1>
    </div>
  )
}
```

2. **Access it**: `http://localhost:3000/my-page`

### Using API Client

```tsx
import { diagnoseProperty } from '@/utils/api-client'

const result = await diagnoseProperty({
  photo: file,
  property_address: "123 Rue de Paris",
  surface_m2: 65,
  code_postal: "75015"
})
```

### Styling with Tailwind

```tsx
<div className="rounded-lg bg-blue-500 p-4 text-white hover:bg-blue-600">
  Click me
</div>
```

## AI Models

### Computer Vision (DETR)

Located in `apps/api/app/services/ai_property_vision.py`:

```python
from app.services.ai_property_vision import AIPropertyVisionAnalyzer

analyzer = AIPropertyVisionAnalyzer()
result = analyzer.analyze_property_image("path/to/image.jpg")
```

### Property Valuation (XGBoost)

Located in `apps/api/app/services/ai_valuation_engine.py`:

**Training** (requires DVF data):
```python
from app.services.ai_valuation_engine import AIPropertyValuationEngine

engine = AIPropertyValuationEngine()
training_data = load_dvf_data()  # Your data source
engine.train_model(training_data)
engine.save_model("models/xgboost_valuation_v1.json")
```

**Inference**:
```python
engine.load_model("models/xgboost_valuation_v1.json")
valuation = engine.predict_property_value({...property_features})
```

### Market Forecasting (Prophet)

Located in `apps/api/app/services/ai_market_forecasting.py`:

```python
from app.services.ai_market_forecasting import AIMarketForecaster

forecaster = AIMarketForecaster()
forecast = forecaster.forecast_price_evolution("75015", months=36)
```

## Database

### Running Migrations

```bash
cd apps/api

# Apply schema from init-db.sql
psql -U ecoimmo -d ecoimmo_france < ../../init-db.sql

# Or via Docker
docker-compose exec postgres psql -U ecoimmo ecoimmo_france < init-db.sql
```

### Accessing Database

```bash
# Via Docker
docker-compose exec postgres psql -U ecoimmo ecoimmo_france

# Via local psql
psql postgresql://ecoimmo:ecoimmo_dev_2026@localhost:5432/ecoimmo_france
```

### Common Queries

```sql
-- Check properties count
SELECT COUNT(*) FROM properties;

-- Check DPE calculations
SELECT * FROM dpe_2026_calculations ORDER BY created_at DESC LIMIT 10;

-- Check AI insights cache
SELECT * FROM ai_insights_cache WHERE code_postal = '75015';
```

## Troubleshooting

### API Won't Start

```bash
# Check if port 8000 is in use
lsof -i :8000
kill -9 <PID>

# Check Python dependencies
cd apps/api
pip install -r requirements.txt --upgrade

# Check database connection
docker-compose ps
docker-compose logs postgres
```

### Frontend Won't Start

```bash
# Check if port 3000 is in use
lsof -i :3000
kill -9 <PID>

# Reinstall dependencies
rm -rf node_modules .pnpm-store
pnpm install

# Clear Next.js cache
rm -rf apps/web/.next
pnpm dev:turbo
```

### Docker Issues

```bash
# Reset everything
docker-compose down -v
docker-compose up -d

# Check logs
docker-compose logs -f api
docker-compose logs -f postgres

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

### Database Issues

```bash
# Reset database
docker-compose down -v postgres
docker-compose up -d postgres

# Wait for it to start, then reinitialize
sleep 5
docker-compose exec postgres psql -U ecoimmo ecoimmo_france < init-db.sql
```

### Redis Issues

```bash
# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL

# Or restart Redis
docker-compose restart redis
```

## Performance Tips

### Frontend

- **Use Turbopack**: Already enabled with `pnpm dev:turbo` (70% faster than Webpack)
- **React Compiler**: Automatic memoization (no useMemo needed)
- **Image Optimization**: Use Next.js `<Image>` component
- **Bundle Analysis**: `pnpm build && pnpm analyze`

### Backend

- **Redis Caching**: Always cache French Gov API calls (rate limits!)
- **Database Indexing**: Already set up in init-db.sql
- **Async Operations**: Use `async/await` for I/O operations
- **Connection Pooling**: Configure in database connection

## Best Practices

### Security

- **Never commit** `.env` files
- **Validate all inputs** (Pydantic on backend, Zod on frontend)
- **Sanitize SQL queries** (use parameterized queries)
- **Rate limiting** via Redis (already implemented)
- **CORS** properly configured in FastAPI

### Code Style

- **Python**: Follow PEP 8, use Black + Ruff
- **TypeScript**: Follow Airbnb style, use ESLint + Prettier
- **Commits**: Use conventional commits (feat:, fix:, docs:, etc.)

### Documentation

- **API**: Document with FastAPI docstrings → auto-generates OpenAPI
- **Components**: Add JSDoc comments to complex functions
- **Types**: Use TypeScript types, never `any` unless necessary

## Resources

- **Next.js Docs**: https://nextjs.org/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Tailwind CSS**: https://tailwindcss.com/docs
- **XGBoost**: https://xgboost.readthedocs.io/
- **Prophet**: https://facebook.github.io/prophet/

## Getting Help

1. Check the [README.md](./README.md) for general information
2. Read [AI_PROPERTY_DOCTOR.md](./AI_PROPERTY_DOCTOR.md) for AI features
3. Run `./test-api.sh` to diagnose API issues
4. Check API docs at http://localhost:8000/docs
5. Open an issue on GitHub

---

**Happy coding! 🚀**
