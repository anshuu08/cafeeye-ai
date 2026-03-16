#!/bin/bash
# CafeEye AI - Automated Google Cloud Deployment
gcloud config set project coastal-haven-467307-t4
gcloud services enable run.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com
gcloud run deploy cafeeye-ai \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501 \
  --memory 2Gi \
  --cpu 2
echo "CafeEye AI deployed to Google Cloud Run!"