# Setup Backend on New Machine

## Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Git (optional, for version control)

## Steps to Setup

### 1. Extract the Zip File
```powershell
# Extract backend-source-only.zip to your desired location
# For example: C:\Projects\VisitorModule\backend
```

### 2. Navigate to Backend Folder
```powershell
cd "path\to\extracted\backend"
```

### 3. Create Virtual Environment (Recommended)
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate

# On Linux/Mac:
# source venv/bin/activate
```

### 4. Install Dependencies
```powershell
# Install all required packages
pip install -r requirements.txt
```

### 5. Set Up Environment Variables
Create a `.env` file in the backend folder with your configuration:
```env
# Database Configuration
DB_HOST=your_database_host
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_PORT=3306

# AWS Configuration (if using AWS services)
AWS_REGION=your_region
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Other configurations
DEBUG=True
```

### 6. Initialize Database (if needed)
```powershell
# Run database schema creation scripts
# Update the connection details in the SQL files first
mysql -u your_user -p your_database < database_schema.sql
mysql -u your_user -p your_database < create_appointment_table.sql
mysql -u your_user -p your_database < vis_admin_complete.sql
```

### 7. Test the Setup
```powershell
# Run a simple test
python -c "import fastapi; print('FastAPI installed successfully')"

# Or run your application
python app/main.py
```

## For AWS Lambda Deployment

### 1. Install AWS CLI
```powershell
# Download and install AWS CLI from: https://aws.amazon.com/cli/
```

### 2. Configure AWS Credentials
```powershell
aws configure
# Enter your AWS Access Key ID, Secret Access Key, Region, and output format
```

### 3. Build Lambda Layer (if needed)
```powershell
# Follow the instructions in CREATE_LAYER_ON_WINDOWS.md
.\create_lambda_layer_windows.bat
```

### 4. Deploy to Lambda
```powershell
# Use the deployment scripts
.\deploy-all.bat
# Or follow AWS_CONSOLE_SETUP_GUIDE.md for manual deployment
```

## Common Issues & Solutions

### Issue: pip install fails
**Solution:** 
```powershell
# Upgrade pip
python -m pip install --upgrade pip
```

### Issue: Module not found errors
**Solution:**
```powershell
# Make sure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Database connection errors
**Solution:**
- Verify database credentials in .env file
- Ensure database server is running
- Check firewall settings

## Quick Start Commands
```powershell
# Complete setup in one go (Windows)
python -m venv venv
.\venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "from app.main import app; print('✓ Backend setup complete!')"
```

## Directory Structure After Setup
```
backend/
├── app/              # Application source code
├── venv/             # Virtual environment (created)
├── .env              # Environment variables (create this)
├── requirements.txt  # Dependencies list
├── lambda_handler.py # Lambda entry point
└── ...               # Other configuration files
```

## Next Steps
1. Configure your database connection
2. Set up environment variables
3. Test the application locally
4. Deploy to AWS Lambda (if needed)
5. Configure API Gateway

For detailed deployment instructions, refer to:
- `LAMBDA_DEPLOYMENT_GUIDE.md`
- `AWS_CONSOLE_SETUP_GUIDE.md`
- `API_GATEWAY_SETUP_STEPS.md`
