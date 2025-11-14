# How to Run

## Prerequisites

### System Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB free space (for Docker images and models)
- **OS**: Linux, macOS, or Windows with WSL2

---

## Quick Start (Local Development)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd gepp
```

### 2. Set Up Environment Files

**Backend Environment**:
```bash
cd backend
cp .env.example .env
```

**Frontend Environment**:
```bash
cd ../frontend
cp .env.example .env
```

### 3. Start All Services

From the project root directory:

```bash
docker compose up -d --build
```

This will:
- Build Docker images for backend and frontend
- Start PostgreSQL with pgvector extension
- Download AI models (first run only, ~100MB)
- **Automatically seed database with 150 realistic incidents** (first run only, takes 2-3 minutes)
- Start backend API on port 8000
- Start frontend dev server on port 3000

**First-time startup takes 5-8 minutes** (downloading models, dependencies, and seeding data with AI processing).

> **Note**: Database seeding is automatic on first run. The system creates 150 realistic incidents across 17 locations with AI-processed data (waste classification, embeddings, keywords, similarity detection). This process takes 2-3 minutes as each incident is processed through the AI pipeline. See [DATABASE_SEEDING.md](./DATABASE_SEEDING.md) for details.

> **⏳ Seeding Progress**: After containers start, wait 2-3 minutes for seeding to complete. Check backend logs with `docker compose logs -f backend` to monitor progress. You'll see "DATABASE SEEDING COMPLETED" when ready.

### 4. Access the Application

Once all services are running and seeding is complete:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)

> **⚠️ Important**: If you see an empty dashboard initially, wait 2-3 minutes for the seeding process to complete. Monitor progress with `docker compose logs -f backend`.

### 5. Verify Installation

Check that all services are healthy:

```bash
# Check running containers
docker compose ps

# Expected output:
# NAME               STATUS              PORTS
# gepp-postgres      Up (healthy)        5432->5432
# gepp-backend       Up                  8000->8000
# gepp-frontend      Up                  3000->3000

# Test backend health
curl http://localhost:8000/health

# Expected output:
# {"status":"healthy"}

# Test frontend
curl http://localhost:3000
```

---

## Development Mode

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres

# Monitor seeding progress (first run)
docker compose logs -f backend | grep -i "seed"
```

### Running Commands in Containers

**Backend shell**:
```bash
docker compose exec backend sh
```

**Frontend shell**:
```bash
docker compose exec frontend sh
```

**Database shell**:
```bash
docker compose exec postgres psql -U gepp_user -d gepp_db
```

---

## Database Management

### Restore

```bash
# Restore database
docker compose exec -T postgres psql -U gepp_user gepp_db < backup.sql

# Or with Docker directly
docker exec -i gepp-postgres psql -U gepp_user gepp_db < backup.sql
```

### Reset Database

```bash
# Stop services
docker compose down

# Remove volumes (⚠️ deletes all data)
docker compose down -v

# Restart (will automatically seed 150 incidents - takes 2-3 minutes)
docker compose up -d --build

# Monitor seeding progress
docker compose logs -f backend
```

### Disable Automatic Seeding

If you don't want automatic data seeding:

```yaml
# In docker-compose.yml, change:
environment:
  SEED_DATA: "false"  # Disable seeding
```

Or adjust the number of seeded incidents:

```yaml
environment:
  SEED_COUNT: "200"  # Seed 200 incidents instead of 150
```

