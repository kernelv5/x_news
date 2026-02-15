# eNewPaper Twitter Crawler

A complete Twitter data crawling system with MongoDB storage, Python FastAPI backend, and Next.js frontend - all running in Docker containers.

## System Architecture

- **MongoDB**: External database for storing Twitter accounts and tweets
- **Backend**: Python FastAPI server for Twitter API integration
- **Frontend**: Next.js UI for managing Twitter accounts

## Prerequisites

- Docker
- Docker Compose
- Local MongoDB running on `mongodb://localhost:27017`
- Twitter API Bearer Token (get it from [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard))

## Quick Start

### 1. Configure Twitter API Token

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Twitter Bearer Token:

```env
TWITTER_BEARER_TOKEN=your_actual_bearer_token_here
```

**How to get Twitter API Bearer Token:**
1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new App (or use existing)
3. Navigate to "Keys and tokens"
4. Generate/Copy your "Bearer Token"

### 2. Start all services

```bash
docker-compose up -d
```

This will start:
- Backend API on `localhost:8000`
- Frontend UI on `localhost:3000`

### 3. Access the application

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Stop all services

```bash
docker-compose down
```

### 5. Stop and remove all data

```bash
docker-compose down -v
```

## Development

### View logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

### Rebuild containers

```bash
docker-compose up -d --build
```

### Access MongoDB shell

```bash
mongosh eNews
```

## API Endpoints

- `GET /api/accounts` - List all Twitter accounts
- `POST /api/accounts` - Add new Twitter account
- `GET /api/accounts/{id}` - Get specific account
- `DELETE /api/accounts/{id}` - Delete account
- `GET /api/accounts/{id}/tweets` - Fetch tweets from account
- `POST /api/crawl/all` - Crawl all active accounts

## Database Collections

- `x_account` - Twitter account information
- `source-twitter` - Stored tweets from crawling

## Environment Variables

See `.env.example` for configuration options.

## Troubleshooting

### Backend won't start
```bash
docker-compose logs backend
```

### Frontend won't start
```bash
docker-compose logs frontend
```

### MongoDB connection issues
```bash
docker-compose logs mongodb
```
