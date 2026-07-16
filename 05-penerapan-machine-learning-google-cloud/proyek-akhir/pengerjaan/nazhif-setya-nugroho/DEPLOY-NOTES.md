# Asclepius — MLGC Final Project: Deploy Notes

Minimal-pass build. Backend = Hapi (pure `@tensorflow/tfjs` + `sharp`, no native build).
Deploy target = **Cloud Run** (auto-satisfies criteria 3 backend deploy + 7 static IP).

## Fixed identifiers
- Project ID: `submissionmlgc-nazhifsetya`
- Region: `asia-southeast2` (Jakarta)  — change if preferred
- Bucket (model): `submissionmlgc-nazhifsetya-model`
- Firestore: `(default)` database, Native mode, collection `predictions`
- Reviewer: `reviewer_googlecloud@dicoding.com`

## Status
- [x] Phase 0–2 DONE + verified locally. All 4 mandatory Postman scenarios pass over HTTP:
      cancer-1→201/Cancer, non-cancer-1→201/Non-cancer, more-than-1mb→413, bad-request→400.
- [ ] Phase 3 GCP setup (needs `gcloud auth login` + billing) — BLOCKED on user auth
- [ ] Phase 4 Cloud Storage + Firestore
- [ ] Phase 5 Cloud Run deploy
- [ ] Phase 6 App Engine frontend
- [ ] Phase 7 grant reviewer, Postman run, requirements.json, ZIP

## Layout
- `asclepius-backend/` — Hapi API (Dockerfile ready)
- `asclepius-frontend/` — Dicoding static frontend (edit only `src/scripts/api.js` BASE_URL)
- `model/` — TF.js graph-model (upload to the bucket)
- `data-test/` — reviewer test images
- `Asclepius.postman_collection.json` — reviewer test collection

## Remaining commands (run after `gcloud auth login`)

```bash
PROJECT=submissionmlgc-nazhifsetya
REGION=asia-southeast2
BUCKET=$PROJECT-model

# 3) Project + billing + APIs
gcloud config set account nazhif.nugroho@gmail.com
gcloud projects create $PROJECT
gcloud billing projects link $PROJECT --billing-account=<BILLING_ACCOUNT_ID>
gcloud config set project $PROJECT
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  cloudbuild.googleapis.com storage.googleapis.com firestore.googleapis.com \
  appengine.googleapis.com

# 4a) Cloud Storage — upload model, make objects public-read (model isn't secret)
gcloud storage buckets create gs://$BUCKET --location=$REGION --uniform-bucket-level-access
gcloud storage cp -r model/* gs://$BUCKET/model/
gcloud storage buckets add-iam-policy-binding gs://$BUCKET \
  --member=allUsers --role=roles/storage.objectViewer
# MODEL_URL = https://storage.googleapis.com/$BUCKET/model/model.json

# 4b) Firestore (default) native mode
gcloud firestore databases create --location=$REGION --type=firestore-native

# 5) Cloud Run deploy (from asclepius-backend/)
cd asclepius-backend
gcloud run deploy asclepius-backend \
  --source . --region=$REGION --allow-unauthenticated \
  --memory=1Gi --cpu=1 --timeout=120 \
  --set-env-vars=MODEL_URL=https://storage.googleapis.com/$BUCKET/model/model.json,FIRESTORE_ENABLED=true
cd ..

# 6) Frontend -> App Engine (set BASE_URL in src/scripts/api.js to the Cloud Run URL first)
gcloud app create --region=asia-southeast2   # App Engine region name (one-time)
cd asclepius-frontend && gcloud app deploy && cd ..

# 7) Grant reviewer (Viewer is simplest; least-privilege is the optional saran)
gcloud projects add-iam-policy-binding $PROJECT \
  --member=user:reviewer_googlecloud@dicoding.com --role=roles/viewer
```
