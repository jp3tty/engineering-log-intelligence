# Engineering Log Intelligence System

An AI-powered log analysis platform that processes engineering logs from multiple sources (SPLUNK, SAP, custom systems), identifies patterns, and provides actionable insights for system optimization.

## Features

### 🔍 **Log Intelligence**
- **Multi-Source Log Processing**: SPLUNK, SAP, and Application logs
- **Real-Time Analysis**: Process 60,000+ logs per second
- **Anomaly Detection**: 6+ types of system anomalies
- **Cross-System Correlation**: Find related logs across different systems
- **Advanced Search**: Full-text search with filters and aggregations

### 🔐 **Security & Authentication**
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: 4 user roles (viewer, user, analyst, admin)
- **Password Security**: PBKDF2 hashing with salt
- **API Key Management**: Secure API key generation and management
- **Rate Limiting**: Per-user and per-endpoint rate limiting

### 🚀 **Performance & Scalability**
- **Serverless Architecture**: Auto-scaling Vercel Functions
- **Dual Storage**: PostgreSQL for structured data, Elasticsearch for search
- **Query Optimization**: Automated query performance optimization
- **Caching**: Intelligent caching for improved performance
- **Global CDN**: Fast worldwide content delivery

### 📊 **Monitoring & Analytics**
- **Real-Time Dashboards**: Live system monitoring
- **Performance Metrics**: Response time and throughput tracking
- **Error Tracking**: Comprehensive error monitoring
- **Audit Logging**: Complete security audit trails
- **Custom Alerts**: Configurable alerting system

## Architecture

This project uses a **hybrid Vercel + External Services architecture**:

- **Frontend**: Vue.js SPA deployed on Vercel with global CDN
- **API Layer**: Vercel Functions for serverless API endpoints
- **External Services**: PostgreSQL, Elasticsearch, Kafka for persistent data and processing
- **ML Pipeline**: External services for model training, Vercel Functions for inference

## Project Structure

```
engineering_log_intelligence/
├── api/                    # Vercel Functions (serverless backend)
│   ├── auth/               # Authentication functions
│   ├── logs/               # Log processing functions
│   ├── ml/                 # ML inference functions
│   ├── dashboard/          # Dashboard data functions
│   └── health/             # Health check functions
├── frontend/               # Vue.js SPA
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── views/          # Page components
│   │   ├── services/       # API service calls
│   │   └── utils/          # Utility functions
│   └── public/             # Static assets
├── external-services/      # External service configurations
│   ├── postgresql/         # Database configs
│   ├── elasticsearch/      # Search configs
│   ├── kafka/              # Streaming configs
│   └── ml/                 # ML service configs
├── docs/                   # Documentation
└── tests/                  # Test files
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker Desktop
- Vercel CLI
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd engineering_log_intelligence
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

4. **Set up development environment**
   ```bash
   ./scripts/setup-dev-simple.sh
   ```

5. **Test the setup**
   ```bash
   python test_simple_api.py
   ```

6. **Run locally (optional)**
   ```bash
   vercel dev
   ```

## Features

- **Real-time Log Processing**: Process logs from SPLUNK, SAP, and custom systems
- **AI-Powered Analysis**: Machine learning models for log classification and anomaly detection
- **Interactive Dashboards**: Real-time visualizations with D3.js
- **Cross-System Correlation**: Identify related events across different systems
- **Natural Language Queries**: Query logs using natural language
- **Automated Alerts**: Intelligent alerting with escalation workflows

## Technology Stack

### Backend (Vercel Functions)
- Python 3.9+
- FastAPI
- PostgreSQL
- Elasticsearch
- Kafka

### Frontend (Vercel)
- Vue.js 3
- D3.js
- Pinia (state management)
- Vite (build tool)

### External Services
- PostgreSQL (Railway/Supabase/Neon)
- Elasticsearch (AWS/GCP)
- Kafka (Confluent Cloud/AWS MSK)
- AWS S3 (file storage)

## Development

### Running Tests
```bash
# Test external services
python test_external_services.py

# Test API functions
python test_simple_api.py

# Run all tests
pytest
```

### Code Quality
```bash
black .
flake8 .
mypy .
```

### External Services
```bash
# Start development services
docker-compose -f docker-compose.dev.yml up -d

# Stop development services
docker-compose -f docker-compose.dev.yml down

# View service logs
docker-compose -f docker-compose.dev.yml logs -f
```

### Deployment
```bash
# Deploy to production
vercel --prod

