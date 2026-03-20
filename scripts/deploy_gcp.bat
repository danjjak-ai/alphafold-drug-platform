@echo off
set PROJECT_ID=alphafold-drug-platform
set REGION=asia-northeast1
set REQ_SERVICE=alphafold-dashboard
set REPOSITORY=raretarget

echo Setting active project...
call gcloud config set project %PROJECT_ID% --quiet

echo Enabling GCP APIs...
call gcloud services enable artifactregistry.googleapis.com run.googleapis.com cloudbuild.googleapis.com --project %PROJECT_ID% --quiet

rem Fetch project number safely (suppress background warnings)
echo Fetching project number...
for /f "tokens=*" %%a in ('gcloud projects list --filter^="projectId:%PROJECT_ID%" --format^="value(projectNumber)" 2^>nul') do set PROJECT_NUMBER=%%a
echo Project Number: %PROJECT_NUMBER%

rem Ensure required service account roles
echo Granting roles to Cloud Build and Compute service accounts...
call gcloud projects add-iam-policy-binding %PROJECT_ID% --member="serviceAccount:%PROJECT_NUMBER%@cloudbuild.gserviceaccount.com" --role="roles/cloudbuild.builds.builder" --quiet >nul 2>&1
call gcloud projects add-iam-policy-binding %PROJECT_ID% --member="serviceAccount:%PROJECT_NUMBER%@cloudbuild.gserviceaccount.com" --role="roles/artifactregistry.writer" --quiet >nul 2>&1
call gcloud projects add-iam-policy-binding %PROJECT_ID% --member="serviceAccount:%PROJECT_NUMBER%-compute@developer.gserviceaccount.com" --role="roles/artifactregistry.writer" --quiet >nul 2>&1
call gcloud projects add-iam-policy-binding %PROJECT_ID% --member="serviceAccount:%PROJECT_NUMBER%-compute@developer.gserviceaccount.com" --role="roles/storage.admin" --quiet >nul 2>&1
call gcloud projects add-iam-policy-binding %PROJECT_ID% --member="serviceAccount:%PROJECT_NUMBER%-compute@developer.gserviceaccount.com" --role="roles/logging.logWriter" --quiet >nul 2>&1

echo Checking Artifact Registry...
call gcloud artifacts repositories create %REPOSITORY% --repository-format=docker --location=%REGION% --description="RareTarget Discovery Docker repository" --project %PROJECT_ID% --quiet 2>nul || echo Repository already exists.

echo Building and pushing image to Artifact Registry...
call gcloud builds submit --tag "%REGION%-docker.pkg.dev/%PROJECT_ID%/%REPOSITORY%/%REQ_SERVICE%:latest" --project %PROJECT_ID%

echo Deploying to Cloud Run...
call gcloud run deploy %REQ_SERVICE% --image "%REGION%-docker.pkg.dev/%PROJECT_ID%/%REPOSITORY%/%REQ_SERVICE%:latest" --platform managed --region %REGION% --allow-unauthenticated --memory 2Gi --cpu 2 --project %PROJECT_ID%

echo Deployment complete!
pause
