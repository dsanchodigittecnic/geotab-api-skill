# Geotab API Operations Reference

## Base URL

```
POST https://my.geotab.com/apiv1      ← use for the first Authenticate when the server is unknown
POST https://{path}/apiv1             ← use for every call after Authenticate, where {path} comes from the auth response
```

All calls share the `/apiv1` path; only the server host changes. Resolve it concretely — never leave `{server}` as a literal placeholder in output:

- Server unknown → authenticate against `https://my.geotab.com/apiv1`.
- `Authenticate` returns `path` (e.g. `my3.geotab.com`) → all later calls go to `https://my3.geotab.com/apiv1`. A `path` of `"ThisServer"` means keep the current host.
- Server already known → use it directly (e.g. `https://my3.geotab.com/apiv1`).

---

## Authentication

```json
{
  "method": "Authenticate",
  "params": {
    "database": "CompanyName",        // required
    "userName": "user@example.com",   // required
    "password": "secret"              // required
  }
}
```

**Response:**
```json
{
  "result": {
    "credentials": {
      "database": "CompanyName",
      "userName": "user@example.com",
      "sessionId": "abc123..."
    },
    "path": "my3.geotab.com"
  }
}
```

Use `credentials` + `path` (as the new server) in all subsequent calls. If `path` is `"ThisServer"`, keep using the server you authenticated against. On `InvalidUserException` in a later call, the session expired — re-authenticate and retry.

All dates in requests and responses are ISO 8601 UTC: `2024-01-01T00:00:00.000Z`.

**Annotation convention:** every field in the example bodies below is marked inline as `// required` or `// optional`. `credentials` (with `database`, `userName`, `sessionId`) is required in `params` of every call after Authenticate and is marked once at the object level.

---

## Entity → typeName mapping

| What the user says | typeName |
|--------------------|----------|
| driver, conductor | `User` |
| vehicle, device, truck | `Device` |
| zone, geofence, area | `Zone` |
| group | `Group` |
| route | `Route` |
| trip, viaje | `Trip` |
| exception, alert | `ExceptionEvent` |
| rule, regla | `Rule` |
| diagnostic | `Diagnostic` |
| status data, telemetry | `StatusData` |
| fault data | `FaultData` |
| log record, GPS | `LogRecord` |

---

## Add (Create)

```json
{
  "method": "Add",
  "params": {
    "typeName": "User",               // required
    "entity": {                        // required
      "name": "John Doe",             // required, login name (usually the email)
      "firstName": "John",            // required
      "lastName": "Doe",              // required
      "employeeNo": "EMP001",         // optional
      "password": "InitialPass1!",    // required
      "changePassword": true,          // optional, force change on first login
      "comment": "Fleet driver",       // optional
      "groups": [                      // required, at least one valid group
        { "id": "GroupCompanyId" }
      ],
      "isDriver": true,               // required (true for drivers)
      "licenseNumber": "DL123456",    // optional
      "licenseProvince": "ON",        // optional, province/state code
      "isEmailReportEnabled": false,  // optional
      "activeFrom": "2024-01-01T00:00:00.000Z", // optional
      "activeTo": "2099-12-31T00:00:00.000Z"    // optional
    },
    "credentials": {                   // required
      "database": "CompanyName",
      "userName": "admin@example.com",
      "sessionId": "abc123"
    }
  }
}
```

**Response:**
```json
{ "result": "aXXXXXXXXXXX" }
```
`result` is the new entity's `id`.

---

## Get (Read / Search)

```json
{
  "method": "Get",
  "params": {
    "typeName": "User",      // required
    "search": {              // optional — empty or omitted = all entities
      "isDriver": true       // optional — filter fields vary by entity
    },
    "resultsLimit": 100,     // optional, default unlimited
    "credentials": {         // required
      "database": "CompanyName",
      "userName": "admin@example.com",
      "sessionId": "abc123"
    }
  }
}
```

