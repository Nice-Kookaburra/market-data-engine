# Market Data Engine Plan

## Goal

Produce clean, reliable historical market data that every later project can trust.

The Market Data Engine should grow around a clear data pipeline: fetch raw market data, normalize it into domain models, validate it, persist it, and expose clean time-series data for later modules.

## What The Project Should Do

- Fetch historical price data for stocks, ETFs, and indexes from one or more providers.
- Support user-selected symbols, index constituents, date ranges, and intervals such as daily, weekly, and monthly.
- Normalize raw provider data into consistent internal models such as `PriceBar`, `Asset`, `DataSource`, `CorporateAction`, and `TimeSeries`.
- Adjust prices for splits and dividends so later calculations use comparable historical values.
- Validate market data before storage, including non-negative prices, `high >= low`, required fields, duplicate rows, and missing dates.
- Store clean time-series data in a database with repeatable imports and safe re-runs.
- Retrieve clean prices by asset, date range, and interval for downstream modules.
- Compute simple returns, log returns, rolling averages, rolling volatility, and basic data quality summaries.
- Provide basic visualizations for prices, returns, rolling averages, and volatility.

## Expected Output

- A reliable historical dataset for all later projects.
- A repeatable ingestion pipeline from provider data to validated stored data.
- A small set of reusable data access functions that the risk, regime, optimization, and backtesting modules can depend on.

## Recommended Libraries

- `yfinance` for historical market data.
- `pandas` for tabular data cleaning and time-series operations.
- `numpy` for numerical calculations.
- `SQLAlchemy` for database models and repositories.
- `psycopg` for PostgreSQL access.
- `matplotlib` or `plotly` for basic visualizations.
- `pytest` for automated tests.

## Suggested Package Structure

```text
src/market_data_engine/
  models/
    asset.py
    corporate_action.py
    data_quality_report.py
    data_source.py
    ingestion_job.py
    price_bar.py
    time_series.py
  services/
    price_fetcher.py
    yahoo_provider.py
    validation.py
    calculations.py
    visualization.py
  db_models/
    price_bar_row.py
  mappers/
    price_bar_mapper.py
  repositories/
    price_repository.py
  sessions/
    session.py
tests/
  test_price_fetcher.py
  test_validation.py
  test_calculations.py
  test_price_repository.py
```

## Completion Steps

### Step 1: Project Setup

- Add packaging and dependency configuration with `pyproject.toml`.
- Make the package importable by adding `__init__.py` files.
- Configure `pytest` so tests can import from `src`.
- Decide the supported Python version and keep type hints consistent with it.

Done when:

- The package imports successfully.
- `pytest` can discover tests.
- Dependencies are documented in one place.

### Step 2: Domain Models

- Convert the core models into clear dataclasses.
- Define `PriceBar` as the central market data record.
- Define `Asset` for tickers, names, exchange, currency, and asset type.
- Define `CorporateAction` for splits and dividends.
- Define `DataSource` for provider metadata.
- Define `DataQualityReport` for validation results.
- Define `TimeSeries` as a wrapper around ordered `PriceBar` data.

Done when:

- All core entities have typed fields.
- Models do not depend on database classes.
- The same model objects can be used by services, repositories, and later projects.

### Step 3: Data Provider Layer

- Add a provider interface for historical price data.
- Implement a Yahoo Finance provider using `yfinance`.
- Support symbol, start date, end date, interval, and optional currency.
- Keep raw provider-specific code isolated from the rest of the engine.

Done when:

- The app can fetch historical bars for a symbol.
- Provider output is passed through normalization before the rest of the system sees it.
- Another provider could be added later without rewriting the fetcher.

### Step 4: Normalization

- Convert raw provider data into `PriceBar` objects.
- Standardize dates, intervals, asset IDs, prices, adjusted close, volume, and currency.
- Skip incomplete rows where required OHLC fields are missing.
- Preserve adjusted close so returns can use comparable historical values.

Done when:

