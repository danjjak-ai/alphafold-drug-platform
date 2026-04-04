#!/bin/bash
PROJECT_ID="alphafold-dashboard"
REGION="asia-northeast1"
REQ_SERVICE="alphafold-dashboard"
REPOSITORY="raretarget"

# 0. Setup Project
echo "Setting active project..."
gcloud config set project $PROJECT_ID --quiet

# 1. Enable APIs
echo "Enabling GCP APIs..."
gcloud services enable artifactregistry.googleapis.com run.googleapis.com cloudbuild.googleapis.com --project $PROJECT_ID --quiet

# 2. Get Project Number
PROJECT_NUMBER=$(gcloud projects list --filter="projectId:$PROJECT_ID" --format="value(projectNumber)" 2>/dev/null)
echo "Project Number: $PROJECT_NUMBER"

# 3. Ensure Service Account Roles
echo "Granting roles to Cloud Build and Compute service accounts..."
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" --role="roles/cloudbuild.builds.builder" --quiet >/dev/null 2>&1
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" --role="roles/storage.admin" --quiet >/dev/null 2>&1

# 4. Create Artifact Registry if not exists
echo "Checking Artifact Registry..."
gcloud artifacts repositories create $REPOSITORY --repository-format=docker --location=$REGION --description="RareTarget Discovery Docker repository" --project $PROJECT_ID --quiet 2>/dev/null || echo "Repository already exists."

# 5. Build and push image using Cloud Build
echo "Building and pushing image to Artifact Registry..."
gcloud builds submit --tag "$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$REQ_SERVICE:latest" --project $PROJECT_ID

# 6. Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $REQ_SERVICE --image "$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$REQ_SERVICE:latest" --platform managed --region $REGION --allow-unauthenticated --memory 2Gi --cpu 2 --project $PROJECT_ID

echo "Deployment complete!"
