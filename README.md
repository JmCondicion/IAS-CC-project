# QR Attendance System

A Flask-based QR code attendance system with webcam scanning, real-time dashboard, and production-ready deployment options.

## Features

- 📷 **Webcam QR Scanner** - Real-time QR code scanning using html5-qrcode library
- 📊 **Live Dashboard** - Auto-refreshing attendance table with filters
- 🔐 **Admin Panel** - Secure admin authentication with Flask-Login
- ⏱️ **Cooldown Protection** - 10-minute cooldown between duplicate scans
- 🚀 **Rate Limiting** - IP-based rate limiting (10 req/min)
- 📱 **Responsive Design** - Mobile-friendly academic UI
- 🐳 **Docker Ready** - Complete Docker & Kubernetes deployment files
- 🗄️ **MySQL + Redis** - Production-grade database and caching

## Project Structure

```
qr-attendance/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/
│   │   └── __init__.py      # SQLAlchemy models
│   ├── routes/
│   │   ├── main.py          # API routes
│   │   └── admin.py         # Admin routes
│   ├── utils/
│   │   ├── base.py          # DB setup
│   │   ├── helpers.py       # Utility functions
│   │   ├── schemas.py       # Marshmallow schemas
│   │   └── auth.py          # Auth helpers
│   ├── static/
│   │   ├── css/style.css    # Styles
│   │   └── js/scanner.js    # Frontend JS
│   └── templates/
│       └── index.html       # Main page
├── k8s/                     # Kubernetes manifests
├── tests/                   # Pytest tests
├── migrations/              # Database migrations
├── app.py                   # Entry point
├── docker-compose.yml       # Docker Compose config
├── Dockerfile               # Docker image
├── requirements.txt         # Python dependencies
└── setup.sh                 # Setup script
```

## Quick Start

### 1. Clone and Setup

```bash
# Clone repository
cd qr-attendance

# Run setup script
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Copy environment file
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/qr_attendance
REDIS_URL=redis://localhost:6379/0
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-password
```

### 3. Initialize Database

```bash
# Using Flask-Migrate
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Or simple init
flask init-db
```

### 4. Run Application

```bash
flask run --host=0.0.0.0 --port=5000
```

Visit: `http://localhost:5000`

## Docker Deployment

### Development (Docker Compose)

```bash
docker-compose up -d
```

Services:
- Flask App: http://localhost:5000
- phpMyAdmin: http://localhost:8080
- MySQL: localhost:3306
- Redis: localhost:6379

### Production (Kubernetes)

```bash
# Apply secrets
kubectl apply -f k8s/flask-secret.yaml

# Apply storage
kubectl apply -f k8s/mysql-pvc.yaml

# Deploy MySQL
kubectl apply -f k8s/mysql-deployment.yaml
kubectl apply -f k8s/mysql-service.yaml

# Deploy Flask
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Access via NodePort: `http://<node-ip>:30080`

## API Documentation

### Endpoints

#### POST `/api/scan_qr`
Scan QR code and record attendance.

**Request:**
```json
{
  "qr_data": "uuid-string"
}
```

**Response:**
```json
{
  "status": "success",
  "name": "John Doe",
  "student_id": "STU001",
  "time": "2024-01-15T10:30:00",
  "status": "IN",
  "message": "Attendance marked as IN"
}
```

#### GET `/api/attendance`
Get paginated attendance records.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Records per page (default: 20)
- `date` (string): Filter by date (YYYY-MM-DD)
- `student_id` (int): Filter by student ID

**Response:**
```json
{
  "status": "success",
  "records": [...],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "pages": 5
}
```

#### POST `/api/register`
Register a new student.

**Request:**
```json
{
  "student_id": "STU002",
  "name": "Jane Smith",
  "course": "Mathematics"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Student registered successfully",
  "student": {...},
  "qr_code": "uuid-string"
}
```

### Error Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 400  | Bad Request (invalid payload, cooldown active) |
| 404  | Not Found (invalid QR code) |
| 500  | Internal Server Error |

## Running Tests

```bash
# Install test dependencies
pip install pytest

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## Admin Panel

Access admin panel at `/admin/login`

Default credentials (change in `.env`):
- Username: `admin`
- Password: `secure-admin-password`

Admin features:
- Dashboard with statistics
- Student management
- Attendance records viewer

## Security Features

- ✅ Rate limiting (Flask-Limiter)
- ✅ Input validation (Marshmallow)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ CORS headers configured
- ✅ HTTPS redirect middleware (production)
- ✅ Non-root Docker user
- ✅ Secrets management (Kubernetes Secrets)

## Technology Stack

**Backend:**
- Flask 3.0
- SQLAlchemy (ORM)
- Flask-Migrate (Migrations)
- Marshmallow (Validation)
- Redis (Caching)
- PyZbar (QR decoding)

**Frontend:**
- HTML5/CSS3
- Vanilla JavaScript
- html5-qrcode library
- Responsive design

**Infrastructure:**
- Docker & Docker Compose
- Kubernetes (K8s)
- MySQL 8.0
- Redis 7

## Troubleshooting

### Camera not working
- Ensure HTTPS in production (camera requires secure context)
- Allow camera permissions in browser
- Check browser compatibility

### Database connection error
- Verify MySQL is running
- Check DATABASE_URL in `.env`
- Ensure database exists

### QR scanning issues
- Ensure good lighting
- Hold QR code steady within frame
- Clean camera lens

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**Made with ❤️ for Academic Institutions**
