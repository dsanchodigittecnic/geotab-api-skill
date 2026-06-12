# Geotab API Recipes — multi-step workflows

Each recipe chains the canonical calls from `operations-reference.md`. All calls go to the resolved endpoint (`https://{path}/apiv1`) and carry `credentials`; the chain below omits them for brevity but every real call needs them.

---

## Recipe 1 — Full onboarding: vehicle + driver + assignment

Goal: "dar de alta una unidad con su conductor".

1. **`Authenticate`** → get `sessionId` + `path` (endpoint `https://my.geotab.com/apiv1` if server unknown).
2. **`Add` `Device`** with `serialNumber`, `name`, `groups` → save the returned device `id`.
3. **`Add` `User`** with `isDriver: true`, `name`, `firstName`, `lastName`, `password`, `groups` → save the returned driver `id`.
4. **`Add` `DriverChange`** with `device.id` (step 2), `driver.id` (step 3), `dateTime` = now, `type: "Driver"`.

Result: the vehicle reports trips attributed to that driver from `dateTime` onward.

---

## Recipe 2 — Where is my fleet right now?

Goal: "posición actual de todos los vehículos" / "dónde está el camión X".

1. **`Get` `DeviceStatusInfo`** — empty `search` for the whole fleet, or `deviceSearch: { id }` for one vehicle → `latitude`, `longitude`, `speed`, `isDriving` per device.
2. **`GetAddresses`** with the coordinates from step 1 (`x` = longitude, `y` = latitude, same order as the input array) → human-readable `formattedAddress` per vehicle.

Tip: for continuous tracking, switch step 1 to **`GetFeed` `LogRecord`** and loop on `toVersion` instead of polling `Get`.

---

## Recipe 3 — Kilometers per vehicle in a period

Goal: "km recorridos por el vehículo X este mes".

Two equivalent approaches:

**A. Sum trips (per-trip detail):**
1. **`Get` `Trip`** with `deviceSearch: { id }`, `fromDate`, `toDate`.
2. Sum the `distance` field of every trip (already in km).

**B. Odometer delta (single total):**
1. **`Get` `StatusData`** with `diagnosticSearch: { id: "DiagnosticOdometerAdjustmentId" }`, `deviceSearch: { id }`, `fromDate`, `toDate`.
2. `(last reading − first reading) / 1000` → km (odometer `data` is in meters).

Use A when the user wants per-trip breakdown (driver, stops, speeds); use B for a plain total — it's one call and robust to missing trips.

---

## Recipe 4 — Continuous sync of GPS data

Goal: "sincronizar posiciones en mi base de datos" / "stream de datos".

1. **`GetFeed` `LogRecord`** with `fromVersion: "0000000000000000"` on the first call (optionally `deviceSearch` to narrow).
2. Store `result.data`, save `result.toVersion`.
3. Next call: pass the saved `toVersion` as `fromVersion` → only new records arrive.
4. Repeat on an interval (e.g. every 30–60 s). On `OverLimitException`, lower `resultsLimit` or poll less often.

The same loop works for `StatusData`, `Trip`, `ExceptionEvent` and `FaultData` feeds.
