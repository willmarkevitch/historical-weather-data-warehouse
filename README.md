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

The same incremental ETL pipeline can be invoked from the command line or through Apache Airflow. Airflow orchestrates two independent city tasks; the ingestion, transformation, and persistence logic remains in the shared Python application.

```text
CLI -------------------+          Apache Airflow (manual DAG)
                       |            |                 |
                       |       San Francisco      Los Angeles
                       |            |                 |
                       +------------+-----------------+
                                    |
                          Incremental ETL Pipeline
                                    |
                         Resolve Logical Location
                                    |
                       PostgreSQL High-Water Mark
                                    |
                        Plan Missing Date Range
                                    |
                         Open-Meteo Archive API
                                    |
                           Response Validation
                                    |
                        Ingestion Record / Metadata
                                    |
                     +--------------+--------------+
                     |                             |
              Immutable Raw JSON             Transformation
                                                   |
                                            Domain Validation
                                                   |
                                           WeatherObservation
                                                   |
                                          PostgreSQL Repository
                                                   |
                                         PostgreSQL Data Warehouse
                                          (locations, observations)
```

If the requested date range is already current for a location, the ETL exits before requesting data from Open-Meteo or creating a raw snapshot.

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

- Apache Airflow orchestration with independent city tasks
- Automated pipeline and DAG validation with GitHub Actions

## Data Flow

A pipeline run begins with a logical location, requested coordinates, and a date range.

1\. The pipeline resolves the logical location in PostgreSQL.

2\. The latest stored observation for that location is retrieved as a high-water mark.

3\. The requested range is reduced to only dates that may still require ingestion.

4\. Historical hourly weather data is requested from Open-Meteo.

5\. The API response is validated before further processing.

6\. The original response and ingestion metadata are stored as an immutable JSON snapshot.

7\. Hourly records are transformed into typed `WeatherObservation` objects.

8\. Domain validation is applied before database loading.

9\. Valid observations are inserted into PostgreSQL.

10\. Duplicate observations are ignored using the logical `(location_id, observed_at)` identity.

If the requested range is already current, the pipeline exits without making another weather API request or creating another raw snapshot.

## Technology Stack

\| Technology | Purpose |

\| --- | --- |

\| Python | ETL pipeline and application logic |

\| PostgreSQL 17 | Data warehouse |

\| Docker Compose | Local PostgreSQL and Airflow infrastructure |
| Apache Airflow 3.3.2 | Manual DAG orchestration and task logs |

\| Open-Meteo Archive API | Historical weather source |

\| psycopg | PostgreSQL database access |

\| requests | HTTP API client |

\| pytest | Unit and integration testing |

\| python-dotenv | Local environment configuration |

## Project Structure

```text

historical-weather-data-warehouse/

├── airflow/
│   ├── Dockerfile
│   └── dags/
│       └── historical_weather.py
│
├── sql/

│   ├── 001_create_weather_observations.sql

│   ├── 002_add_locations.sql

│   └── 003_update_weather_observation_uniqueness.sql

│

├── src/

│   ├── ingestion/

│   │   ├── ingestion_record.py

│   │   ├── pipeline.py

│   │   └── weather_client.py

│   │

│   ├── models/

│   │   └── weather_observation.py

│   │

│   ├── pipeline/

│   │   ├── incremental.py

│   │   ├── incremental_weather_etl.py

│   │   ├── raw_filename.py

│   │   ├── run_weather_etl.py

│   │   └── weather_etl.py

│   │

│   ├── storage/

│   │   ├── database.py

│   │   ├── location_repository.py

│   │   ├── raw_storage.py

│   │   └── weather_repository.py

│   │

│   ├── transformation/

│   │   └── weather_transformer.py

│   │

│   └── validation/

│       └── weather_validation.py

│

├── tests/

│   ├── integration/

│   └── test_\*.py

│

├── .github/
│   └── workflows/
│       └── tests.yml
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

Requested range:       2025-01-01 -> 2025-01-05

Warehouse current to:  2025-01-03 23:00 UTC

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
AIRFLOW_JWT_SECRET=your_generated_secret_here

```

