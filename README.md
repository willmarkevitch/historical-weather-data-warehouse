# Historical Weather Data Warehouse

A production-style batch data engineering pipeline that ingests historical weather data from the Open-Meteo Archive API, preserves immutable raw API responses, transforms and validates hourly observations, and loads them incrementally into PostgreSQL.

The project is designed around common data engineering concerns including reproducible ingestion, layered validation, idempotent database writes, incremental loading, schema migrations, and automated testing.

## Table of Contents

- [Architecture](#architecture)
- [Features](#features)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Database Model](#database-model)
- [Incremental Loading](#incremental-loading)
- [Getting Started](#getting-started)
- [Running the Pipeline](#running-the-pipeline)
- [Testing](#testing)
- [Design Decisions](#design-decisions)
- [Roadmap](#roadmap)

## Architecture

```text
                         Open-Meteo Archive API
                                  |
                                  v
                         Weather API Client
                                  |
                         Response Validation
                                  |
                                  v
                       Ingestion Record + Metadata
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
          Immutable Raw JSON           Transformation
                                                |
                                         Domain Validation
                                                |
                                                v
                                      WeatherObservation
                                                |
                                                v
                                    PostgreSQL Repository
                                                |
                                                v
                                  PostgreSQL Data Warehouse
                                      |               |
                                      v               v
                                  Locations     Weather Observations
                                      |
                                      v
                              High-Water-Mark Lookup
                                      |
                                      v
                                Incremental Loads
```

## Features

- Historical hourly weather ingestion from the Open-Meteo Archive API
- API input and response validation
- Immutable timestamped raw JSON snapshots
- Typed weather observation domain model
- Transformation and domain-level validation
- Dockerized PostgreSQL warehouse
- SQL schema migrations
- Logical location management
- Location-aware high-water marks
- Incremental date-range planning
- Idempotent database loading
- Database integrity constraints
- Command-line pipeline execution
- Unit and PostgreSQL integration tests

## Data Flow

A pipeline run begins with a logical location, requested coordinates, and a date range.

1. The pipeline resolves the logical location in PostgreSQL.
2. The latest stored observation for that location is retrieved as a high-water mark.
3. The requested range is reduced to only dates that may still require ingestion.
4. Historical hourly weather data is requested from Open-Meteo.
5. The API response is validated before further processing.
6. The original response and ingestion metadata are stored as an immutable JSON snapshot.
7. Hourly records are transformed into typed `WeatherObservation` objects.
8. Domain validation is applied before database loading.
9. Valid observations are inserted into PostgreSQL.
10. Duplicate observations are ignored using the logical `(location_id, observed_at)` identity.

If the requested range is already current, the pipeline exits without making another weather API request or creating another raw snapshot.

## Technology Stack

| Technology | Purpose |
| --- | --- |
| Python | ETL pipeline and application logic |
| PostgreSQL 17 | Data warehouse |
| Docker Compose | Local database infrastructure |
| Open-Meteo Archive API | Historical weather source |
| psycopg | PostgreSQL database access |
| requests | HTTP API client |
| pytest | Unit and integration testing |
| python-dotenv | Local environment configuration |

## Project Structure

```text
historical-weather-data-warehouse/
├── sql/
│   ├── 001_create_weather_observations.sql
│   ├── 002_add_locations.sql
│   └── 003_update_weather_observation_uniqueness.sql
│
├── src/
│   ├── ingestion/
│   │   ├── ingestion_record.py
│   │   ├── pipeline.py
│   │   └── weather_client.py
│   │
│   ├── models/
│   │   └── weather_observation.py
│   │
│   ├── pipeline/
│   │   ├── incremental.py
│   │   ├── incremental_weather_etl.py
│   │   ├── raw_filename.py
│   │   ├── run_weather_etl.py
│   │   └── weather_etl.py
│   │
│   ├── storage/
│   │   ├── database.py
│   │   ├── location_repository.py
│   │   ├── raw_storage.py
│   │   └── weather_repository.py
│   │
│   ├── transformation/
│   │   └── weather_transformer.py
│   │
│   └── validation/
│       └── weather_validation.py
│
├── tests/
│   ├── integration/
│   └── test_*.py
│
├── .env.example
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```

## Database Model

The warehouse currently contains two primary entities.

### `locations`

Stores logical locations requested by the pipeline.

Important fields include:

- `id`
- `name`
- `requested_latitude`
- `requested_longitude`
- `created_at`

### `weather_observations`

Stores hourly weather observations returned by the upstream API.

Current measurements include:

- Temperature
- Relative humidity
- Precipitation

Each observation also stores its timestamp, upstream coordinates, logical `location_id`, and creation timestamp.

Weather observations are uniquely identified by:

```text
(location_id, observed_at)
```

This separates the logical location requested by the pipeline from the grid coordinates returned by the weather provider.

## Incremental Loading

The pipeline uses the latest stored observation for each logical location as a high-water mark.

For example:

```text
Requested range:       2025-01-01 -> 2025-01-05
Warehouse current to:  2025-01-03 23:00 UTC

Incremental API range: 2025-01-04 -> 2025-01-05
```

Only the missing range is fetched and processed.

Running the same request again after the warehouse is current results in:

```text
No new weather data to load.
```

This avoids unnecessary API requests, raw files, transformations, and database writes.

## Getting Started

### Prerequisites

Install:

- Python 3
- Docker Desktop
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/willmarkevitch/historical-weather-data-warehouse.git
cd historical-weather-data-warehouse
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

On Windows Git Bash:

```bash
source venv/Scripts/activate
```

On Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

For development:

```bash
python -m pip install -r requirements-dev.txt
```

For runtime dependencies only:

```bash
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment configuration.

On Git Bash/macOS/Linux:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

The resulting `.env` file should contain:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=weather
POSTGRES_USER=weather_user
POSTGRES_PASSWORD=your_password_here
```

Replace `your_password_here` with a local PostgreSQL password of your choice.

The `.env` file is excluded from version control.

### 5. Start PostgreSQL

```bash
docker compose up -d
```

Verify that the container is running:

```bash
docker compose ps
```

On a fresh PostgreSQL volume, the SQL migration files mounted in `sql/` initialize the warehouse schema automatically.

To stop the PostgreSQL container without deleting the persisted database volume:

```bash
docker compose down
```

## Running the Pipeline

The ETL pipeline can be executed from the command line.

For example:

```bash
python -m src.pipeline.run_weather_etl \
  --location los_angeles \
  --latitude 34.0522 \
  --longitude -118.2437 \
  --start-date 2025-01-01 \
  --end-date 2025-01-05
```

The pipeline determines which portion of the requested range is missing from the warehouse before requesting data from Open-Meteo.

A successful incremental load reports the raw snapshot path and the number of transformed and inserted observations.

Example:

```text
Raw file: data/raw/los_angeles_2025-01-04_2025-01-05_<timestamp>.json
Transformed observations: 48
Inserted observations: 48
```

Running the same command after the requested range is current results in:

```text
No new weather data to load.
```

Raw API responses are written beneath `data/raw/` and are intentionally excluded from version control.

## Testing

Run the complete test suite:

```bash
python -m pytest -v
```

Run tests that do not require PostgreSQL:

```bash
python -m pytest -m "not integration" -v
```

Run only PostgreSQL integration tests:

```bash
python -m pytest -m integration -v
```

Integration tests require the Dockerized PostgreSQL service to be running.

The test suite covers:

- API request construction
- HTTP failures
- API response validation
- Raw storage behavior
- Transformation
- Domain validation
- PostgreSQL repositories
- Database constraints
- Location management
- Incremental range planning
- Incremental ETL orchestration
- CLI behavior
- Idempotent writes
- Location/time uniqueness

## Design Decisions

### Immutable Raw Storage

Every successful API extraction is preserved as a timestamped raw JSON snapshot before transformation.

This provides a reproducible record of the source data received during a pipeline run and separates source ingestion from downstream warehouse state.

### Layered Validation

Validation occurs at multiple boundaries:

- API request inputs
- API response structure
- Transformed domain objects
- PostgreSQL constraints

This prevents the database from being the only layer responsible for data quality and allows invalid data to fail closer to its source.

### Logical Locations

Requested locations are stored independently from coordinates returned by Open-Meteo.

This distinction is important because weather APIs may resolve requested coordinates to nearby grid points. Logical location identity therefore does not depend on the exact coordinates returned by the upstream provider.

### Idempotent Warehouse Writes

Observations use:

```text
(location_id, observed_at)
```

as their logical identity.

Repeated loads can therefore safely encounter observations that already exist without creating duplicate warehouse records.

Two observations with the same logical location and timestamp are treated as duplicates even if their upstream grid coordinates differ.

### Incremental Processing

The pipeline retrieves the latest stored observation for a location before extraction.

This high-water mark is used to calculate the portion of the requested date range that may still require ingestion.

As a result, repeated executions avoid unnecessary API requests and processing while remaining safe to rerun.

### Database Constraints

Application-level validation is complemented by PostgreSQL constraints.

The warehouse enforces requirements such as:

- Valid foreign-key relationships between observations and locations
- Unique location/timestamp combinations
- Relative humidity between 0% and 100%
- Non-negative precipitation

This provides an additional layer of protection if invalid data reaches the persistence layer.

## Roadmap

Planned improvements include:

- Apache Airflow orchestration and scheduling
- Retry and operational failure handling
- Additional weather measurements
- AWS deployment
- Cloud object storage for raw weather data
- Managed PostgreSQL deployment
- Streamlit analytics interface
- Automated CI testing with GitHub Actions
