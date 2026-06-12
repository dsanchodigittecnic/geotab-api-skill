#!/usr/bin/env python3
"""Optional validation of the skill's documented schemas against a real MyGeotab database.

Credentials come from environment variables; if they are not set the script
exits cleanly (the validation is opt-in, never required):

    GEOTAB_DATABASE   company database name            (required to run)
    GEOTAB_USERNAME   MyGeotab user                    (required to run)
    GEOTAB_PASSWORD   password                         (or GEOTAB_SESSION_ID)
    GEOTAB_SESSION_ID existing session id              (alternative to password)
    GEOTAB_SERVER     starting server, default my.geotab.com

Read-only by default: one bounded Get per documented entity, plus
GetAddresses, ExecuteMultiCall, GetFeed and the diagnostic-id table.
Pass --write to also run an Add -> Set -> Remove cycle on a clearly named
temporary Zone (the only state-changing test, and it cleans up after itself).

Exit code: 0 when credentials are missing or all checks pass/warn, 1 on FAIL.
"""

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

# Core response fields the skill documents per entity (operations-reference.md).
# A missing field in a live sample is reported as WARN, not FAIL: Geotab omits
# some defaulted fields when serializing, so only call errors fail the run.
DOCUMENTED_FIELDS = {
    "User": ["id", "name", "firstName", "lastName"],
    "Device": ["id", "name"],
    "Zone": ["id", "name", "points"],
    "Group": ["id"],
    "Rule": ["id", "name"],
    "Trip": ["id", "device", "start", "stop", "distance"],
    "DeviceStatusInfo": ["device", "latitude", "longitude", "speed", "dateTime"],
    "LogRecord": ["latitude", "longitude", "dateTime", "device"],
    "StatusData": ["data", "dateTime", "device", "diagnostic"],
    "ExceptionEvent": ["id", "device", "rule"],
    "Diagnostic": ["id", "name"],
}

# Diagnostic ids from the skill's Diagnostics table — each must exist for real.
DOCUMENTED_DIAGNOSTICS = [
    "DiagnosticOdometerAdjustmentId",
    "DiagnosticFuelLevelId",
    "DiagnosticDeviceTotalFuelId",
    "DiagnosticEngineHoursAdjustmentId",
    "DiagnosticEngineSpeedId",
    "DiagnosticEngineCoolantTemperatureId",
]


class GeotabError(Exception):
    def __init__(self, error):
        self.type = (error.get("data") or {}).get("type", "UnknownError")
        super().__init__(f"{self.type}: {error.get('message', '')}")


class Reporter:
    def __init__(self):
        self.counts = {"OK": 0, "WARN": 0, "SKIP": 0, "FAIL": 0}

    def log(self, status, check, detail=""):
        self.counts[status] += 1
        suffix = f" — {detail}" if detail else ""
        print(f"[{status:<4}] {check}{suffix}")

    def summary(self):
        c = self.counts
        print(f"\nSummary: {c['OK']} OK, {c['WARN']} WARN, {c['SKIP']} SKIP, {c['FAIL']} FAIL")
        return 0 if c["FAIL"] == 0 else 1