Replace `your_password_here` with a local PostgreSQL password of your choice. Generate `AIRFLOW_JWT_SECRET` as described in [Apache Airflow Orchestration](#apache-airflow-orchestration).

The `.env` file is excluded from version control.

### 5. Start the Docker Services

```bash

docker compose up -d --build

```

Verify that the containers are running:

```bash

docker compose ps

```

On a fresh PostgreSQL volume, the SQL migration files mounted in `sql/` initialize the warehouse schema automatically.

To stop the services without deleting persisted volumes:

```bash

docker compose down

```

## Running the Pipeline

The ETL pipeline can be executed from the command line.

For example:

```bash

python -m src.pipeline.run_weather_etl \\

  --location los_angeles \\

  --latitude 34.0522 \\

  --longitude -118.2437 \\

  --start-date 2025-01-01 \\

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

## Apache Airflow Orchestration

The `historical_weather` DAG is defined in `airflow/dags/historical_weather.py` and runs using Apache Airflow 3.3.2. It contains two independent `PythonOperator` tasks:

| Task ID | Location | Coordinates |
| --- | --- | --- |
| `load_san_francisco` | San Francisco | 37.7749, -122.4194 |
| `load_los_angeles` | Los Angeles | 34.0522, -118.2437 |

Each task calls `run_incremental_weather_etl()` with its own location, coordinates, and requested date range. Both currently use **January 1–5, 2025** as a reproducible example. The DAG has `schedule=None` and `catchup=False`: it runs **only when manually triggered**, and it does not automatically schedule future loads.

### Start Airflow locally

After cloning the repository and configuring `.env` as described in [Getting Started](#getting-started), create a shared JWT secret for local Airflow services:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the generated value into `.env` as `AIRFLOW_JWT_SECRET=...`. Do not commit the secret or share it in logs. The same secret must be available to the Airflow API server, scheduler, and DAG processor.

Start the services:

```bash
docker compose up -d --build
```

Check container status:

```bash
docker compose ps
```

Open **http://localhost:8080**. The local development environment uses Airflow's simple authentication manager. Retrieve the generated admin password from the API server's startup logs (do not commit or publish it):

```bash
docker compose logs airflow-api-server
```

Sign in as `admin`, open the `historical_weather` DAG, and select **Trigger** to run it manually. Inspect each task's status and logs in the Airflow UI. Subsequent runs over an already-current date range should report that there is no new weather data to load.

Airflow uses its own PostgreSQL metadata database, separate from the weather warehouse. Application code, DAG files, and raw weather storage are mounted into the containers; task logs are stored in the shared `airflow_logs` Docker volume.

To stop the stack while preserving database and log volumes:

```bash
docker compose down
```

**Do not use `docker compose down -v` unless you intend to delete persisted database and Airflow volume data.**

### Current limitations

- The DAG is manual and uses fixed historical dates rather than a dynamic schedule.
- Location names are not yet canonicalized: `San Francisco` and `san_francisco`, for example, can create distinct logical location records.
- High-water-mark planning handles trailing missing data, but does not yet detect earlier or interior gaps in an otherwise populated date range.
- Automated retry policies, alerting, and production authentication/deployment are future improvements.

## Testing

The standard Python environment does not require Apache Airflow. Run the non-integration tests with the Airflow-only module excluded:

```bash
python -m pytest -m "not integration" --ignore=tests/test_airflow_dag.py -v
```

Run PostgreSQL integration tests while the database service is available:

```bash
python -m pytest -m integration --ignore=tests/test_airflow_dag.py -v
```

Run the four Airflow DAG tests inside the Airflow scheduler container:

```bash
docker exec airflow-scheduler python -m pytest -v /opt/airflow/project/tests/test_airflow_dag.py
```

On **Windows Git Bash**, prevent MSYS from rewriting the Linux container path:

```bash
MSYS_NO_PATHCONV=1 docker exec airflow-scheduler \
  python -m pytest -v /opt/airflow/project/tests/test_airflow_dag.py
```

The DAG tests validate parsing/imports, task IDs, manual scheduling, and city parameters without running ingestion or requiring a metadata database. The existing pipeline tests cover API requests and failures, response and domain validation, raw storage, transformations, PostgreSQL repositories and constraints, location management, incremental planning, CLI behavior, and idempotent writes.

GitHub Actions runs two separate jobs on pull requests: `unit-tests` for the standard non-integration Python suite and `Airflow DAG Tests` for the DAG tests using the project's custom Docker image. At the Airflow orchestration milestone, **101 standard tests and four DAG tests passed**; six PostgreSQL integration tests were excluded from the standard CI job.

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

- Scheduled Airflow execution with dynamic date ranges

- Retry policies, backoff, and operational failure handling
- Canonical location naming and safe duplicate-location consolidation
- Historical gap detection and backfills

- Additional weather measurements

- AWS deployment

- Cloud object storage for raw weather data

- Managed PostgreSQL deployment

- Streamlit analytics interface
