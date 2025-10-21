#!/bin/bash

#----------------------------------------------------------------------------------
# Script Name: setup_project.sh
# Description: creates the NYC_Train-Mobility-App project folder and file structure
# Author: Monica Dhieu
# Date:   2025-10-14
# Usage:  ./setup_project.sh
#-----------------------------------------------------------------------------------

#!/bin/bash

# ensure reliable error handling
set -euo pipefail

echo -e "Hello!\nWelcome to the NYC Trip Visualiser.\nSetting up project structure..."

# define folders to create
dirs=(
  ".github/workflows"
  "nginx/"
  "frontend/css"
  "frontend/js"
  "backend/app/database"
  "backend/app/routers"
  "backend/app/controllers"
  "backend/app/services"
  "data/raw"
  "data/processed"
  "examples"
  "docs"
  "tests"
)

# create folders
for dir in "${dirs[@]}"; do
  if [[ ! -d "$dir" ]]; then
    mkdir -p "$dir"
    echo "Created directory: $dir"
  else
    echo "Directory already exists: $dir"
  fi
done

# define files to create
files=(
  "CONTRIBUTING.md"
  "docker-compose.yml"
  ".dockerignore"
  ".gitignore"
  "index.html"
  "nginx/Dockerfile"
  "nginx/nginx.conf"
  "frontend/css/styles.css"
  "frontend/js/main.js"
  "data/raw/train.zip"
  "data/processed/clean_train.csv"
  "backend/Dockerfile"
  "backend/app/__init__.py"
  "backend/app/main.py"
  "backend/app/auth.py"
  "backend/app/data_processing.py"
  "backend/app/database/__init__.py"
  "backend/app/database/connection.py"
  "backend/app/database/models.py"
  "backend/app/database/manager.py"
  "backend/app/database/schema.sql"
  "backend/app/routers/__init__.py"
  "backend/app/routers/trip_routes.py"
  "backend/app/routers/auth_routes.py"
  "backend/app/routers/vendor_routes.py"
  "backend/app/controllers/__init__.py"
  "backend/app/controllers/trip_controller.py"
  "backend/app/controllers/vendor_controller.py"
  "backend/app/services/__init__.py"
  "backend/app/services/trip_service.py"
  "backend/app/services/utils.py"
  "backend/__init__.py"
  "backend/requirements.txt"
  "backend/.env"
  "backend/nyc_train.db"
  "backend/README.md"
  "docs/architecture_diagram.png"
  "docs/erd_diagram.png"
  "docs/api_docs.md"
  "docs/REPORT.pdf"
  "docs/README.md"
  "examples/trip_schema.json"
  "examples/sample_trip_data.json"
  "tests/test_trip_controller.py"
  "tests/test_vendor_controller.py"
  "tests/test_database.py"
  ".github/workflows/docker-build-push.yml"
)

# create files
for file in "${files[@]}"; do
  if [[ ! -f "$file" ]]; then
    touch "$file"
    echo "Created file: $file"
  else
    echo "File already exists: $file"
  fi
done

# define files to make executable
exec_files=(
  "backend/app/main.py"
  "backend/app/services/trip_service.py"
  "tests/test_trip_controller.py"
  "tests/test_database.py"
)

# make files executable
for file in "${exec_files[@]}"; do
  if [[ -f "$file" ]]; then
    chmod +x "$file"
    echo "Made executable: $file"
  fi
done

echo "Project structure setup complete! 🚀"