def call(server, method, params):
    body = json.dumps({"method": method, "params": params}).encode()
    req = urllib.request.Request(
        f"https://{server}/apiv1", data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if "error" in payload:
        raise GeotabError(payload["error"])
    return payload["result"]


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def check_fields(report, type_name, sample):
    missing = [f for f in DOCUMENTED_FIELDS[type_name] if f not in sample]
    if missing:
        report.log("WARN", f"Get {type_name}", f"documented fields missing from sample: {', '.join(missing)}")
    else:
        report.log("OK", f"Get {type_name}", "call + documented fields")


def check_get(report, server, creds, type_name, search=None):
    """Bounded Get; returns the first entity (or None). Never raises."""
    params = {"typeName": type_name, "resultsLimit": 1, "credentials": creds}
    if search:
        params["search"] = search
    try:
        result = call(server, "Get", params)
    except GeotabError as e:
        report.log("FAIL", f"Get {type_name}", str(e))
        return None
    if not result:
        report.log("SKIP", f"Get {type_name}", "call ok, no data in database to verify fields")
        return None
    check_fields(report, type_name, result[0])
    return result[0]


def write_cycle(report, server, creds):
    """Add -> Set -> Remove on a temporary, clearly named Zone."""
    zone = {
        "name": "ZZ_SKILL_VALIDATION_TEMP",
        "points": [
            {"x": 2.17340, "y": 41.38510},
            {"x": 2.17350, "y": 41.38510},
            {"x": 2.17345, "y": 41.38520},
        ],
        "zoneTypes": [{"id": "ZoneTypeCustomerId"}],
        "groups": [{"id": "GroupCompanyId"}],
        "comment": "Temporary zone created by scripts/validate.py — safe to delete",
    }
    zone_id = None
    try:
        zone_id = call(server, "Add", {"typeName": "Zone", "entity": zone, "credentials": creds})
        report.log("OK", "Add Zone", f"id {zone_id}")
        zone["id"] = zone_id
        zone["comment"] = "Updated by scripts/validate.py"
        call(server, "Set", {"typeName": "Zone", "entity": zone, "credentials": creds})
        report.log("OK", "Set Zone")
    except GeotabError as e:
        report.log("FAIL", "Add/Set Zone", str(e))
    finally:
        if zone_id:
            try:
                call(server, "Remove", {"typeName": "Zone", "entity": {"id": zone_id}, "credentials": creds})
                report.log("OK", "Remove Zone", "temporary zone cleaned up")
            except GeotabError as e:
                report.log("FAIL", "Remove Zone", f"{e} — delete '{zone['name']}' manually")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="also run the Add/Set/Remove cycle on a temporary Zone")
    args = parser.parse_args()

    database = os.environ.get("GEOTAB_DATABASE")
    username = os.environ.get("GEOTAB_USERNAME")
    password = os.environ.get("GEOTAB_PASSWORD")
    session_id = os.environ.get("GEOTAB_SESSION_ID")
    server = os.environ.get("GEOTAB_SERVER", "my.geotab.com")

    if not (database and username and (password or session_id)):
        print("Validation skipped (optional): set GEOTAB_DATABASE, GEOTAB_USERNAME and")
        print("GEOTAB_PASSWORD (or GEOTAB_SESSION_ID) to validate against a real database.")
        return 0

    report = Reporter()
    print("== geotab-api schema validation ==")

    if session_id:
        creds = {"database": database, "userName": username, "sessionId": session_id}
        report.log("SKIP", "Authenticate", "using GEOTAB_SESSION_ID")
    else:
        try:
            auth = call(server, "Authenticate", {"database": database, "userName": username, "password": password})
        except (GeotabError, OSError) as e:
            report.log("FAIL", "Authenticate", str(e))
            return report.summary()
        creds = auth["credentials"]
        path = auth.get("path", "ThisServer")
        if path and path != "ThisServer":
            server = path
        report.log("OK", "Authenticate", f"resolved server {server}")

    print(f"Server   : {server}\nDatabase : {database}\nMode     : {'read-write' if args.write else 'read-only'}\n")

    now = datetime.now(timezone.utc)
    week = {"fromDate": iso(now - timedelta(days=7)), "toDate": iso(now)}

    check_get(report, server, creds, "User")
    device = check_get(report, server, creds, "Device")
    check_get(report, server, creds, "Zone")
    check_get(report, server, creds, "Group")
    check_get(report, server, creds, "Rule")
    check_get(report, server, creds, "DeviceStatusInfo")
    check_get(report, server, creds, "ExceptionEvent", search=dict(week))

    if device:
        dev_search = {"deviceSearch": {"id": device["id"]}}
        check_get(report, server, creds, "Trip", search={**dev_search, **week})
        check_get(report, server, creds, "LogRecord", search={**dev_search, **week})
        check_get(report, server, creds, "StatusData", search={
            **dev_search, **week, "diagnosticSearch": {"id": "DiagnosticOdometerAdjustmentId"},
        })
    else:
        for t in ("Trip", "LogRecord", "StatusData"):
            report.log("SKIP", f"Get {t}", "no device available to scope the search")

    bad = []
    for diag_id in DOCUMENTED_DIAGNOSTICS:
        try:
            found = call(server, "Get", {"typeName": "Diagnostic", "search": {"id": diag_id}, "credentials": creds})
            if not found:
                bad.append(diag_id)
        except GeotabError:
            bad.append(diag_id)
    if bad:
        report.log("FAIL", "Diagnostics table", f"unknown ids: {', '.join(bad)}")
    else:
        report.log("OK", "Diagnostics table", f"all {len(DOCUMENTED_DIAGNOSTICS)} documented ids exist")

    try:
        addresses = call(server, "GetAddresses", {"coordinates": [{"x": 2.1734, "y": 41.3851}], "credentials": creds})
        if addresses and "formattedAddress" in addresses[0]:
            report.log("OK", "GetAddresses", addresses[0]["formattedAddress"])
        else:
            report.log("WARN", "GetAddresses", "call ok but no formattedAddress in response")
    except GeotabError as e:
        report.log("FAIL", "GetAddresses", str(e))

    try:
        multi = call(server, "ExecuteMultiCall", {"calls": [
            {"method": "Get", "params": {"typeName": "Device", "resultsLimit": 1}},
            {"method": "Get", "params": {"typeName": "User", "resultsLimit": 1}},
        ], "credentials": creds})
        if isinstance(multi, list) and len(multi) == 2:
            report.log("OK", "ExecuteMultiCall", "2 calls, 2 ordered results")
        else:
            report.log("WARN", "ExecuteMultiCall", "unexpected result shape")
    except GeotabError as e:
        report.log("FAIL", "ExecuteMultiCall", str(e))

    try:
        feed = call(server, "GetFeed", {
            "typeName": "LogRecord", "fromVersion": "0000000000000000",
            "resultsLimit": 10, "credentials": creds,
        })
        if "data" in feed and "toVersion" in feed:
            report.log("OK", "GetFeed LogRecord", f"toVersion {feed['toVersion']}")
        else:
            report.log("WARN", "GetFeed LogRecord", "missing data/toVersion in response")
    except GeotabError as e:
        report.log("FAIL", "GetFeed LogRecord", str(e))

    if args.write:
        write_cycle(report, server, creds)

    return report.summary()


if __name__ == "__main__":
    sys.exit(main())
