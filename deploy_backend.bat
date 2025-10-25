@echo off
echo ========================================
echo Deploying Backend to Render
echo ========================================
echo.
echo This will:
echo 1. Add all changes
echo 2. Commit with CORS fix message
echo 3. Push to GitHub
echo 4. Render will auto-deploy
echo.
pause
echo.
echo Adding changes...
git add .
echo.
echo Committing...
git commit -m "Fix CORS configuration for production deployment"
echo.
echo Pushing to GitHub...
git push origin main
echo.
echo ========================================
echo Done! 
echo ========================================
echo.
echo Render will now automatically deploy your backend.
echo Check status at: https://dashboard.render.com
echo.
echo After deployment completes:
echo 1. Go to your frontend on Render
echo 2. Add environment variable: VITE_BASE_URL=https://my-shop-app-c1kx.onrender.com
echo 3. Save and wait for frontend to redeploy
echo.
pause
