# Migration Notice

The original `myfirstETL.py` file has been migrated to the new structure:

**Old location:**
```
myfirstETL.py
```

**New location:**
```
etls/myfirstETL/src/pipeline.py
```

## What Changed

1. **Organized structure**: Code moved to `src/` folder
2. **Configuration separated**: New `resources/config.yaml` file
3. **Poetry dependencies**: `pyproject.toml` for dependency management
4. **Containerized**: Added `Dockerfile` for deployment
5. **Tests added**: Unit tests in `tests/` folder
6. **Enhanced functionality**: Better config management and CLI support

## The old file can be safely deleted after verification:

```bash
rm myfirstETL.py
```

## To run the new version:

```bash
cd etls/myfirstETL
poetry install
poetry run poe run
```
