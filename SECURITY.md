# Security Best Practices

This project follows security best practices to protect sensitive credentials and prevent accidental exposure.

## ✅ What We Do Right

### 1. **No Hardcoded Secrets or Configuration**
- **ALL** configuration values come from environment variables
- **No config folder** - completely removed from the project
- No project IDs, regions, buckets, or service accounts anywhere in code
- Environment (dev/prod) passed as command line argument
- Zero sensitive information in version control

### 2. **Workload Identity Federation**
- GitHub Actions uses Workload Identity Federation (WIF)
- No service account keys stored in GitHub
- Short-lived tokens instead of static credentials

### 3. **Environment Variable Injection**
```bash
# All configuration from environment
export GCP_PROJECT_ID="your-project"
export GCP_REGION="us-central1"
export GCP_SERVICE_ACCOUNT="sa@project.iam.gserviceaccount.com"
export GCP_BUCKET="your-bucket"
export CONTAINER_REGISTRY="gcr.io"
export CONTAINER_REGISTRY_PROJECT="your-project"
```

### 4. **Separate Environments**
- Dev and prod use different secrets
- No cross-environment pollution
- Environment-specific secrets in GitHub

## 🔐 Secrets Management

### GitHub Secrets (Required for CI/CD)
```
WIF_PROVIDER                    # Workload Identity Federation provider path
GCP_SA_EMAIL                    # Service account email for authentication
GCP_PROJECT_ID                  # GCP project ID
GCP_REGION                      # GCP region (e.g., us-central1)
GCP_BUCKET                      # GCS bucket for pipeline artifacts
CONTAINER_REGISTRY              # Container registry (e.g., gcr.io)
```

### Environment Variables (Local Development)
```bash
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"
export GCP_SERVICE_ACCOUNT="your-sa@project.iam.gserviceaccount.com"
export GCP_BUCKET="your-bucket-name"
export CONTAINER_REGISTRY="gcr.io"
export CONTAINER_REGISTRY_PROJECT="your-project-id"
```

### In GitHub Actions
```yaml
- name: Set Environment Variables from Secrets
  run: |
    echo "GCP_PROJECT_ID=${{ secrets.GCP_PROJECT_ID }}" >> $GITHUB_ENV
    echo "GCP_REGION=${{ secrets.GCP_REGION }}" >> $GITHUB_ENV
    echo "GCP_SERVICE_ACCOUNT=${{ secrets.GCP_SA_EMAIL }}" >> $GITHUB_ENV
    echo "GCP_BUCKET=${{ secrets.GCP_BUCKET }}" >> $GITHUB_ENV
    echo "CONTAINER_REGISTRY=${{ secrets.CONTAINER_REGISTRY }}" >> $GITHUB_ENV
    echo "CONTAINER_REGISTRY_PROJECT=${{ secrets.GCP_PROJECT_ID }}" >> $GITHUB_ENV
```

## 🛡️ What NOT to Do

### ❌ Never Commit
- Service account keys (`.json` files)
- Project IDs, regions, or bucket names
- Any GCP-specific values
- API keys or tokens
- `.env` files with real values

### ❌ Never Hardcode
```yaml
# BAD - Don't do this anywhere!
gcp:
  project_id: "my-project-123"
```

### ✅ Instead, Do This
```bash
# GOOD - Use environment variables
export GCP_PROJECT_ID="my-project-123"
```

## 🔍 Checking for Secrets

### Before Committing
```bash
# Check for potential secrets or hardcoded config anywhere
find . -name "*.yaml" -o -name "*.yml" -o -name "*.py" | xargs grep -i "project.*id\|region\|bucket" | grep -v "environment variable"

# Should only find variable names and comments
```

### Git Hooks (Recommended)
```bash
# Install pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
if git diff --cached | grep -i "iam.gserviceaccount.com\|service_account.*@"; then
  echo "Error: Potential service account email found!"
  echo "Use environment variables instead of hardcoding secrets."
  exit 1
fi
EOF
chmod +x .git/hooks/pre-commit
```

## 📋 Security Checklist

Before deploying:

- [ ] No service account keys in repository
- [ ] No hardcoded service accounts in configs
- [ ] GitHub Secrets configured (WIF_PROVIDER, GCP_SA_EMAIL)
- [ ] Environment variables documented in README
- [ ] Workload Identity Federation set up
- [ ] Separate dev/prod environments configured
- [ ] `.gitignore` includes `*.json` and `credentials/`

## 🔄 Rotation Policy

### Service Account Rotation
1. Create new service account
2. Update WIF bindings
3. Update GitHub Secret (`GCP_SA_EMAIL`)
4. Test deployment in dev
5. Update prod
6. Disable old service account
7. Delete after grace period

### WIF Provider Rotation
1. Create new WIF pool/provider
2. Update GitHub Secret (`WIF_PROVIDER`)
3. Test in dev environment
4. Update prod
5. Delete old pool after verification

## 📚 Additional Resources

- [Workload Identity Federation Guide](https://cloud.google.com/iam/docs/workload-identity-federation)
- [GitHub Actions Security](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Google Cloud Security Best Practices](https://cloud.google.com/security/best-practices)

## 🚨 If Secrets Are Exposed

1. **Immediately revoke** the service account
2. **Rotate all credentials**
3. **Review git history** for exposed secrets
4. **Consider using `git-filter-repo`** to remove from history
5. **Update all dependent systems**
6. **Document the incident**

---

**Remember: Security is everyone's responsibility!** 🔐
