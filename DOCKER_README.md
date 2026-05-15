# Running the Application with Docker

## Prerequisites

- Docker
- Docker Compose

## Setup

1. **Copy `.env.example` to `.env`:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** and add your values:
   - `JWT_SECRET` - secure secret key
   - `MAIL_*` - email credentials (e.g., Gmail)
   - `CLOUDINARY_*` - Cloudinary credentials

## Running the Application

### Start with Docker Compose

```bash
docker-compose up -d
```

This will:
- Create a PostgreSQL container with the database
- Create a FastAPI application container
- Run Alembic migrations
- Start the application at `http://localhost:8000`

### Check Status

```bash
docker-compose ps
```

### View Logs

```bash
docker-compose logs -f app
```

To view only database logs:
```bash
docker-compose logs -f db
```

## Stopping the Application

```bash
docker-compose down
```

To remove all data, including the database:
```bash
docker-compose down -v
```

## Useful Commands

### Execute Commands in Container

```bash
# Run bash in the app container
docker-compose exec app bash

# Run database management in the container
docker-compose exec app poetry run alembic current
```

### Rebuild Images

```bash
docker-compose build --no-cache
```

### Restart Application

```bash
docker-compose restart app
```

## Environment Variables

Main variables to configure in `.env`:

- **DATABASE_URL**: Automatically generated from POSTGRES_* variables
- **JWT_SECRET**: Secret key for JWT tokens (required!)
- **MAIL_***: Parameters for sending emails
- **CLOUDINARY_***: Parameters for cloud image storage

## Application Access

- **API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Alternative Documentation (ReDoc)**: http://localhost:8000/redoc
- **Database**: localhost:5432 (PostgreSQL)

## Troubleshooting

### Migrations Not Running

Check the logs:
```bash
docker-compose logs app
```

### Database Connection Error

Make sure the DB container is running and ready:
```bash
docker-compose ps
```

Check the DB logs:
```bash
docker-compose logs db
```

### Start from Scratch

```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```
