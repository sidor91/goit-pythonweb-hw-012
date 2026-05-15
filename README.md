
# Contacts app

An app with CRUD operations for contacts

## Prerequisites

Before you begin, ensure you have the following installed:
* **Python 3.10+**
* **Poetry** (Dependency management)

---

## Getting Started: Local Installation

Follow these steps to set up and run the project locally.

### 1. Pull the repo
```bash
git clone https://github.com/sidor91/goit-pythonweb-hw-08
cd goit-pythonweb-hw-08
```

### 2. Environment Configuration
The application requires environment variables to function correctly. Create a `.env` file in the root directory by copying the provided example:

```bash
cp .env.example .env
```
### 3. Add env variables
The mandatory env variables are marked with "required"

### 4. Install dependencies
```bash
poetry install --no-root
```
### 5. Run migrations
```bash
poetry run alembic upgrade head
```

### 6. Run the app
```bash
poetry run python main.py
```

### 7. Navigate to API Swagger docs
```bash
http://127.0.0.1:8000/docs
```
*In the example above the port is 8000, but in your case it will be according to env variable*

### 8. Enjoy =))
