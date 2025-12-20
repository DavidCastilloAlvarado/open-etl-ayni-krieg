# GitHub Environment Setup

To enable manual deployment approvals (only repository owner can deploy), configure GitHub Environments:

## Steps

1. Go to your GitHub repository
2. Click **Settings** → **Environments**
3. Click **New environment**
4. Name: `production`
5. Under **Environment protection rules**, check:
   - ✅ **Required reviewers**
   - Add repository owner as required reviewer
6. Click **Save protection rules**

## For Development Environment (Optional)

1. Create another environment named `dev`
2. No protection rules needed (auto-deploy)
3. Or add different reviewers for dev deployments

## Secrets Configuration

Add these secrets in **Settings** → **Secrets and variables** → **Actions**:

```
WIF_PROVIDER          # Format: projects/PROJECT_NUM/locations/global/workloadIdentityPools/POOL/providers/PROVIDER
GCP_SA_EMAIL          # Format: service-account@project.iam.gserviceaccount.com
```

## Testing the Workflow

1. Go to **Actions** tab
2. Select "Deploy ETL to Vertex AI"
3. Click "Run workflow"
4. Select ETL and environment
5. Owner will receive approval request
6. After approval, deployment proceeds
