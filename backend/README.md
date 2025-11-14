# Neevs Backend API

Go backend API with PostgreSQL database integration using Fiber framework.

## Features

- RESTful API for CRUD operations
- PostgreSQL database integration
- CORS support
- Health check endpoint
- Automatic table creation
- Environment-based configuration

## Prerequisites

- Go 1.21 or higher
- PostgreSQL 14 or higher

## Local Development

1. Install dependencies:
```bash
go mod download
```

2. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. Start PostgreSQL (if not running):
```bash
# Using Docker
docker run --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=neevs -p 5432:5432 -d postgres:16-alpine
```

4. Run the server:
```bash
go run main.go
```

The server will start on `http://localhost:3001`

## API Endpoints

### Health Check
```
GET /api/health
```

### Items
- `GET /api/items` - Get all items
- `GET /api/items/:id` - Get single item
- `POST /api/items` - Create new item
- `PUT /api/items/:id` - Update item
- `DELETE /api/items/:id` - Delete item

### Example Request
```bash
# Create item
curl -X POST http://localhost:3001/api/items \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Item","description":"This is a test"}'

# Get all items
curl http://localhost:3001/api/items
```

## Environment Variables

See `.env.example` for all available configuration options.

## Build

```bash
# Build for production
go build -o backend main.go

# Run production build
./backend
```

## Docker

```bash
# Build image
docker build -t neevs-backend .

# Run container
docker run -p 3001:3001 --env-file .env neevs-backend
```
