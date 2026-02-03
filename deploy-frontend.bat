@echo off
echo Starting frontend deployment build process...
echo.

cd frontend

echo Step 1: Cleaning node_modules and package-lock.json...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json
if exist yarn.lock del yarn.lock

echo Step 2: Installing dependencies with legacy peer deps...
npm install --legacy-peer-deps

echo Step 3: Building for production...
npm run build

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Build successful!
    echo.
    echo Next steps:
    echo 1. Upload contents of 'frontend/build' folder to your Hostinger public_html directory
    echo 2. Make sure index.html is in the root of public_html
    echo 3. Configure your backend API URL in the environment
    echo.
    echo Build files are located in: frontend/build/
) else (
    echo.
    echo ❌ Build failed. Check the error messages above.
    echo.
    echo Troubleshooting tips:
    echo 1. Make sure you're using Node.js version 18 or higher
    echo 2. Try running: npm cache clean --force
    echo 3. Delete node_modules and try again
)

pause
