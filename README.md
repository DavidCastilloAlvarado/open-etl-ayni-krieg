# ETL Deployment Platform for Vertex AI

Production-ready platform for deploying ETL pipelines to Google Cloud Vertex AI using Kubeflow, similar to Databricks Asset Bundles.

## 🏗️ Architecture

```
ETL Code (Python + Poetry) 
    ↓
Docker Container
    ↓
Kubeflow Pipeline (Auto-generated from config)
    ↓
Vertex AI Pipelines (Managed)
    ↓
Scheduled Execution (Cloud Scheduler)
```

**Key Feature:** Pipelines are automatically generated from each ETL's `resources/config.yaml` - no per-ETL pipeline code needed!

## 📁 Project Structure

```
myetlsopensource/
├── .github/workflows/        # CI/CD pipelines
│   ├── pr-checks.yml        # Ruff linting on PRs
│   └── deploy-etl.yml       # Manual deployment
├── etls/                    # ETL projects
│   └── myfirstETL/         # Example ETL
│       ├── src/            # Python source code
│       ├── resources/      # Configuration files
│       ├── tests/          # Unit tests
│       ├── pyproject.toml  # Poetry dependencies + Ruff
│       └── Dockerfile      # Container definition
├── kubeflow/               # Kubeflow pipeline definitions
│   └── pipelines/
│       └── base_pipeline.py    # Generic pipeline (reads ETL configs)
├── scripts/                # Deployment scripts
├── .env.template           # Environment variables template
└── pyproject.toml         # Root project
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Poetry
- Docker
- Google Cloud account with Vertex AI enabled
- GitHub repository

### 1. Install Dependencies

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install root dependencies
poetry install

# Install ETL dependencies
cd etls/myfirstETL
poetry install
cd ../..
```

### 2. Configure Environment Variables

All configuration is loaded from environment variables (no hardcoded values).

**For local development**, set these environment variables:

```bash
# Required for deployment
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"
export GCP_SERVICE_ACCOUNT="vertex-ai-sa@your-project.iam.gserviceaccount.com"
export GCP_BUCKET="your-pipeline-bucket"
export CONTAINER_REGISTRY="gcr.io"
export CONTAINER_REGISTRY_PROJECT="your-project-id"
```

**Optional**: Create a `.env` file (add to `.gitignore`):
```bash
# .env (never commit this!)
export GCP_PROJECT_ID="your-project"
export GCP_REGION="us-central1"
export GCP_SERVICE_ACCOUNT="sa@project.iam.gserviceaccount.com"
export GCP_BUCKET="bucket-name"
export CONTAINER_REGISTRY="gcr.io"
export CONTAINER_REGISTRY_PROJECT="your-project"
```

Then source it: `source .env`

### 3. Run ETL Locally

```bash
cd etls/myfirstETL
poetry run poe run
```

### 4. Test & Lint

```bash
# Test
poetry run poe test

# Lint
poetry run poe ruff
```

## 📦 Creating a New ETL

### 1. Create ETL Structure

```bash
mkdir -p etls/mynewtl/{src,resources,tests}
cd etls/mynewtl
```

### 2. Create `pyproject.toml`

```toml
[tool.poetry]
name = "mynewtl"
version = "0.1.0"
description = "My new ETL"
authors = ["Your Name <your.email@example.com>"]
package-mode = false

[tool.poetry.dependencies]
python = "^3.11"
pandas = "^2.2.0"
# Add your dependencies here

[tool.poetry.group.dev.dependencies]
ruff = "^0.8.4"
poethepoet = "^0.29.0"
pytest = "^8.3.0"

[tool.poe.tasks]
ruff.shell = "ruff check src/ tests/ --fix && ruff format src/ tests/"
run = "python src/pipeline.py"
test = "pytest tests/"

# ... Ruff configuration (copy from myfirstETL)
```

### 3. Create `resources/config.yaml`

