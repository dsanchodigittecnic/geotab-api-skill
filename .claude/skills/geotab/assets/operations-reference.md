# Geotab API Operations Reference

## Base URL

```
POST https://{server}/apiv1
```

All calls share this endpoint. `{server}` is the MyGeotab server (e.g., `my.geotab.com`, `my3.geotab.com`).

---

## Authentication

```json
{
  "method": "Authenticate",
  "params": {
    "database": "CompanyName",
    "userName": "user@example.com",
    "password": "secret"
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

Use `credentials` + `path` (as the new server) in all subsequent calls.

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
    "typeName": "User",
    "entity": {
      "name": "John Doe",
      "firstName": "John",
      "lastName": "Doe",
      "employeeNo": "EMP001",         // optional
      "password": "InitialPass1!",
      "changePassword": true,          // optional, force change on first login
      "comment": "Fleet driver",       // optional
      "groups": [
        { "id": "GroupCompanyId" }
      ],
      "isDriver": true,
      "licenseNumber": "DL123456",    // optional
      "licenseProvince": "ON",        // optional, province/state code
      "isEmailReportEnabled": false,  // optional
      "activeFrom": "2024-01-01T00:00:00.000Z", // optional
      "activeTo": "2099-12-31T00:00:00.000Z"    // optional
    },
    "credentials": {
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
    "typeName": "User",
    "search": {
      "isDriver": true       // optional — filter fields vary by entity
    },
    "resultsLimit": 100,     // optional, default unlimited
    "credentials": {
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

Empty `search: {}` returns all entities of that type.

### Common search fields by entity

| typeName | Useful search fields |
|----------|---------------------|
| `User` | `isDriver`, `name`, `groups` |
| `Device` | `name`, `serialNumber`, `groups`, `activeFrom`, `activeTo` |
| `Trip` | `deviceSearch`, `fromDate`, `toDate` |
| `LogRecord` | `deviceSearch`, `fromDate`, `toDate` |
| `StatusData` | `deviceSearch`, `diagnosticSearch`, `fromDate`, `toDate` |
| `ExceptionEvent` | `deviceSearch`, `ruleSearch`, `fromDate`, `toDate` |

---

## Set (Update)

```json
{
  "method": "Set",
  "params": {
    "typeName": "User",
    "entity": {
      "id": "aXXXXXXXXXXX",
      "name": "John Doe",
      "firstName": "John",
      "lastName": "Doe Updated",
      "isDriver": true,
      "groups": [{ "id": "GroupCompanyId" }]
    },
    "credentials": {
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

Set replaces the full entity — always include all required fields, not just changed ones.

---

## Remove (Delete)

```json
{
  "method": "Remove",
  "params": {
    "typeName": "User",
    "entity": {
      "id": "aXXXXXXXXXXX"
    },
    "credentials": {
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

---

## GetFeed (Incremental streaming)

```json
{
  "method": "GetFeed",
  "params": {
    "typeName": "LogRecord",
    "search": {
      "deviceSearch": { "id": "bXXXXXXXXXXX" }
    },
    "fromVersion": "0000000000000000",  // use "0..." for first call
    "resultsLimit": 50000,
    "credentials": {
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
    "typeName": "Device",
    "entity": {
      "serialNumber": "GT9000000000",
      "name": "Truck 01",
      "groups": [{ "id": "GroupCompanyId" }],
      "comment": "Main delivery truck",  // optional
      "engineVehicleIdentificationNumber": "1HGBH41JXMN109186", // optional
      "vehicleIdentificationNumber": "1HGBH41JXMN109186",       // optional
      "licensePlate": "ABC-1234",        // optional
      "activeFrom": "2024-01-01T00:00:00.000Z"  // optional
    },
    "credentials": { ... }
  }
}
```

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

Common error types: `InvalidUserException`, `DbUnavailableException`, `OverLimitException`, `MissingMemberException`.