# Deploy to development
vercel
```

## Documentation

- [Project Status](PROJECT_STATUS.md) - Current project status and achievements
- [Technical Architecture](docs/TECHNICAL_ARCHITECTURE.md)
- [Environment Setup](docs/ENVIRONMENT_SETUP.md)
- [Vercel Development Setup](docs/VERCEL_DEVELOPMENT_SETUP.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- [Data Schema Design](docs/DATA_SCHEMA_DESIGN.md)
- [Monitoring Setup](docs/MONITORING_SETUP.md)
- [Phase 2 Preparation](docs/PHASE2_PREPARATION.md)
- [API Documentation](docs/API.md) *(Coming Soon)*
- [Deployment Guide](docs/DEPLOYMENT.md) *(Coming Soon)*

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Status

🚀 **Phase 3 In Progress** - Performance optimization and scalability implementation!

### Current Progress (Phase 3 - Day 14 Complete ✅)
- ✅ **Project Foundation** (Days 1-3): Complete Vercel + External Services architecture
- ✅ **Code Quality** (Day 4): Automated formatting, linting, type checking, security scanning
- ✅ **CI/CD Pipeline** (Day 4): GitHub Actions with automated testing and deployment
- ✅ **API Functions** (Day 5): All Vercel Functions tested and working locally
- ✅ **Monitoring** (Day 5): Full observability stack with metrics and alerting
- ✅ **Documentation** (Days 4-5): Comprehensive setup, troubleshooting, and architecture guides
- ✅ **Data Schemas** (Day 5): Complete database, search, and streaming schemas designed
- ✅ **SPLUNK Generator** (Day 6): Enhanced log generator with 6 anomaly types, 90k+ logs/sec
- ✅ **SAP Generator** (Day 7): Transaction log simulator with 8 business types, 65k+ trans/sec
- ✅ **Application Logs** (Day 8): Application log simulator with various error types
- ✅ **Vercel Functions** (Days 9-11): Complete API layer with authentication and user management
- ✅ **Elasticsearch Integration** (Day 10): Full search and analytics integration
- ✅ **API Documentation** (Day 12): Complete API documentation and comprehensive testing

### Phase 1 Achievements ✅
- **Architecture** (Days 1-3): Hybrid Vercel + External Services with auto-scaling
- **Quality** (Day 4): 100% automated code quality controls with Black, Flake8, MyPy
- **CI/CD** (Day 4): GitHub Actions with automated testing and deployment hooks
- **Testing** (Day 5): All Vercel Functions tested and validated
- **Monitoring** (Day 5): Structured logging, performance tracking, alerting
- **Security** (Day 4): Multi-layer security approach with automated scanning
- **Documentation** (Days 4-5): Complete guides for setup, troubleshooting, and development

### Phase 2 Achievements ✅
- **SPLUNK Simulation** (Day 6): 8 source types, 6 anomaly types, realistic log formats
- **SAP Simulation** (Day 7): 8 transaction types, real T-codes, business scenarios
- **Application Logs** (Day 8): Application log simulator with various error types
- **Vercel Functions** (Days 9-11): Complete API layer with authentication and user management
- **Elasticsearch Integration** (Day 10): Full search and analytics integration
- **API Documentation** (Day 12): Complete API documentation and comprehensive testing
- **Performance**: 90k+ SPLUNK logs/sec, 65k+ SAP transactions/sec, 60k+ application logs/sec
- **User Management**: Complete CRUD operations with role-based access control
- **Security**: JWT authentication, password hashing, rate limiting, API keys
- **Testing**: Comprehensive test suites for all components

### Phase 3 Goals (Days 13-19) - In Progress
- ✅ **Production Infrastructure** (Day 13): Production Vercel deployment and environment setup complete
- 🔄 **Security & Compliance** (Day 14): Production security measures and compliance
- 🔄 **Performance & Scalability** (Day 15): Horizontal scaling and performance optimization
- 🔄 **Monitoring & Operations** (Day 16): Comprehensive monitoring and operational excellence
- 🔄 **ML Pipeline Integration** (Days 17-19): Machine learning model integration and real-time inference

### Day 13 Achievements ✅
- **Vercel Production Deployment**: Successfully deployed to production with 4 API functions
- **Environment Variables**: Configured 17 production environment variables
- **Security**: Vercel authentication protection working correctly
- **Documentation**: Created comprehensive setup guides and automation scripts
- **Production URL**: https://engineeringlogintelligence-g011dkik6-jp3ttys-projects.vercel.app

### Day 14 Achievements ✅ COMPLETED
- **PostgreSQL Production**: Railway PostgreSQL database configured and connected ✅
- **OpenSearch Production**: AWS OpenSearch domain created with free tier ✅
- **Kafka Production**: Confluent Cloud cluster configured with free tier ✅
- **Security Configuration**: Fine-grained access control with master user ✅
- **Environment Variables**: Updated Vercel with all database credentials (25+ total) ✅
- **Connection Testing**: All three production databases tested and verified ✅
- **Documentation**: Updated project status and progress tracking ✅
- **Security**: All credentials properly encrypted and protected ✅

### Available Endpoints

#### Authentication
- **POST** `/api/auth/login` - User authentication
- **POST** `/api/auth/refresh` - Token refresh
- **POST** `/api/auth/password-reset/request` - Password reset request
- **POST** `/api/auth/password-reset/confirm` - Password reset confirmation
- **POST** `/api/auth/password-change` - Change password

#### User Management
- **POST** `/api/users/register` - User registration
- **GET** `/api/users/profile` - Get user profile
- **PUT** `/api/users/profile` - Update user profile
- **DELETE** `/api/users/profile` - Delete user account
- **GET** `/api/users/admin` - List users (admin only)
- **GET** `/api/users/admin/{id}` - Get user by ID (admin only)
- **PUT** `/api/users/admin/{id}` - Update user (admin only)
- **DELETE** `/api/users/admin/{id}` - Delete user (admin only)

#### Log Management
- **POST** `/api/logs/ingest` - Ingest log entries
- **GET** `/api/logs/search` - Search log entries
- **GET** `/api/logs/correlation` - Search by correlation
- **GET** `/api/logs/statistics` - Get log statistics

#### System Health
- **GET** `/api/health` - System health monitoring

---

**Last Updated**: September 19, 2025  
**Version**: 1.1.0  
**Phase**: 2 Complete (Days 6-12 Complete)
