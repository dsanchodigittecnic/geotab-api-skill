# geotab-api — Claude Code skill

Skill de Claude Code que traduce un objetivo de Geotab en lenguaje natural ("crear conductor", "dónde está el camión", "km del mes") a la llamada exacta de la API MyGeotab: método HTTP, URL del endpoint resuelta, request body JSON con cada campo marcado como obligatorio u opcional, y la forma de la respuesta esperada.

## Estructura

```
.claude-plugin/
├── plugin.json                     # manifiesto del plugin (apunta a .claude/skills)
└── marketplace.json                # catálogo del marketplace "digittecnic"
.claude/skills/geotab-api/
├── SKILL.md                        # contrato de la skill (triggers, reglas, formato de salida)
└── assets/
    ├── operations-reference.md     # esquemas canónicos por entidad y método
    └── recipes.md                  # workflows multi-paso (alta completa, posición de flota, km, sync)
```

La única fuente de verdad es `.claude/skills/geotab-api/` — el plugin la referencia directamente, no hay copias duplicadas que sincronizar.

## Instalación

**Como plugin** (recomendado para compartir con el equipo) — este repo es a la vez plugin y marketplace:

```
/plugin marketplace add dsanchodigittecnic/geotab-api-skill
/plugin install geotab-api@digittecnic
```

Instalada como plugin, la skill se invoca como `/geotab-api:geotab-api` (o se activa sola al describir una operación de Geotab).

**Como skill de proyecto**: clona este repositorio y abre Claude Code en él; la skill se carga automáticamente desde `.claude/skills/`.

**Como skill de usuario** (disponible en todos tus proyectos):

```bash
cp -r .claude/skills/geotab-api ~/.claude/skills/
```

## Uso

Invócala con el slash command y un objetivo en cualquier idioma:

```
/geotab-api crear una unidad
/geotab-api dónde está la flota ahora
/geotab-api km del vehículo X este mes
/geotab-api eliminar conductor
```

También se activa sola cuando describes una operación de Geotab en la conversación.

## Qué cubre

- CRUD completo (`Add`, `Get`, `Set`, `Remove`) sobre `User`, `Device`, `Zone`, `Trip` y demás entidades.
- Autenticación y resolución del servidor (`Authenticate` → `path`).
- Posición en tiempo real (`DeviceStatusInfo`) y geocodificación inversa (`GetAddresses`).
- Telemetría (`StatusData`) con tabla de diagnósticos conocidos (odómetro, combustible, horas de motor…).
- Asignación de conductores (`DriverChange`), streaming incremental (`GetFeed`) y batching (`ExecuteMultiCall`).
- Recetas multi-paso en `assets/recipes.md`.

## Versiones

Ver [CHANGELOG.md](CHANGELOG.md). Las versiones se etiquetan en git (`v1.4`, …).

## Licencia

Apache-2.0
