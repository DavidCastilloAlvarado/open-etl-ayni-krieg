# Dockerfile Best Practices Applied

## Changes Made

### 1. Multi-Stage Build
- **Stage 1 (builder)**: Installs Poetry, exports dependencies to requirements.txt
- **Stage 2 (production)**: Clean Python image, installs from requirements.txt
- **Benefit**: ~50-100MB smaller final image, Poetry not in production

### 2. Non-Root User
- Creates `etluser` (UID 1000)
- Runs container as non-root
- **Benefit**: Security best practice, prevents privilege escalation

### 3. Optimized Layer Caching
- Dependencies installed before code copy
- Changes to code don't rebuild dependencies
- **Benefit**: Faster rebuilds during development

### 4. Clean Dependencies
- No dev dependencies in final image
- No Poetry installation overhead
- **Benefit**: Smaller attack surface, faster startup

## Image Size Comparison

| Version | Approximate Size |
|---------|-----------------|
| Previous (with Poetry) | ~450-500MB |
| Optimized (multi-stage) | ~350-400MB |

## Security Improvements

✅ Non-root user (UID 1000)  
✅ Minimal base image (python:3.11-slim)  
✅ No unnecessary tools in final image  
✅ Proper file ownership

## Build & Test

```bash
# Build
docker build -t myfirstetl:latest .

# Test as non-root
docker run --rm myfirstetl:latest --help

# Verify non-root user
docker run --rm myfirstetl:latest id
# Should show: uid=1000(etluser)
```

## For New ETLs

Copy this Dockerfile pattern to any new ETL folder. Just update the LABEL metadata.
