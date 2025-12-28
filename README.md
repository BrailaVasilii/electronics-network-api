# Electronics Network API

![CI](https://github.com/BrailaVasilii/electronics-network-api/workflows/CI/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Django](https://img.shields.io/badge/django-5.2-green.svg)
![DRF](https://img.shields.io/badge/DRF-3.15-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A Django REST Framework API for managing a hierarchical electronics supply chain network with three levels: Factory (level 0), Retail Network (level 1), and Individual Entrepreneur (level 2). Features automated level calculation, supplier hierarchy management, and comprehensive admin panel with 94% test coverage.

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Local Installation](#-local-installation)
- [Docker Installation](#-docker-installation)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Environment Variables](#-environment-variables)
- [Admin Panel](#-admin-panel)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

## 🚀 Features

- **Three-level hierarchical network structure** - Factory → Retail Network → Individual Entrepreneur
- **Self-referencing supplier relationships** - Nodes can have suppliers from higher levels
- **Automatic level calculation** - Smart hierarchy level assignment based on supplier chain
- **Circular reference prevention** - Validation prevents infinite loops in supplier chains
- **Protected debt field** - Debt is read-only via API, can only be modified in admin panel
- **Advanced filtering** - Filter by country, city, level with search functionality
- **Active staff-only API access** - Secure permission system for API endpoints
- **Comprehensive Django Admin** - Custom admin interface with actions and filters
- **Docker Compose setup** - Production-ready containerized deployment
- **CI/CD pipeline** - Automated testing with GitHub Actions
- **High test coverage** - 94% coverage with 59 comprehensive tests

## 🛠 Tech Stack

- **Python 3.12** - Core programming language
- **Django 5.2** - Web framework
- **Django REST Framework 3.15** - API framework
- **PostgreSQL 15** - Primary database
- **Redis 7** - Caching and session storage
- **Poetry** - Dependency management
- **Docker & Docker Compose** - Containerization
- **GitHub Actions** - CI/CD pipeline
- **pytest & coverage** - Testing framework

## 📁 Project Structure

```
electronics-network-api/
├── config/
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI application
├── network/
│   ├── __init__.py
│   ├── admin.py             # Django admin customization
│   ├── apps.py              # App configuration
│   ├── models.py            # NetworkNode and Product models
│   ├── permissions.py       # Custom permission classes
│   ├── serializers.py       # DRF serializers
│   ├── urls.py              # App URL patterns
│   ├── views.py             # API viewsets
│   ├── migrations/          # Database migrations
│   └── tests/               # Test suite
│       ├── __init__.py
│       ├── test_admin.py    # Admin interface tests
│       ├── test_api.py      # API endpoint tests
│       └── test_models.py   # Model logic tests
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI pipeline
├── docker-compose.yml       # Production Docker setup
├── docker-compose.override.yml  # Development overrides
├── Dockerfile              # Docker image configuration
├── docker-entrypoint.sh    # Container startup script
├── .dockerignore           # Docker build exclusions
├── .env.example            # Environment variables template
├── pyproject.toml          # Poetry dependencies and tool config
├── poetry.lock             # Locked dependency versions
├── manage.py               # Django management script
└── README.md               # Project documentation
```

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Poetry (for dependency management)
- Docker & Docker Compose (optional, for containerized setup)

## 🔧 Local Installation

### 1. Clone the repository
```bash
git clone https://github.com/BrailaVasilii/electronics-network-api.git
cd electronics-network-api
```

### 2. Install dependencies with Poetry
```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install
```

### 3. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 4. Set up PostgreSQL database
```bash
# Create database
createdb electronics_network_db

# Or using psql
psql -c "CREATE DATABASE electronics_network_db;"
```

### 5. Run migrations
```bash
poetry run python manage.py migrate
```

### 6. Create superuser
```bash
poetry run python manage.py createsuperuser
```

### 7. Start development server
```bash
poetry run python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`
Admin panel at `http://localhost:8000/admin/`

## 🐳 Docker Installation

### 1. Clone the repository
```bash
git clone https://github.com/BrailaVasilii/electronics-network-api.git
cd electronics-network-api
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Edit .env for Docker (DB_HOST=db, REDIS_URL=redis://redis:6379/0)
```

### 3. Build and start containers
```bash
# Production setup
docker-compose up --build

# Development setup with auto-reload
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build
```

### 4. Access the application
- API: `http://localhost:8000/api/`
- Admin: `http://localhost:8000/admin/`
- Database: `localhost:5432`
- Redis: `localhost:6379`

### 5. Create superuser (if needed)
```bash
docker-compose exec web python manage.py createsuperuser
```

## 📖 API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Authentication
API requires active staff user authentication. Use Django admin to create users.

### Endpoints

#### Network Nodes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/nodes/` | List all network nodes |
| `POST` | `/api/nodes/` | Create new network node |
| `GET` | `/api/nodes/{id}/` | Retrieve specific node |
| `PUT` | `/api/nodes/{id}/` | Update node (full) |
| `PATCH` | `/api/nodes/{id}/` | Update node (partial) |
| `DELETE` | `/api/nodes/{id}/` | Delete node |

#### Filtering & Search

```bash
# Filter by country
GET /api/nodes/?country=USA

# Filter by city
GET /api/nodes/?city=Seoul

# Filter by hierarchy level
GET /api/nodes/?level=0

# Search by name or email
GET /api/nodes/?search=Samsung

# Combine filters
GET /api/nodes/?country=USA&level=1&search=tech
```

### API Examples

#### Create a Factory (Level 0)
```bash
curl -X POST http://localhost:8000/api/nodes/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Session <your-session>" \
  -d '{
    "name": "Samsung Electronics",
    "node_type": "factory",
    "email": "contact@samsung.com",
    "country": "South Korea",
    "city": "Seoul",
    "street": "Samsung Digital City",
    "house_number": "1"
  }'
```

#### Create a Retail Network (Level 1)
```bash
curl -X POST http://localhost:8000/api/nodes/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Session <your-session>" \
  -d '{
    "name": "Tech World Store",
    "node_type": "retail",
    "email": "info@techworld.com",
    "country": "USA",
    "city": "New York",
    "street": "Broadway",
    "house_number": "123",
    "supplier": 1
  }'
```

#### Python requests example
```python
import requests

# List all nodes
response = requests.get(
    'http://localhost:8000/api/nodes/',
    headers={'Authorization': 'Session <your-session>'}
)
nodes = response.json()

# Create a new node
new_node = {
    'name': 'Local Electronics',
    'node_type': 'entrepreneur',
    'email': 'owner@local-electronics.com',
    'country': 'USA',
    'city': 'Boston',
    'street': 'Main Street',
    'house_number': '456',
    'supplier': 2
}

response = requests.post(
    'http://localhost:8000/api/nodes/',
    json=new_node,
    headers={'Authorization': 'Session <your-session>'}
)
```

### Response Format

```json
{
  "id": 1,
  "name": "Samsung Electronics",
  "node_type": "factory",
  "email": "contact@samsung.com",
  "country": "South Korea",
  "city": "Seoul",
  "street": "Samsung Digital City",
  "house_number": "1",
  "supplier": null,
  "level": 0,
  "debt": "0.00",
  "created_at": "2023-12-01T10:30:00Z",
  "products": [
    {
      "id": 1,
      "name": "Galaxy S24",
      "model": "SM-S921",
      "release_date": "2024-01-17"
    }
  ]
}
```

## 🧪 Testing

### Run all tests
```bash
# Local environment
poetry run pytest

# With coverage
poetry run coverage run -m pytest
poetry run coverage report
poetry run coverage html

# Docker environment
docker-compose exec web python manage.py test
```

### Run specific test modules
```bash
# Model tests
poetry run pytest network/tests/test_models.py

# API tests
poetry run pytest network/tests/test_api.py

# Admin tests
poetry run pytest network/tests/test_admin.py
```

### Test Coverage
Current test coverage: **94%** (59 tests)
- Model validation and logic: ✅
- API endpoints and permissions: ✅
- Admin interface functionality: ✅
- Data integrity and constraints: ✅

## 🔧 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Django secret key | `django-insecure-...` | Yes |
| `DEBUG` | Enable debug mode | `True` | No |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` | No |
| `DB_NAME` | PostgreSQL database name | `electronics_network_db` | Yes |
| `DB_USER` | PostgreSQL username | `postgres` | Yes |
| `DB_PASSWORD` | PostgreSQL password | `postgres_pass` | Yes |
| `DB_HOST` | PostgreSQL host | `localhost` (Docker: `db`) | Yes |
| `DB_PORT` | PostgreSQL port | `5432` | No |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` | No |
| `CORS_ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000` | No |
| `DJANGO_SUPERUSER_USERNAME` | Auto-created superuser name | `admin` | No |
| `DJANGO_SUPERUSER_EMAIL` | Auto-created superuser email | `admin@example.com` | No |
| `DJANGO_SUPERUSER_PASSWORD` | Auto-created superuser password | `admin123` | No |

## 👨‍💼 Admin Panel

Access the Django admin panel at `http://localhost:8000/admin/`

### Features
- **Network Node Management**: Create, edit, delete network nodes
- **Supplier Hierarchy Visualization**: Clickable supplier links
- **Advanced Filtering**: Filter by city, level, node type
- **Bulk Actions**: Clear debt for multiple nodes
- **Product Management**: Inline product editing
- **Search Functionality**: Search by name, city, email

### Admin Actions
- **Clear Debt**: Set debt to 0.00 for selected nodes
- **Export**: Export node data (can be extended)

## 💻 Development

### Code Style
The project follows PEP 8 style guidelines with these tools:

```bash
# Format code with Black
poetry run black network/ config/

# Sort imports with isort
poetry run isort network/ config/

# Check style with flake8
poetry run flake8 network/ config/
```

### Pre-commit Hooks (Optional)
```bash
# Install pre-commit
poetry add --group dev pre-commit

# Set up hooks
pre-commit install
```

### Database Migrations
```bash
# Create migrations
poetry run python manage.py makemigrations

# Apply migrations
poetry run python manage.py migrate

# Show migration status
poetry run python manage.py showmigrations
```

### Adding New Features
1. Create feature branch: `git checkout -b feature/new-feature`
2. Write tests first (TDD approach)
3. Implement feature
4. Run tests: `poetry run pytest`
5. Check code style: `poetry run black . && poetry run flake8`
6. Commit and push
7. Create pull request

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Write tests for new features
- Follow PEP 8 style guidelines
- Add docstrings to functions and classes
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

**Author**: Braila Vasile  
**Email**: braila.vasile@example.com  
**GitHub**: [@BrailaVasilii](https://github.com/BrailaVasilii)  
**Project Link**: [https://github.com/BrailaVasilii/electronics-network-api](https://github.com/BrailaVasilii/electronics-network-api)

---

⭐ If you found this project helpful, please consider giving it a star!
