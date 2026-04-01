# 🩸 Smart Geo-Enabled Blood Donor Management System

A comprehensive web application that connects blood donors with recipients using geo-location technology and machine learning predictions.

## 🌟 Features

- **Real-time Donor Discovery**: Find nearby blood donors instantly
- **Geo-Location Search**: Search donors within 10km radius using interactive maps
- **ML Predictions**: AI-powered donor availability and blood demand forecasting
- **Emergency Alerts**: Instant notifications to matching donors during emergencies
- **Eligibility Management**: Automatic 90-day donation eligibility tracking
- **Certificate Generation**: Downloadable donation certificates with QR codes
- **Admin Dashboard**: Comprehensive analytics and management tools
- **Hospital Integration**: Register and locate nearby hospitals

## 🛠️ Technology Stack

### Backend
- **Python 3.9+**
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Flask-Login** - Authentication
- **Flask-WTF** - Forms

### Machine Learning
- **Scikit-learn** - ML models
- **Pandas/NumPy** - Data processing
- **Joblib** - Model persistence

### Frontend
- **HTML5/CSS3**
- **Bootstrap 5** - UI framework
- **JavaScript** - Client-side logic
- **Leaflet.js** - Interactive maps
- **Chart.js** - Data visualization

### Database
- **SQLite** (Development)
- **PostgreSQL** (Production ready)

### Additional Tools
- **ReportLab** - PDF certificate generation
- **QRCode** - QR code generation
- **Geopy** - Distance calculations
- **Gunicorn** - WSGI server

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git
- Virtual environment (recommended)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/blood-donor-finder.git
   cd blood-donor-finder