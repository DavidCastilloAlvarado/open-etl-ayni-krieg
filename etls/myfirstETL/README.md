# myfirstETL

Daily ETL pipeline using pandas and scikit-learn, deployed to Vertex AI.

## Structure

```
myfirstETL/
├── src/                    # Python source code
│   ├── pipeline.py         # Main ETL logic
│   ├── transforms.py       # Data transformations
│   └── utils.py            # Helper functions
├── resources/              # Configuration files
│   └── config.yaml         # ETL configuration
├── tests/                  # Unit tests
│   └── test_pipeline.py
├── pyproject.toml          # Poetry dependencies
└── Dockerfile              # Container definition
```

## Local Development

### Install dependencies
```bash
poetry install
```

### Run ETL locally
```bash
poetry run poe run
```

### Run tests
```bash
poetry run poe test
```

### Lint code
```bash
poetry run poe ruff
```

## Configuration

Edit `resources/config.yaml` to configure:
- Schedule (cron expression)
- Compute resources (CPU, memory)
- Input/output paths
- GCP settings

## Deployment

Deploy via GitHub Actions:
1. Go to Actions tab
2. Select "Deploy ETL to Vertex AI"
3. Click "Run workflow"
4. Select `myfirstETL` and environment
5. Approve deployment (owner only)
