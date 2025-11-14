# System Architecture

## Overview

GEPP (Global Environmental Protection Platform) is an enterprise-grade waste incident reporting and AI insight platform built with a modern, scalable architecture. The system uses a **modular monolith** approach for the backend, keeping related functionalities organized while maintaining deployment simplicity.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend Layer                       │
│  React + TypeScript + Tailwind CSS + Vite + React Query    │
└───────────────┬─────────────────────────────────────────────┘
                │ REST API (JSON)
                │
┌───────────────▼─────────────────────────────────────────────┐
│                       API Gateway Layer                      │
│                    FastAPI Application                       │
└───────────────┬─────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────┐
│                     Application Layer                        │
│    ┌──────────────┬──────────────┬──────────────┐          │
│    │  Incidents   │  Analytics   │  AI Service  │          │
│    │   Module     │    Module    │    Module    │          │
│    └──────────────┴──────────────┴──────────────┘          │
└───────────────┬─────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────┐
│                      Data Layer                              │
│  PostgreSQL with pgvector Extension + SQLAlchemy ORM        │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Async Python web framework)
- **Language**: Python
- **ORM**: SQLAlchemy (Async mode)
- **Database Driver**: asyncpg (PostgreSQL async driver)
- **API Documentation**: Auto-generated OpenAPI (Swagger) docs

### Frontend
- **Framework**: React
- **Language**: TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI primitives
- **State Management**: TanStack Query (React Query)
- **Routing**: React Router DOM
- **Charts**: Recharts

### Database
- **RDBMS**: PostgreSQL
- **Vector Extension**: pgvector (for similarity search)
- **Schema**: Managed via SQLAlchemy models

### AI/ML (Offline Only)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Text Processing**: NLTK
- **Classification**: scikit-learn (cosine similarity)
- **Vector Operations**: NumPy

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Web Server**: Uvicorn (ASGI server)
- **Logging**: structlog + python-json-logger
- **CORS**: FastAPI CORS middleware

## Backend Architecture (Modular Monolith)

### Core Modules

```
backend/
├── app/
│   ├── main.py                    # Application entry point
│   ├── core/                      # Core infrastructure
│   │   ├── config.py             # Configuration management
│   │   ├── database.py           # Database connection & session
│   │   └── logging.py            # Structured logging & auditing
│   └── modules/                   # Business modules
│       ├── incidents/             # Incident management
│       │   ├── models.py         # Database models
│       │   ├── schemas.py        # Pydantic schemas (DTOs)
│       │   ├── service.py        # Business logic
│       │   └── routes.py         # API endpoints
│       ├── analytics/             # Analytics & dashboard
│       │   ├── schemas.py
│       │   ├── service.py        # Statistical analysis
│       │   └── routes.py
│       └── ai/                    # AI features (offline)
│           ├── schemas.py
│           ├── service.py        # ML models & algorithms
│           └── routes.py
```

### Modular Monolith Principles

1. **Domain-Driven Design**: Each module represents a bounded context
2. **Separation of Concerns**: Clear separation of routes, services, schemas, and models
3. **Dependency Injection**: Database sessions injected via FastAPI dependencies
4. **Async-First**: All I/O operations are asynchronous for better performance
5. **Type Safety**: Full type hints with Pydantic validation

### Data Flow

```
Request → Route Handler → Service Layer → Database/AI → Response
   │          │               │              │
   │          │               └──────────────┴─► Logging & Auditing
   │          └─► Validation (Pydantic schemas)
   └─► CORS, Auth middleware (if added)
```

## Frontend Architecture

### Component Structure

```
frontend/
├── src/
│   ├── main.tsx                  # App entry point
│   ├── App.tsx                   # Root component with routing
│   ├── config/                   # Configuration
│   │   └── api.ts               # API endpoints
│   ├── api/                      # API client layer
│   │   ├── incidents.ts         # Incident API calls
│   │   └── analytics.ts         # Analytics API calls
│   └── pages/                    # Page components
│       ├── Dashboard.tsx        # Dashboard with admin summary & charts
│       ├── IncidentList.tsx     # Incident list with filters
│       ├── IncidentForm.tsx     # Incident submission with duplicate detection
│       └── SemanticSearch.tsx   # AI-powered similarity search
```

### State Management

- **Server State**: TanStack Query for API caching and synchronization
- **Form State**: React hooks (useState)
- **URL State**: React Router for navigation state

### API Communication

- **Client**: Axios for HTTP requests
- **Caching**: React Query with automatic revalidation
- **Error Handling**: Centralized error handling with user feedback

## Database Schema

### Main Tables

