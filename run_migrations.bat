@echo off
echo ========================================
echo Running Django Migrations
echo ========================================
echo.

echo Step 1: Making migrations...
python manage.py makemigrations

echo.
echo Step 2: Applying migrations...
python manage.py migrate

echo.
echo ========================================
echo Migrations completed!
echo ========================================
echo.
echo Next steps:
echo 1. Create superuser: python manage.py createsuperuser
echo 2. Run server: python manage.py runserver
echo.
pause
