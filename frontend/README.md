# Neevs Frontend

Next.js 14 application with React Server Components and TypeScript.

## Features

- React Server Components for server-side data fetching
- Client Components for interactivity
- Tailwind CSS for styling
- TypeScript for type safety
- API integration with Go backend

## Prerequisites

- Node.js 18 or higher
- npm or yarn

## Local Development

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Create `.env.local` file:
```bash
cp .env.example .env.local
# Edit .env.local if needed
```

3. Run the development server:
```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:3001)

## Build for Production

```bash
# Build
npm run build

# Start production server
npm start
```

## Docker

```bash
# Build image
docker build -t neevs-frontend .

# Run container
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://backend:3001 neevs-frontend
```

## Project Structure

```
frontend/
├── app/
│   ├── components/       # React components
│   ├── layout.tsx        # Root layout
│   ├── page.tsx          # Home page
│   └── globals.css       # Global styles
├── public/               # Static files
├── next.config.js        # Next.js configuration
└── package.json          # Dependencies
```

## API Integration

The frontend connects to the Go backend API at the URL specified in `NEXT_PUBLIC_API_URL`.

Endpoints used:
- `GET /api/health` - Health check
- `GET /api/items` - Fetch all items
- `POST /api/items` - Create new item
- `DELETE /api/items/:id` - Delete item
