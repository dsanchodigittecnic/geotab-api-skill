---
name: geotab
description: "Trigger: geotab api, create driver, add device, get trips, geotab endpoint, geotab call. Map a Geotab goal to HTTP method, endpoint, request body, and expected response."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## Activation Contract

Activate when the user describes a Geotab operation goal in plain language (e.g., "create a driver", "get all devices", "update a zone") and needs the exact API call to make.

## Hard Rules

- ALL Geotab API calls use HTTP `POST` to `https://{server}/apiv1`. There are no GET/PUT/DELETE endpoints.
- Every request body is JSON-RPC style: `{ "method": "...", "params": { ... } }`.
- `params` MUST include `credentials` with `{ "database", "userName", "sessionId" }` or `{ "database", "userName", "password" }`.
- `typeName` identifies the entity (e.g., `"User"` for drivers, `"Device"` for vehicles).
- Never invent field names — reference `assets/operations-reference.md` for canonical schemas.

## Decision Gates

| Goal verb | Geotab method | Notes |
|-----------|--------------|-------|
| create / add / new | `Add` | Returns the new entity's `id` |
| get / fetch / search / list / find | `Get` | Use `search` object to filter; empty search = all |
| update / edit / modify / set | `Set` | Must include full entity with `id` |
| delete / remove | `Remove` | Requires entity with `id` |
| login / authenticate | `Authenticate` | Returns `credentials` for subsequent calls |
| stream / changes since | `GetFeed` | Returns incremental data with `toVersion` token |

## Execution Steps

1. Parse the user's goal → identify the **verb** and **entity** (e.g., "create" + "driver").
2. Map entity to `typeName` — see `assets/operations-reference.md`.
3. Select the Geotab `method` from the Decision Gates table.
4. Build the full request body from the canonical schema in `assets/operations-reference.md`.
5. Output in this exact format:

```
HTTP method : POST
Endpoint    : https://{server}/apiv1
Geotab call : {method}
typeName    : {TypeName}

Request body:
{full JSON with all required fields shown}

Response:
{expected response shape or entity object}
```

6. Flag optional fields with `// optional` inline comment in the JSON.
7. If authentication is not yet obtained, prepend the `Authenticate` call first.

## Output Contract

Every response MUST include:
- HTTP method (always POST)
- Full endpoint URL pattern
- Complete JSON request body (no placeholders left unexplained)
- Expected response shape with field descriptions
- A note on required vs. optional fields

## References

- [`assets/operations-reference.md`](assets/operations-reference.md) — canonical entity schemas and field lists