```yaml
name: mynewtl
description: "Description of your ETL"
schedule: "0 8 * * *"  # Daily at 8am UTC

compute:
  cpu: "4"
  memory: "16Gi"
  timeout: "3600"

parameters:
  input_path: "gs://bucket/input"
  output_path: "gs://bucket/output"

# GCP settings (project, region, service_account) are 
# loaded from environment variables - never hardcode them here
```

### 4. Create `src/pipeline.py`

```python
from pathlib import Path
import yaml

def load_config():
    config_path = Path(__file__).parent.parent / "resources" / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)

def run_etl(input_path: str = None, output_path: str = None):
    config = load_config()
    input_path = input_path or config["parameters"]["input_path"]
    output_path = output_path or config["parameters"]["output_path"]
    
    # Your ETL logic here
    print(f"Running ETL: {config['name']}")
    
if __name__ == "__main__":
    run_etl()
```

### 5. Create `Dockerfile`

```dockerfile
FROM python:3.11-slim
RUN pip install --no-cache-dir poetry==1.8.0
WORKDIR /app
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi
COPY src/ ./src/
COPY resources/ ./resources/
ENV PYTHONPATH=/app/src:$PYTHONPATH
ENTRYPOINT ["python", "src/pipeline.py"]
```

### 6. Create Kubeflow Pipeline (Optional)

**No action needed!** The base pipeline automatically reads your ETL's `resources/config.yaml` and creates the pipeline dynamically. No per-ETL pipeline files required.

### 7. Update GitHub Actions

Add your new ETL to `.github/workflows/deploy-etl.yml`:

```yaml
etl_name:
  options:
    - myfirstETL
    - mynewtl  # Add here
```

## 🔧 Local Development

### List All ETLs

```bash
poetry run poe list-etls
```

### Build Docker Image

```bash
python scripts/build.py --etl-name myfirstETL --environment dev
```

### Build and Push

```bash
python scripts/build.py --etl-name myfirstETL --environment dev --push
```

### Deploy to Vertex AI (Local)

```bash
# Set all required environment variables (see step 2)
source .env  # or export them manually

# Deploy
python scripts/deploy.py --etl-name myfirstETL --environment dev
```

## 🚢 Deployment via GitHub Actions

### Manual Deployment (Production)

1. Go to **Actions** tab in GitHub
2. Select **"Deploy ETL to Vertex AI"**
3. Click **"Run workflow"**
4. Select:
   - ETL name (e.g., `myfirstETL`)
   - Environment (`dev` or `prod`)
   - Tag (default: `latest`)
5. Click **"Run workflow"**
6. **Owner approval required** (Environment protection rule)
7. Workflow will:
   - Build Docker image
   - Push to Google Container Registry
   - Deploy to Vertex AI
   - Create schedule (daily at 8am)

### PR Checks (Automatic)

On every Pull Request:
- ✅ Ruff linting on all code
- ✅ Configuration validation
- ✅ Unit tests
- ✅ All ETLs checked independently

## 🔐 GitHub Secrets Setup

Required secrets in GitHub repository settings (**Settings** → **Secrets and variables** → **Actions**):

```
WIF_PROVIDER                    # Workload Identity Federation provider
GCP_SA_EMAIL                    # GCP Service Account email
GCP_PROJECT_ID                  # Your GCP project ID
GCP_REGION                      # GCP region (e.g., us-central1)
GCP_BUCKET                      # GCS bucket for pipeline artifacts
CONTAINER_REGISTRY              # Container registry (default: gcr.io)
```

### Important Security Notes

✅ **ALL configuration is in secrets** - no hardcoded values in code  
✅ **Config files only contain environment markers** (dev/prod)  
✅ **Workload Identity Federation** is used instead of service account keys  
✅ **Secrets are managed in GitHub** and injected at runtime  
✅ **Zero sensitive data in version control**

### Setting up Workload Identity Federation

