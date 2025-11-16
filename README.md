# PsyProtocol Platform

A comprehensive health technology platform for protocol-based medical treatments, client management, and AI-powered clinical support. Supporting psychedelics, hormone therapy, cancer treatments, regenerative medicine, and emerging therapies.

## Features

- User authentication and authorization (JWT-based)
- Role-based access control (Admin, Therapist, Client)
- Protocol management and client assignments for diverse medical treatments
- AI-powered clinical support using Anthropic's Claude
- Payment processing via Stripe
- Real-time caching with Redis
- RESTful API with comprehensive documentation

## Supported Protocol Types

### Psychedelic Therapy
- Psilocybin, MDMA, Ketamine, LSD, Ibogaine

### Hormone Replacement Therapy
- Testosterone replacement therapy (TRT)
- Estrogen therapy
- Growth hormone protocols
- Peptide therapies

### Cancer Treatments
- Chemotherapy protocols
- Immunotherapy regimens
- Radiation therapy schedules

### Regenerative Medicine
- Stem cell therapy
- Platelet-rich plasma (PRP)
- Exosome treatments

### Emerging Therapies
- Gene therapy
- CRISPR-based treatments
- CAR-T cell therapy
- Longevity protocols

## Quick Start with Docker

### Prerequisites

- Docker Desktop installed and running
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd health-tech-protocol-app
   ```

2. Create environment file (optional - for API keys):
   ```bash
   # Create .env file in project root for sensitive keys
   echo "ANTHROPIC_API_KEY=your-actual-key" > .env
   echo "STRIPE_SECRET_KEY=your-actual-key" >> .env
   ```

3. Start all services:
   ```bash
   docker-compose up -d
   ```

   This will:
   - Start PostgreSQL database
   - Start Redis cache
   - Build and start the FastAPI backend
   - Run database migrations automatically
   - Make the API available at http://localhost:8000

4. Access the application:
   - API: http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs
   - Alternative API docs: http://localhost:8000/redoc

### First-Time Setup

Create an admin user (after services are running):

```bash
# Access the backend container
docker-compose exec backend bash

# Inside the container, use Python to create admin
python -c "
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
admin = User(
    email='admin@psyprotocol.com',
    hashed_password=get_password_hash('admin123'),
    full_name='Admin User',
    role='admin',
    is_active=True
)
db.add(admin)
db.commit()
print('Admin user created!')
db.close()
"
```

## Development

### View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Database only
docker-compose logs -f postgres
```

### Run Tests

```bash
# Run all tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Run specific test file
docker-compose exec backend pytest tests/test_auth.py -v
```

### Database Operations

```bash
# Create a new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback one migration
docker-compose exec backend alembic downgrade -1

# View migration history
docker-compose exec backend alembic history
```

### Access Database

```bash
# Using psql
docker-compose exec postgres psql -U psyprotocol -d psyprotocol

# Common queries
docker-compose exec postgres psql -U psyprotocol -d psyprotocol -c "SELECT * FROM users;"
```

### Rebuild Services

```bash
# Rebuild backend after dependency changes
docker-compose build backend

# Rebuild and restart
docker-compose up -d --build backend
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

## Local Development (Without Docker)

If you prefer to run services locally:

1. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt -r requirements-dev.txt
   ```

2. Set up PostgreSQL and Redis locally

3. Update `.env` with local connection strings

4. Run migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once the services are running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

Key environment variables (set in `.env` or `docker-compose.yml`):

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql://psyprotocol:password@postgres:5432/psyprotocol |
| REDIS_URL | Redis connection string | redis://redis:6379/0 |
| JWT_SECRET | Secret key for JWT tokens | dev_secret_change_in_production |
| ANTHROPIC_API_KEY | Anthropic API key for AI features | Required for chat |
| STRIPE_SECRET_KEY | Stripe secret key for payments | Required for payments |
| ENVIRONMENT | Environment name | development |
| DEBUG | Enable debug mode | true |

## Project Structure

```
health-tech-protocol-app/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core functionality
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   ├── tests/            # Test suite
│   ├── alembic/          # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── docs/                 # Documentation
├── docker-compose.yml
└── README.md
```

## Testing

The project includes comprehensive test coverage:

```bash
# Run all tests with coverage
docker-compose exec backend pytest --cov=app --cov-report=term-missing

# Run specific test categories
docker-compose exec backend pytest tests/test_auth.py -v
docker-compose exec backend pytest tests/test_protocols.py -v
docker-compose exec backend pytest tests/test_chat.py -v
```

## Troubleshooting

### Services won't start

```bash
# Check service status
docker-compose ps

# View detailed logs
docker-compose logs backend
docker-compose logs postgres
```

### Database connection errors

```bash
# Ensure PostgreSQL is healthy
docker-compose ps postgres

# Restart database
docker-compose restart postgres
```

### Port already in use

If ports 5432, 6379, or 8000 are already in use, update the port mappings in `docker-compose.yml`:

```yaml
ports:
  - "5433:5432"  # Change 5432 to 5433
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests: `docker-compose exec backend pytest`
4. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions, please create an issue in the repository.
