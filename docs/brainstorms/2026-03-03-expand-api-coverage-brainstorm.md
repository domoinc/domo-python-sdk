# Expand Domo SDK API Coverage

**Date:** 2026-03-03
**Status:** Brainstorm

## What We're Building

Expand domo-sdk-python from ~22 API client areas to comprehensive coverage of Domo's ~31 API surfaces. This includes:

1. **New API clients** for missing areas (AppDB, Scheduled Reports, Beast Modes, FileSets, Task Center, Certified Content, Code Engine, Cloud Amplifier, Remote Domostats)
2. **Deepened existing clients** (datasets, files, connectors, dataflows) with Product API endpoints
3. **Pydantic model migration** — new clients return models by default, existing clients migrate incrementally

## Why This Approach

### Auth: Let It Fail Naturally (Stripe/Slack Pattern)

Domo has two auth modes:
- **OAuth** (`api.domo.com/v1/...`) — Platform APIs only
- **Developer Token** (`{instance}.domo.com/api/...`) — superset, Platform + Product APIs

Research across GitHub, Stripe, AWS, Slack, and Google SDKs shows universal consensus: **don't validate auth at client creation time**. The server enforces permissions. Our transport layer already routes to the right base URL based on auth mode — Product API clients just need different `URL_BASE` constants.

No runtime auth checks. No warnings. No separate client classes per auth mode.

### Rollout: One Client Per PR

Each new API client ships as its own PR with full tests. Benefits:
- Small, reviewable changes
- Get value incrementally
- Easy to revert if an API shape is wrong
- Clear git history per API area

### Models: Default Returns for New Clients, Incremental Migration for Old

**New clients** return Pydantic models by default (better DX, typed responses).
**Existing clients** migrate to return models incrementally as we deepen them.

This means the SDK will have a transitional period where some clients return dicts and others return models. That's acceptable — it's better than a big-bang migration or permanent inconsistency.

### Extension: Same Client, New Methods

When deepening existing clients (e.g., adding partition management to DataSetClient), new methods go directly in the existing client class. No subclasses, no mixins. Users access everything from `domo.datasets`.

Product API methods use different `URL_BASE` paths within the same client file.

## Key Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Auth validation | None — let server enforce | Industry consensus (Stripe, Slack, boto3). Simplest. |
| Rollout strategy | One client per PR | Small reviews, incremental value, clear git history |
| New client return types | Pydantic models by default | Better DX, typed responses, modern Python |
| Existing client migration | Incremental to models | Migrate each client as we deepen it. No big bang. |
| Extending existing clients | Add methods to same class | Simplest. No subclass/mixin complexity. |
| Product API URL routing | Different URL_BASE per client | Transport already handles base URL by auth mode |
| Audience | Internal WKS + public PyPI | Internal needs first, but keep it publishable |

## Priority Order

Based on immediate needs and API surface size:

| Priority | Client | Why |
|---|---|---|
| 1 | **AppDB** | Immediate blocker — building Domo apps that need document storage |
| 2 | **Deepen DataSetClient** | Partitions, tags, sharing, upload sessions — core workflow gaps |
| 3 | **Deepen FilesClient** | Permissions, revisions, copy/duplicate — needed for file workflows |
| 4 | **Scheduled Reports** | Large surface (20+ endpoints), high value for WKS automation |
| 5 | **Beast Modes** | Card/dataset management — search, get, update, stats |
| 6 | **FileSets (BETA)** | File collections — complements AppDB for app development |
| 7 | **Task Center** | Workflow task queues — needed for workflow automation |
| 8 | **Certified Content** | Small surface — get/set/remove certification tags |
| 9 | **Code Engine** | Single endpoint — execute serverless functions |
| 10 | **Deepen CardsClient** | Chart definitions, drill views, render/image export |
| 11 | **Deepen ConnectorsClient** | Account types, connector metadata |
| 12 | **Deepen DataFlowsClient** | Create, update, delete, trigger execution |
| 13 | **Cloud Amplifier** | Federated integrations — niche use case |
| 14 | **Remote Domostats** | DomoStats app/job management — niche |

## Implementation Pattern (Per Client)

Each new client requires these files:

```
src/domo_sdk/models/{area}.py          # Pydantic v2 models (DomoModel base)
src/domo_sdk/clients/{area}.py         # Sync client (DomoAPIClient base)
src/domo_sdk/async_clients/{area}.py   # Async mirror (AsyncDomoAPIClient base)
src/domo_sdk/domo.py                   # Wire up in Domo + AsyncDomo._init_clients()
tests/test_models/test_{area}.py       # Model validation tests
tests/test_clients/test_{area}.py      # Sync tests (MagicMock transport)
tests/test_async_clients/test_{area}.py # Async tests (respx mocking)
```

Conventions:
- Module-level `URL_BASE` constant
- Methods return Pydantic models (new clients) or dicts (existing, until migrated)
- Async client is a mechanical mirror: `async def` + `await`
- Sync list methods use generators, async list methods return `list[Model]`

## Open Questions

_None — all resolved during brainstorming._