```bash
# Create service account
gcloud iam service-accounts create vertex-ai-deployer \
    --display-name="Vertex AI Deployer"

# Grant permissions
gcloud projects add-iam-policy-binding YOUR-PROJECT \
    --member="serviceAccount:vertex-ai-deployer@YOUR-PROJECT.iam.gserviceaccount.com" \
    --role="roles/aiplatform.admin"

gcloud projects add-iam-policy-binding YOUR-PROJECT \
    --member="serviceAccount:vertex-ai-deployer@YOUR-PROJECT.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Create Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
    --location="global" \
    --display-name="GitHub Actions Pool"

# Create provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository"

# Allow GitHub to impersonate service account
gcloud iam service-accounts add-iam-policy-binding \
    vertex-ai-deployer@YOUR-PROJECT.iam.gserviceaccount.com \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/PROJECT-NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/YOUR-GITHUB-USER/myetlsopensource"
```

## 📊 Monitoring

### View Pipeline Runs

1. Go to [Vertex AI Pipelines Console](https://console.cloud.google.com/vertex-ai/pipelines)
2. Select your project
3. View pipeline runs, logs, and metrics

### View Schedules

```bash
gcloud ai schedules list --location=us-central1
```

## 🧪 Testing

### Run All Tests

```bash
# Root project
poetry run poe test

# Specific ETL
cd etls/myfirstETL
poetry run poe test
```

### Run Linting

```bash
# Root project
poetry run poe ruff

# Specific ETL
cd etls/myfirstETL
poetry run poe ruff
```

## 📝 ETL Configuration Reference

### `resources/config.yaml`

```yaml
name: string                    # ETL name (required)
description: string             # Description (optional)
schedule: string               # Cron expression (required)

compute:                       # Compute resources (required)
  cpu: string                  # e.g., "4"
  memory: string               # e.g., "16Gi"
  timeout: integer             # Seconds (optional)

parameters:                    # Runtime parameters (required)
  input_path: string           # Input data path
  output_path: string          # Output data path
  # Add custom parameters here

# All GCP configuration (project_id, region, service_account, bucket)
# is loaded from environment variables for security
# NEVER hardcode these values in config files
```

## 🎯 Best Practices

### Code Organization

- Keep ETL logic in `src/`
- Keep configurations in `resources/`
- Write tests in `tests/`
- Use type hints
- Document functions with docstrings

### Configuration

- **ALL configuration comes from environment variables** - nothing hardcoded
- No config files needed - environment is passed as command argument
- Set environment variables before running any deployment commands
- Use `.env` file locally (but never commit it!)
- Use GitHub Secrets for CI/CD

### Dependencies

- Lock dependencies with `poetry.lock`
- Keep dependencies minimal
- Separate dev dependencies

### Testing

- Write unit tests for all functions
- Test with sample data
- Mock external services

### Deployment

- Always test in `dev` before `prod`
- Use semantic versioning for tags
- Review logs after deployment
- Monitor pipeline execution

## 🐛 Troubleshooting

### Build Fails

```bash
# Check Docker
docker --version

# Check Poetry
poetry --version

# Rebuild without cache
docker build --no-cache -t test .
```

### Deployment Fails

```bash
# Check GCP authentication
gcloud auth list

# Check Vertex AI API
gcloud services list --enabled | grep aiplatform

# Check service account permissions
gcloud projects get-iam-policy YOUR-PROJECT
```

### ETL Fails in Vertex AI

1. Check logs in Vertex AI console
2. Verify GCS paths are correct
3. Check service account permissions
4. Verify Docker image exists in registry

## 📚 Additional Resources

- [Vertex AI Pipelines Documentation](https://cloud.google.com/vertex-ai/docs/pipelines)
- [Kubeflow Pipelines Documentation](https://www.kubeflow.org/docs/components/pipelines/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)

## 📄 License

MIT

## 👥 Contributing

1. Create a new branch
2. Make your changes
3. Run tests and linting
4. Create a Pull Request
5. Wait for PR checks to pass
6. Get approval and merge

---

**Built with ❤️ for Data Engineers**
