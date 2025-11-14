# Full Stack Guide: Go + Next.js + PostgreSQL

This guide covers running the complete stack locally and in GitHub Actions.

## Stack Overview

- **Backend**: Go 1.21 with Fiber framework
- **Frontend**: Next.js 14 with React Server Components
- **Database**: PostgreSQL 16
- **Deployment**: Docker & GitHub Actions

## Quick Start with Docker Compose

The easiest way to run the entire stack:

```bash
# Start all services
docker-compose up

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

Then visit:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:3001
- **Health Check**: http://localhost:3001/api/health

## Local Development (Without Docker)

### Prerequisites

- Go 1.21+
- Node.js 20+
- PostgreSQL 16+

### 1. Start PostgreSQL

```bash
# Using Docker
docker run --name postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=neevs \
  -p 5432:5432 \
  -d postgres:16-alpine

# Or use your local PostgreSQL installation
```

### 2. Start Backend

```bash
cd backend

# Install dependencies
go mod download

# Create .env file
cp .env.example .env

# Run the server
go run main.go

# Or build and run
go build -o backend .
./backend
```

Backend will start on http://localhost:3001

### 3. Start Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local

# Run development server
npm run dev

# Or build and run production
npm run build
npm start
```

Frontend will start on http://localhost:3000

## Live Demo in GitHub Actions

Run a live demo of the entire stack in GitHub Actions:

1. Go to **Actions** tab in your repository
2. Select **"🚀 Live Full Stack Demo"** workflow
3. Click **"Run workflow"**
4. Set duration (default: 20 minutes)
5. Click **"Run workflow"**

### With Public Access (Optional)

To enable public access via Cloudflare Tunnel:

1. Create a Cloudflare Tunnel at https://one.dash.cloudflare.com/
2. Get the tunnel token
3. Add it as a repository secret named `CLOUDFLARE_TUNNEL_TOKEN`
4. Run the workflow again

The stack will be publicly accessible at the configured tunnel URLs.

## API Endpoints

### Health Check
```bash
GET /api/health

Response:
{
  "status": "ok",
  "database": "connected",
  "time": "2024-01-15T10:30:00Z"
}
```

### Items CRUD

**Get all items**
```bash
GET /api/items

Response: Array of items
```

**Get single item**
```bash
GET /api/items/:id

Response: Item object or 404
```

**Create item**
```bash
POST /api/items
Content-Type: application/json

{
  "title": "Item Title",
  "description": "Item description"
}

Response: Created item with id
```

**Update item**
```bash
PUT /api/items/:id
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated description"
}

Response: Updated item
```

**Delete item**
```bash
DELETE /api/items/:id

Response: { "message": "Item deleted successfully" }
```

## Testing the Stack

### Manual Testing

```bash
# Health check
curl http://localhost:3001/api/health

# Create an item
curl -X POST http://localhost:3001/api/items \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Item","description":"Testing the API"}'

# Get all items
curl http://localhost:3001/api/items

# Get specific item
curl http://localhost:3001/api/items/1

# Update item
curl -X PUT http://localhost:3001/api/items/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Item","description":"Updated description"}'

# Delete item
curl -X DELETE http://localhost:3001/api/items/1
```

### Using the Frontend

1. Open http://localhost:3000
2. Click "Create New Item"
3. Fill in title and description
4. Click "Create"
5. View, edit, or delete items

## Environment Variables

### Backend (.env)
```bash
PORT=3001
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=neevs
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:3001
```

## Database Schema

The application automatically creates the following table:

```sql
CREATE TABLE items (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_items_created_at ON items(created_at DESC);
```

## Project Structure

```
.
├── backend/                 # Go backend
│   ├── main.go             # Main application
│   ├── go.mod              # Go dependencies
│   ├── Dockerfile          # Backend container
│   └── README.md           # Backend docs
│
├── frontend/               # Next.js frontend
│   ├── app/                # App directory
│   │   ├── components/     # React components
│   │   ├── layout.tsx      # Root layout
│   │   └── page.tsx        # Home page
│   ├── package.json        # Node dependencies
│   ├── Dockerfile          # Frontend container
│   └── README.md           # Frontend docs
│
├── .github/
│   └── workflows/
│       └── live-stack-demo.yml  # GitHub Actions workflow
│
├── docker-compose.yml      # Docker Compose config
└── STACK_GUIDE.md         # This file
```

## Troubleshooting

### Backend won't connect to database

Check PostgreSQL is running:
```bash
# Docker
docker ps | grep postgres

# Local
pg_isready -h localhost -p 5432
```

### Frontend can't reach backend

1. Verify backend is running: `curl http://localhost:3001/api/health`
2. Check CORS settings in backend `.env`
3. Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`

### Port already in use

Change ports in:
- Backend: `.env` → `PORT=3002`
- Frontend: `.env.local` and run with `PORT=3001 npm run dev`
- Docker Compose: Edit `ports` section in `docker-compose.yml`

### Database connection errors

Ensure PostgreSQL is healthy:
```bash
docker-compose logs postgres

# Connect to database
PGPASSWORD=postgres psql -h localhost -p 5432 -U postgres -d neevs
```

## Production Deployment

### Docker

Build and push images:
```bash
# Backend
docker build -t your-registry/neevs-backend:latest ./backend
docker push your-registry/neevs-backend:latest

# Frontend
docker build -t your-registry/neevs-frontend:latest ./frontend
docker push your-registry/neevs-frontend:latest
```

### Environment-specific Configuration

Update environment variables for production:
- Use secure database passwords
- Configure proper CORS origins
- Set production API URLs
- Enable SSL/TLS
- Configure proper logging

## Contributing

When adding new features:

1. Update backend API in `backend/main.go`
2. Add corresponding frontend components
3. Update API documentation in this guide
4. Test locally with Docker Compose
5. Test in GitHub Actions workflow

## License

See main repository LICENSE file.
