# KYC System Port Configuration

This document explains the port configuration for the KYC system components.

## 🚀 Port Assignments

| Component | Port | URL | Description |
|-----------|------|-----|-------------|
| **API Server** | 8000 | http://localhost:8000 | FastAPI backend server |
| **Admin Dashboard** | 3000 | http://localhost:3000 | React admin interface |
| **Customer Portal** | 3001 | http://localhost:3001 | React customer interface |

## 📋 Quick Start

### Option 1: Start All Components (Recommended)
```bash
# Start API server
cd src && python api_server.py

# In another terminal, start both portals
python start_portals.py
```

### Option 2: Start Components Individually
```bash
# 1. Start API server
cd src && python api_server.py

# 2. Start Admin Dashboard (Port 3000)
cd admin-dashboard && npm start

# 3. Start Customer Portal (Port 3001)
cd customer-portal && npm start
```

## 🔧 Configuration Details

### Admin Dashboard (Port 3000)
- **Package.json**: `"start": "PORT=3000 react-scripts start"`
- **Purpose**: Administrative interface for KYC case management
- **Features**: Dashboard, case details, manual review, processing steps

### Customer Portal (Port 3001)
- **Package.json**: `"start": "PORT=3001 react-scripts start"`
- **Purpose**: Customer-facing interface for KYC submission
- **Features**: Document upload, form submission, status tracking

### API Server (Port 8000)
- **CORS Configuration**: Allows both ports 3000 and 3001
- **Endpoints**: 
  - `/api/dashboard` - Admin dashboard data
  - `/api/customer/*` - Customer portal endpoints
  - `/api/cases/*` - Case management endpoints

## 🌐 Access URLs

Once all components are running:

- **Admin Dashboard**: http://localhost:3000
- **Customer Portal**: http://localhost:3001
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/api/health

## 🔄 Development Workflow

1. **Start API Server**: Always start the API server first
2. **Start Portals**: Use the startup script or start individually
3. **Development**: Make changes to React components (hot reload enabled)
4. **Testing**: Test both portals simultaneously

## 🛠️ Troubleshooting

### Port Already in Use
If you get a "port already in use" error:

```bash
# Find process using the port
lsof -i :3000  # or :3001, :8000

# Kill the process
kill -9 <PID>
```

### CORS Issues
If you see CORS errors, ensure the API server is running and the CORS configuration includes both ports.

### React Scripts Issues
If npm start fails, try:
```bash
cd customer-portal  # or admin-dashboard
npm install
npm start
```

## 📝 Notes

- Both React apps use hot reloading for development
- The API server must be running for the portals to function
- Port 3000 is the default React port, so admin dashboard uses it
- Port 3001 is explicitly set for customer portal to avoid conflicts
- All components can run simultaneously on the same machine 