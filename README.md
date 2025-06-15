# Automobile Maintenance System (AMS)

The Automobile Maintenance System is a comprehensive solution for managing automotive repair businesses, providing user management, vehicle management, order processing, technician task assignment, etc.

## Requirements

- Python 3.13
- Microsoft SQL Server (or any ODBC-compliant relational database)
- ODBC Driver 17 for SQL Server (or compatible driver for your database)

## Quick Start

### 1. Database Setup

Create a database:

```sql
CREATE DATABASE AMS;
USE AMS;
```

### 2. Backend Setup

#### Install Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

#### Environment Configuration

Create a `.env` file in the `backend` directory:

```
# Database Configuration
DRIVER={ODBC Driver 17 for SQL Server}
SERVER=your_server_name_or_ip
DATABASE=AMS
UID=your_database_username
PWD=your_database_password

# Security Configuration
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Background Configuration
ASSIGNMENT_PROCESSOR_INTERVAL=30
```

#### Start the Backend Service

```powershell
cd backend
python main.py
```

The backend service will run at http://127.0.0.1:8000.

API documentation can be viewed at http://127.0.0.1:8000/docs.

### 3. Frontend Setup

#### Install Dependencies

Make sure you have Node.js (version 16 or higher) installed on your system.

```powershell
cd frontend
npm install
```

#### Start the Development Server

```powershell
cd frontend
npm run dev
```

The frontend application will run at http://localhost:5173 (or another port if 5173 is occupied).

#### Build for Production

To build the frontend for production:

```powershell
cd frontend
npm run build
```