**Response:**
```json
{
  "result": [
    {
      "id": "aXXXXXXXXXXX",
      "name": "John Doe",
      "firstName": "John",
      "lastName": "Doe",
      "isDriver": true,
      ...
    }
  ]
}
```

Empty `search: {}` returns all entities of that type. To fetch a single entity by id, use `search: { "id": "aXXXXXXXXXXX" }`.

### Common search fields by entity

| typeName | Useful search fields |
|----------|---------------------|
| `User` | `isDriver`, `name`, `groups` |
| `Device` | `name`, `serialNumber`, `groups`, `activeFrom`, `activeTo` |
| `Trip` | `deviceSearch`, `fromDate`, `toDate` |
| `LogRecord` | `deviceSearch`, `fromDate`, `toDate` |
| `StatusData` | `deviceSearch`, `diagnosticSearch`, `fromDate`, `toDate` |
| `ExceptionEvent` | `deviceSearch`, `ruleSearch`, `fromDate`, `toDate` |

### Get example — trips for a device in a date range

```json
{
  "method": "Get",
  "params": {
    "typeName": "Trip",                            // required
    "search": {                                    // optional, but recommended to bound the result set
      "deviceSearch": { "id": "bXXXXXXXXXXX" },   // optional, filter by device
      "fromDate": "2024-01-01T00:00:00.000Z",     // optional
      "toDate": "2024-01-08T00:00:00.000Z"        // optional
    },
    "resultsLimit": 1000,    // optional
    "credentials": {         // required
      "database": "CompanyName",
      "userName": "admin@example.com",
      "sessionId": "abc123"
    }
  }
}
```

**Response:** array of `Trip` objects — key fields: `start`, `stop` (timestamps), `distance` (km), `drivingDuration`, `stopDuration`, `maximumSpeed`, `averageSpeed`, `device`, `driver`, `stopPoint` (`{ "x": lon, "y": lat }`).

---

## Set (Update)

```json
{
  "method": "Set",
  "params": {
    "typeName": "User",               // required
    "entity": {                        // required — the FULL entity, not a partial patch
      "id": "aXXXXXXXXXXX",           // required
      "name": "John Doe",             // required
      "firstName": "John",            // required
      "lastName": "Doe Updated",      // required
      "isDriver": true,               // required
      "groups": [{ "id": "GroupCompanyId" }]  // required
    },
    "credentials": {                   // required
      "database": "CompanyName",
      "userName": "admin@example.com",
      "sessionId": "abc123"
    }
  }
}
```

**Response:**
```json
{ "result": null }
```

Set replaces the full entity — always include all required fields, not just changed ones. Omitted fields are wiped. Recommended pattern: `Get` the entity by `id`, modify the fields you need, then `Set` the whole object back.

---

## Remove (Delete)

```json
{
  "method": "Remove",
  "params": {
    "typeName": "User",      // required
    "entity": {              // required — only the id is needed
      "id": "aXXXXXXXXXXX"   // required
    },
    "credentials": {         // required
      "database": "CompanyName",
      "userName": "admin@example.com",
      "sessionId": "abc123"
    }
  }
}
```

**Response:**
```json
{ "result": null }
```

Removal is irreversible via the API. Non-destructive alternative: deactivate with `Set` by moving `activeTo` to a past date — this hides the entity while preserving its trip/telemetry history.

---

## GetFeed (Incremental streaming)

```json
{
  "method": "GetFeed",
  "params": {
    "typeName": "LogRecord",                       // required
    "search": {                                    // optional, narrows the feed
      "deviceSearch": { "id": "bXXXXXXXXXXX" }    // optional
    },
    "fromVersion": "0000000000000000",  // required — use "0..." for first call, then last toVersion
    "resultsLimit": 50000,              // optional, max 50000
    "credentials": {                    // required
      "database": "CompanyName",
      "userName": "admin@example.com",
      "sessionId": "abc123"
    }
  }
}
```

