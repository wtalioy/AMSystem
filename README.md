# Automobile Maintenance System (AMS)

The Automobile Maintenance System is a comprehensive solution for managing automotive repair businesses, providing user management, vehicle management, order processing, technician task assignment, etc.

## Requirements

- Python 3.13
- Microsoft SQL Server (or any ODBC-compliant relational database)
- ODBC Driver 17 for SQL Server (or compatible driver for your database)

## Quick Start

### 1. Database Setup

Create a database in SQL Server:

```sql
CREATE DATABASE AMS;
USE AMS;
```

### 2. Install Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the `backend` directory:

```
# API Configuration
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database Configuration
DRIVER={ODBC Driver 17 for SQL Server}
SERVER=your_server_name_or_ip
DATABASE=AMS
UID=your_database_username
PWD=your_database_password
```

### 4. Start the Service

```powershell
cd backend
python main.py
```

The service will run at http://127.0.0.1:8000.

API documentation can be viewed at http://127.0.0.1:8000/docs.

For more detailed API documentation, please refer to [docs/api.md](docs/api.md).