- Provider data becomes a list of valid `PriceBar` objects.
- Date and interval behavior is consistent across all symbols.
- Normalization is covered by tests using sample data.

### Step 5: Validation

- Validate each `PriceBar`.
- Reject negative prices and negative volume.
- Check `high >= low`.
- Check open and close are within the high/low range.
- Detect duplicate `(asset_id, interval, day)` records.
- Detect missing weekday dates for daily data.
- Return a `DataQualityReport`.

TODO (Step 5):

- [ ] Add holiday calendars so missing-weekday checks exclude non-trading days (exchange holidays, early closes) and reduce false positives when `check_missing_weekdays` is enabled.

Done when:

- Invalid bars produce clear validation errors.
- Duplicate and missing data checks are testable.
- The fetcher can stop bad data before it is stored.

### Step 6: Persistence

- Define SQLAlchemy ORM tables for stored price bars.
- Map between database rows and domain models.
- Add repository methods to insert, upsert, and retrieve price bars.
- Make imports idempotent so re-running the same job does not duplicate data.
- Keep database sessions isolated behind a session factory.

Done when:

- Clean bars can be saved to the database.
- Existing bars can be updated safely.
- Stored bars can be retrieved by asset, interval, and date range.

### Step 7: Fetcher Service

- Build a `PriceFetcher` service that coordinates provider, normalization, validation, and optional persistence.
- Allow fetching without persistence for experimentation.
- Allow fetching with persistence for repeatable ingestion jobs.
- Return clean domain objects to callers.

Done when:

- One service call can fetch, validate, and optionally store price bars.
- Validation errors are raised before persistence.
- The service can be reused by scripts, APIs, notebooks, and later modules.

### Step 8: Return And Volatility Calculations

- Compute simple returns.
- Compute log returns.
- Compute rolling averages.
- Compute rolling volatility.
- Prefer adjusted close where available.

Done when:

- Later modules can consume clean return series.
- Calculations are deterministic and covered by tests.
- Edge cases such as empty data and zero prices are handled clearly.

### Step 9: Data Quality Summaries

- Summarize missing dates, duplicate keys, validation errors, and stale data.
- Expose data quality results alongside fetched or stored data.
- Keep data quality output simple enough to show in a dashboard later.

Done when:

- Every ingestion run can produce a quality report.
- Bad data can be diagnosed without manually inspecting raw provider output.

### Step 10: Basic Visualizations

- Add simple plots for price history, returns, rolling average, and volatility.
- Keep visualization code separate from core calculations.
- Make visualizations optional so the engine still works in backend-only environments.

Done when:

- A user can quickly inspect fetched data.
- Charts use clean engine outputs, not raw provider data.

### Step 11: Tests

- Test normalization with representative provider-like data.
- Test validation rules.
- Test return and volatility calculations.
- Test repository mapping and database behavior.
- Test the fetcher using a fake provider so tests do not depend on live network calls.

Done when:

- Core behavior is covered by automated tests.
- Tests can run without calling external APIs.
- Live provider behavior is isolated to optional integration tests.

### Step 12: Documentation

- Update the README with setup instructions.
- Document how to fetch data for one symbol.
- Document how to persist data.
- Document how to compute returns and view a basic chart.
- Include a short explanation of data quality checks.

Done when:

- A new developer can install the project and run a basic ingestion workflow.
- The Market Data Engine has a clear boundary for later projects to depend on.

## Suggested Build Order

1. Project setup.
2. Domain models.
3. Yahoo provider.
4. Normalization.
5. Validation.
6. Return and volatility calculations.
7. Repository and database persistence.
8. Fetcher orchestration.
9. Data quality summaries.
10. Basic visualizations.
11. Tests.
12. README documentation.

## Definition Of Done

The Market Data Engine is complete when it can fetch historical data for a symbol, normalize it into `PriceBar` objects, validate it, store it safely, retrieve it later, compute returns and volatility, report data quality issues, and provide basic visualizations without requiring any later investment app modules.
