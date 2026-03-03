# Domo SDK Python

Modernized fork of `domoinc/domo-python-sdk` (pydomo). Adds async support (httpx), Pydantic v2 models, developer token auth, and 22+ API clients.

**Repo:** `wksusa/domo-sdk-python` (fork of `domoinc/domo-python-sdk`)

## Stack

- **Python 3.10+** with `uv` for dependency management
- **Pydantic v2** for models (`DomoModel` base with `extra="ignore"`, `populate_by_name=True`)
- **requests** (sync transport) + **httpx** (async transport)
- **Auth:** OAuth (`api.domo.com`) or Developer Token (`{instance}.domo.com/api`)

## Key Commands

```bash
uv run --extra dev python -m pytest tests/ -q --ignore=tests/test_utilities_type_conversion.py --ignore=tests/integration
uv run --extra dev ruff check src/ tests/
```

## Structure

```
src/domo_sdk/
├── models/          # Pydantic v2 models (DomoModel base)
├── clients/         # Sync API clients (DomoAPIClient base)
├── async_clients/   # Async mirrors (AsyncDomoAPIClient base)
├── transport/       # HTTP transports + auth strategies
└── domo.py          # Domo + AsyncDomo entry points
tests/
├── test_models/
├── test_clients/     # MagicMock transport tests
├── test_async_clients/ # respx-based async tests
└── test_transport/
```

## Conventions

- New clients return Pydantic models (AppDB is the first; existing clients still return dicts)
- Module-level `URL_BASE` constant per client
- Async client is a mechanical mirror: `async def` + `await`
- Sync list methods use generators, async list methods return `list[Model]`
- Tests: sync uses `MagicMock` transport, async uses `respx`

## Linear

- **Project**: Domo SDK Python
- **Project ID**: 20997992-c296-4530-93ae-90b79b15888c
- **Project URL**: https://linear.app/wksusa/project/domo-sdk-python-6deeecba3598
- **Team**: AI Labs
