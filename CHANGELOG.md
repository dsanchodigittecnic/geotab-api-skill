# Changelog

## v1.4 — 2026-06-12

- Nueva entidad `DeviceStatusInfo` (posición en tiempo real) con nota de que "dónde está X" NO es un `Get` de `Device`.
- Tabla de diagnósticos conocidos para telemetría `StatusData` (odómetro, nivel de combustible, horas de motor, RPM…) con unidades, y regla de no inventar ids de diagnóstico.
- `GetAddresses` (geocodificación inversa) y `DriverChange` (asignar conductor a vehículo).
- Nuevo asset `assets/recipes.md` con workflows multi-paso: alta completa de unidad+conductor, posición de flota con direcciones, km por periodo (viajes vs. delta de odómetro) y sincronización continua con `GetFeed`.
- Fuente única de verdad: eliminadas las copias duplicadas de la raíz (`SKILL.md`, `assets/`); la skill vive solo en `.claude/skills/geotab-api/`.
- Añadidos README.md y CHANGELOG.md; versiones etiquetadas en git.

## v1.3 — 2026-06-12

- Todos los campos de los request bodies anotados inline como `// required` u `// optional`, con aclaradores cortos; el Output Contract exige el marcado completo más un resumen final.

## v1.2 — 2026-06-12

- URLs de endpoint concretas en cada llamada en lugar del placeholder `{server}`: `https://my.geotab.com/apiv1` para el primer `Authenticate` y después `https://{path}/apiv1` con el `path` de la respuesta de autenticación (`"ThisServer"` = mantener el host actual).

## v1.1 — 2026-06-12

- Renombrada la skill `geotab` → `geotab-api`.
- Triggers y verbos en español en la tabla de decisión; responder en el idioma del usuario.
- Sección Safety Rules: `Remove` irreversible (Get previo de confirmación + alternativa de desactivación con `activeTo`), patrón Get→modificar→Set para actualizaciones, no reflejar credenciales reales.
- Esquema de `Zone` (geofence), `ExecuteMultiCall` (batching), ejemplo de `Get Trip` con rango de fechas, tabla de errores con acciones de recuperación, fechas ISO 8601 UTC y nota sobre `path: "ThisServer"`.

## v1.0 — 2026-06-11

- Skill inicial: contrato de activación, tabla verbo→método (`Add`/`Get`/`Set`/`Remove`/`Authenticate`/`GetFeed`), formato de salida fijo y referencia de operaciones con esquemas de `User` y `Device`.
