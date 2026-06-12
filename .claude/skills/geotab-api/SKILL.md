---
name: geotab-api
description: "Trigger: geotab api, create driver, add device, get trips, geotab endpoint, geotab call, crear conductor, añadir dispositivo, obtener viajes, eliminar conductor. Map a Geotab goal to HTTP method, endpoint, request body, and expected response."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.1"
---

## Activation Contract

Activate when the user describes a Geotab operation goal in plain language — in any language (e.g., "create a driver", "crear conductor", "get all devices", "update a zone") — and needs the exact API call to make. Respond in the user's language; keep JSON field names and Geotab method names verbatim.

## Hard Rules

- ALL Geotab API calls use HTTP `POST` to `https://{server}/apiv1`. There are no GET/PUT/DELETE endpoints.
- Every request body is JSON-RPC style: `{ "method": "...", "params": { ... } }`.
- `params` MUST include `credentials` with `{ "database", "userName", "sessionId" }` or `{ "database", "userName", "password" }`.
- `typeName` identifies the entity (e.g., `"User"` for drivers, `"Device"` for vehicles).
- Never invent field names — reference `assets/operations-reference.md` for canonical schemas.

## Decision Gates

| Goal verb (EN / ES) | Geotab method | Notes |
|---------------------|--------------|-------|
| create / add / new — crear / añadir / nuevo | `Add` | Returns the new entity's `id` |
| get / fetch / search / list / find — obtener / buscar / listar / consultar | `Get` | Use `search` object to filter; empty search = all |
| update / edit / modify / set — actualizar / editar / modificar | `Set` | Must include full entity with `id` — `Get` it first, modify, send back whole |
| delete / remove — eliminar / borrar / quitar | `Remove` | Requires entity with `id`; irreversible — see Safety Rules |
| login / authenticate — autenticar / iniciar sesión | `Authenticate` | Returns `credentials` for subsequent calls |
| stream / changes since — sincronizar / cambios desde | `GetFeed` | Returns incremental data with `toVersion` token |
| batch / multiple ops — varias operaciones | `ExecuteMultiCall` | Wraps several calls in one request |

## Safety Rules

- `Remove` is irreversible via the API. Always show a `Get` call first to confirm the target `id`, and mention the non-destructive alternative: `Set` with `activeTo` in the past (deactivation preserves trip history).
- `Set` replaces the whole entity. Recommend the pattern: `Get` by `id` → modify fields → `Set` the full object. Sending a partial entity silently wipes omitted fields.
- Never echo real passwords or `sessionId` values from the conversation back into examples — use placeholders.

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
7. If authentication is not yet obtained, prepend the `Authenticate` call first and note that the returned `path` becomes `{server}` (unless it is `"ThisServer"`, meaning keep the current server).
8. For date filters, use ISO 8601 UTC (`2024-01-01T00:00:00.000Z`). Suggest `resultsLimit` on `Get` calls that may return large sets.
9. Close with the most likely errors for that call (`InvalidUserException` → re-authenticate; `OverLimitException` → reduce `resultsLimit`/paginate).

## Output Contract

Every response MUST include:
- HTTP method (always POST)
- Full endpoint URL pattern
- Complete JSON request body (no placeholders left unexplained)
- Expected response shape with field descriptions
- A note on required vs. optional fields

## References

- [`assets/operations-reference.md`](assets/operations-reference.md) — canonical entity schemas and field lists