#### `incidents`
```sql
id              UUID PRIMARY KEY
description     TEXT NOT NULL
timestamp       TIMESTAMP NOT NULL
location        VARCHAR(500) NOT NULL
latitude        FLOAT
longitude       FLOAT
waste_type      VARCHAR(100)
waste_type_confidence FLOAT
embedding       VECTOR(384)      -- pgvector for similarity
keywords        TEXT[]
similar_incident_ids UUID[]
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

### Indexes
- `idx_timestamp_desc`: Timestamp descending (for time-based queries)
- `idx_waste_type`: Waste type filtering
- `idx_location`: Location-based queries
- Vector index on `embedding` for similarity search

## AI Architecture (Offline)

### Components

1. **Waste Classification (Hybrid AI)**
   - Primary: Semantic similarity with pre-computed category embeddings
   - Fallback: Rule-based keyword matching
   - 10 predefined categories with detailed descriptions
   - Dynamic confidence scoring combining both approaches
   - High accuracy (~90%) with explainable results

2. **Semantic Similarity Detection**
   - sentence-transformers (all-MiniLM-L6-v2)
   - 384-dimensional embeddings
   - Cosine similarity calculation
   - Real-time duplicate detection during incident submission
   - Configurable threshold (default: 0.75)

3. **Keyword Extraction**
   - NLTK tokenization
   - Stopword removal
   - Frequency analysis
   - Top-N selection

4. **AI-Generated Admin Summary & Insights**
   - Aggregates AI features with statistical analytics
   - Rule-based natural language generation
   - Severity-based prioritization (error, warning, success, info)
   - Executive summary paragraph + structured insights
   - Configurable time periods (7, 14, 30 days)

### Processing Pipeline

```
Incident Submission
    ↓
1. Store in Database
    ↓
2. Generate Embedding (sentence-transformers)
    ↓
3. Classify Waste Type (hybrid: semantic + keyword)
    ├─ Primary: Semantic similarity with category embeddings
    ├─ Fallback: Keyword matching
    └─ Dynamic confidence calculation
    ↓
4. Extract Keywords (NLTK)
    ├─ Tokenization
    ├─ Stopword removal
    └─ Frequency analysis
    ↓
5. Find Similar Incidents (vector search)
    ├─ Cosine similarity calculation
    ├─ Real-time duplicate detection
    └─ Filter by threshold (0.75)
    ↓
6. Update AI Fields
    ├─ waste_type
    ├─ waste_type_confidence
    ├─ embedding
    ├─ keywords
    └─ similar_incident_ids
    ↓
7. Return complete incident to client
   (with duplicate warnings if applicable)
```

## Logging & Monitoring

### Structured Logging
- **Format**: JSON logs for machine parsing
- **Library**: structlog + python-json-logger
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Context**: Request ID, user ID, timestamps

### Audit Trail
- All CRUD operations logged
- Includes: action, resource, resource_id, user_id, timestamp, status
- Separate audit logger for compliance

### Log Output
```json
{
  "timestamp": "2025-11-13T10:30:45.123Z",
  "level": "INFO",
  "event": "incident_created",
  "incident_id": "uuid",
  "location": "Downtown Park",
  "waste_type": "plastic"
}
```

## Security Considerations

1. **Input Validation**: Pydantic schemas validate all inputs
2. **SQL Injection**: SQLAlchemy ORM prevents SQL injection
3. **CORS**: Configured for allowed origins
4. **Rate Limiting**: Can be added via middleware
5. **Authentication**: Ready for JWT/OAuth2 integration

## Performance Optimizations

1. **Database**
   - Indexed columns for common queries
   - Connection pooling (10 connections)
   - Async operations throughout

2. **API**
   - Pagination for large result sets
   - Query parameter filtering
   - Response compression

3. **Frontend**
   - React Query caching
   - Code splitting with Vite
   - Lazy loading of routes
   - Optimized bundle size

## Development Workflow

1. **Local Development**: Docker Compose for all services
2. **Hot Reload**: Both frontend (Vite) and backend (Uvicorn) support hot reload
3. **Type Safety**: TypeScript on frontend, type hints on backend
4. **API Documentation**: Auto-generated at `/docs` (Swagger UI)

## Deployment

### Docker Compose
- **Services**: postgres, backend, frontend
- **Networks**: Internal network for service communication
- **Volumes**: Persistent database storage
- **Health Checks**: Ensures services are ready

### Environment Variables
- **Backend**: DATABASE_URL, LOG_LEVEL, ENVIRONMENT
- **Frontend**: VITE_API_URL

## Monitoring & Observability

### Logs
- Structured JSON logs to stdout
- Aggregatable by log management systems (ELK, Splunk, etc.)

### Metrics (Future)
- Prometheus metrics endpoint
- Grafana dashboards
- Request latency, error rates, throughput

### Health Checks
- `/health` endpoint for service health
- Database connectivity check
- AI model availability check

## API Design

### RESTful Principles
- Resource-based URLs
- HTTP methods (GET, POST, PUT, DELETE)
- Status codes (200, 201, 404, 500)
- JSON request/response

### API Versioning
- Prefix: `/api/`
- Future: `/api/v2/` for breaking changes

### Response Format
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```