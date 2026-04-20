# Rental Management System

A production-ready web application for managing rental properties, tenants, and financial records. Built with a modern backend stack and designed for serverless deployment.

## Overview

This system provides a comprehensive platform for landlords and property managers to:
- Manage properties and units.
- Track tenant registration and lease agreements.
- Automate rent payment tracking and overdue notifications.
- Generate financial reports and AI-powered narratives.
- Dashboard for administrative overview of system metrics.

## Technical Stack

### Backend
- Framework: FastAPI
- ORM: SQLAlchemy (Asynchronous)
- Database: PostgreSQL (Supabase)
- Authentication: JWT-based secure auth

### Frontend
- Structure: HTML5
- Styling: Vanilla CSS (Custom design system)
- Logic: JavaScript (ES6+)

### Infrastructure
- Deployment: Vercel
- Database Hosting: Supabase
- Integration: SMTP for email notifications, M-PESA for payment processing (optional)

## Project Structure

```text
├── api/                # Vercel serverless entry points
├── backend/            # Main application logic
│   ├── app/
│   │   ├── api/        # API endpoints and dependencies
│   │   ├── core/       # Core config and database engines
│   │   ├── models/     # SQLAlchemy database models
│   │   ├── schemas/    # Pydantic validation schemas
│   │   └── services/   # Business logic (AI, payments)
├── frontend/           # Static frontend assets (HTML, CSS, JS)
├── vercel.json         # Vercel routing configuration
└── requirements.txt    # Python dependencies
```

## Local Setup

### Prerequisites
- Python 3.8+
- PostgreSQL database

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd RMS
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables in `backend/.env`:
   ```text
   DATABASE_URL=your_postgresql_url
   SECRET_KEY=your_secret_key
   ALGORITHM=HS256
   ```

5. Run the application:
   ```bash
   uvicorn backend.app.main:app --reload
   ```

## Deployment to Vercel

The application is specifically optimized for Vercel's serverless environment.

### Optimization Highlights
- Serverless-friendly database pooling (NullPool).
- Automated routing for static and API assets via `vercel.json`.
- Compatible with Supabase Transaction Mode pooler (Port 6543).

### Configuration
1. Connect your GitHub repository to Vercel.
2. Set the following Environment Variables in the Vercel Dashboard:
   - `DATABASE_URL`: Your Supabase connection string.
   - `SECRET_KEY`: A secure random string for JWT signatures.
   - `VERCEL`: Set to `1`.

## Maintenance

To initialize or update the database schema in production, use the provided setup endpoint (with caution):
`/setup-db`

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.