**Response:**
```json
{
  "result": {
    "data": [ { "id": "...", ... } ],
    "toVersion": "0000000000000ABC"
  }
}
```

Save `toVersion` and pass it as `fromVersion` on the next call to get only new records.

---

## Device (Vehicle) — Add example

```json
{
  "method": "Add",
  "params": {
    "typeName": "Device",               // required
    "entity": {                          // required
      "serialNumber": "GT9000000000",   // required, GO device serial
      "name": "Truck 01",               // required, display name in the fleet
      "groups": [{ "id": "GroupCompanyId" }],  // required, at least one valid group
      "comment": "Main delivery truck",  // optional
      "engineVehicleIdentificationNumber": "1HGBH41JXMN109186", // optional
      "vehicleIdentificationNumber": "1HGBH41JXMN109186",       // optional
      "licensePlate": "ABC-1234",        // optional
      "activeFrom": "2024-01-01T00:00:00.000Z"  // optional
    },
    "credentials": { ... }               // required
  }
}
```

---

## Zone (Geofence) — Add example

```json
{
  "method": "Add",
  "params": {
    "typeName": "Zone",                  // required
    "entity": {                           // required
      "name": "Warehouse Barcelona",     // required
      "points": [                         // required, polygon outline (min 3 points)
        { "x": 2.1734, "y": 41.3851 },
        { "x": 2.1750, "y": 41.3851 },
        { "x": 2.1750, "y": 41.3870 },
        { "x": 2.1734, "y": 41.3870 }
      ],
      "zoneTypes": [{ "id": "ZoneTypeCustomerId" }],  // required
      "groups": [{ "id": "GroupCompanyId" }],          // required
      "displayed": true,                              // optional, show on map
      "mustIdentifyStops": false,                     // optional
      "fillColor": { "r": 255, "g": 0, "b": 0, "a": 80 }, // optional
      "activeFrom": "2024-01-01T00:00:00.000Z",      // optional
      "activeTo": "2099-12-31T00:00:00.000Z",        // optional
      "comment": "Main warehouse geofence"            // optional
    },
    "credentials": { ... }                // required
  }
}
```

`points` is the polygon outline: `x` = longitude, `y` = latitude (note the order). The polygon closes automatically. Built-in zone types: `ZoneTypeCustomerId`, `ZoneTypeHomeId`, `ZoneTypeOfficeId`.

---

## ExecuteMultiCall (Batching)

Run several calls in one HTTP request — credentials go once at the top level, not inside each call:

```json
{
  "method": "ExecuteMultiCall",
  "params": {
    "calls": [               // required, one object per call (no credentials inside)
      { "method": "Get", "params": { "typeName": "Device", "resultsLimit": 10 } },
      { "method": "Get", "params": { "typeName": "User", "search": { "isDriver": true } } }
    ],
    "credentials": {         // required, once at top level
      "database": "CompanyName",
      "userName": "admin@example.com",
      "sessionId": "abc123"
    }
  }
}
```

**Response:**
```json
{ "result": [ [ ...devices ], [ ...drivers ] ] }
```

`result` is an array with one element per call, in order. If any call fails, the whole MultiCall returns an error — don't mix risky writes into a batch.

---

## Error response shape

```json
{
  "error": {
    "message": "Detailed error message",
    "code": -32000,
    "data": {
      "id": "...",
      "type": "InvalidUserException",
      "requestIndex": 0
    }
  }
}
```

Common error types and what to do:

| Type | Meaning | Action |
|------|---------|--------|
| `InvalidUserException` | Bad credentials or expired `sessionId` | Re-authenticate and retry |
| `DbUnavailableException` | Database busy or moved | Retry with backoff; re-check `path` from Authenticate |
| `OverLimitException` | Result set or rate limit exceeded | Lower `resultsLimit`, paginate with date ranges or `GetFeed` |
| `MissingMemberException` | Referenced `id` doesn't exist | Verify the `id` with a `Get` call |
| `DuplicateException` | Entity with same unique field exists | Search for the existing entity first |
