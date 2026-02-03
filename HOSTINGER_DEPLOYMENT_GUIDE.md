# Hostinger Cloud Startup Deployment Guide

## Overview
This guide covers deploying your React + FastAPI application to Hostinger Cloud Startup subscription.

## Project Structure
- **Frontend**: React app with modern UI components (Radix UI, Tailwind CSS)
- **Backend**: FastAPI with extensive dependencies including AI/ML libraries
- **Database**: SQLite/MySQL support

## Deployment Options for Hostinger Cloud Startup

### Option 1: Static Frontend + Separate Backend Hosting (Recommended)

#### Step 1: Fix Dependencies and Build Frontend

**IMPORTANT: Dependency fixes have been applied to resolve build errors**

1. **Use the automated build script**:
   ```bash
   # On Windows:
   deploy-frontend.bat
   
   # On Linux/Mac:
   chmod +x deploy-frontend.sh
   ./deploy-frontend.sh
   ```

2. **Manual build process** (if script fails):
   ```bash
   cd frontend
   
   # Clean previous installations
   rm -rf node_modules package-lock.json yarn.lock
   
   # Install with legacy peer deps to resolve conflicts
   npm install --legacy-peer-deps
   
   # Build for production
   npm run build
   ```

3. **Upload to Hostinger**:
   - Access your Hostinger hPanel
   - Go to File Manager
   - Navigate to `public_html` folder
   - Upload the contents of `frontend/build` folder
   - Ensure `index.html` is in the root of `public_html`

**Fixed Issues:**
- ✅ Date-fns version conflict (downgraded to 3.6.0)
- ✅ React Router compatibility (downgraded to 6.26.2)  
- ✅ ajv module resolution errors (added overrides)
- ✅ Node.js v18 compatibility

#### Backend Deployment Options:
Since Hostinger Cloud Startup has limitations for Python applications, consider these options:

**A. External Backend Hosting (Recommended)**:
- Deploy backend to Railway, Render, or Heroku
- Update frontend API endpoints to point to external backend
- Use environment variables for API URLs

**B. Hostinger VPS Upgrade**:
- Upgrade to Hostinger VPS for full Python support
- Install Python, pip, and dependencies
- Set up systemd service for FastAPI

### Option 2: Full Stack on VPS (If Upgraded)

#### Prerequisites
- Upgrade to Hostinger VPS
- SSH access to server

#### Backend Setup on VPS
1. **Install Python and dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv nginx
   ```

2. **Clone and setup project**:
   ```bash
   git clone <your-repo>
   cd franch/backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Create systemd service** (`/etc/systemd/system/franch-api.service`):
   ```ini
   [Unit]
   Description=Franch FastAPI
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/franch/backend
   Environment="PATH=/path/to/franch/backend/venv/bin"
   ExecStart=/path/to/franch/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

4. **Configure Nginx** (`/etc/nginx/sites-available/franch`):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       # Frontend
       location / {
           root /var/www/html;
           try_files $uri $uri/ /index.html;
       }

       # Backend API
       location /api/ {
           proxy_pass http://localhost:8000/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

## Current Hostinger Cloud Startup Limitations

### What's Supported:
- ✅ Static HTML/CSS/JS files
- ✅ PHP applications
- ✅ MySQL databases
- ✅ SSL certificates
- ✅ Custom domains

### What's NOT Supported:
- ❌ Python/FastAPI applications
- ❌ Node.js applications
- ❌ Custom server configurations
- ❌ SSH access
- ❌ Root access

## Recommended Deployment Strategy

### Step 1: Deploy Frontend to Hostinger
1. Build React app:
   ```bash
   cd frontend
   npm run build
   ```

2. Upload `build` folder contents to `public_html` in Hostinger File Manager

### Step 2: Deploy Backend Externally
Choose one of these free/low-cost options:

**Railway** (Recommended):
1. Connect GitHub repository
2. Select backend folder
3. Railway auto-detects Python
4. Set environment variables
5. Deploy automatically

**Render**:
1. Connect repository
2. Create new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Heroku**:
1. Create `Procfile`: `web: uvicorn main:app --host 0.0.0.0 --port $PORT`
2. Deploy via Git or GitHub integration

### Step 3: Configure Frontend API Endpoints
Update your React app's API configuration to point to the external backend URL.

## Environment Variables Setup

### Frontend (.env):
```env
REACT_APP_API_URL=https://your-backend-url.railway.app
REACT_APP_ENVIRONMENT=production
```

### Backend (.env):
```env
DATABASE_URL=your-database-connection-string
SECRET_KEY=your-secret-key
CORS_ORIGINS=https://your-domain.com
```

## Database Options

### For External Backend:
- **PostgreSQL**: Railway, Render provide free tiers
- **MongoDB**: MongoDB Atlas free tier
- **MySQL**: PlanetScale free tier

### For Hostinger:
- Use Hostinger's MySQL database
- Connect via database credentials in hPanel

## SSL and Domain Setup

1. **Custom Domain**:
   - Add domain in Hostinger hPanel
   - Update DNS records
   - Enable SSL certificate

2. **CORS Configuration**:
   Update backend CORS settings to allow your domain:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-domain.com"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

## Deployment Checklist

- [ ] Build React app for production
- [ ] Upload frontend to Hostinger public_html
- [ ] Deploy backend to external service
- [ ] Configure environment variables
- [ ] Update API endpoints in frontend
- [ ] Set up database connection
- [ ] Configure CORS
- [ ] Test all functionality
- [ ] Set up custom domain and SSL

## Troubleshooting

### Common Issues:
1. **CORS Errors**: Check backend CORS configuration
2. **API Not Found**: Verify API URL in frontend
3. **Build Errors**: Check Node.js version compatibility
4. **Database Connection**: Verify connection strings

### Support Resources:
- Hostinger Knowledge Base
- Railway/Render documentation
- FastAPI deployment guides

## Cost Estimation

### Current Setup:
- Hostinger Cloud Startup: ~$2-4/month
- External Backend (Railway/Render): Free tier available
- Database: Free tier available

### Total Monthly Cost: $2-4 (with free backend hosting)

## Next Steps

1. Choose deployment strategy (Static + External Backend recommended)
2. Set up external backend hosting account
3. Configure environment variables
4. Deploy and test

Would you like me to help you implement any specific part of this deployment process?
