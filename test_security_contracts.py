#!/usr/bin/env python3
# test_security_contracts.py
# Minimal integration tests for security/contracts (run against local server)

import os
import sys
import requests


API_URL = os.getenv("API_URL", "http://localhost:5050")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")


def must(condition: bool, msg: str):
    if not condition:
        raise AssertionError(msg)


def main() -> int:
    print("=" * 60)
    print("Security & Contract Tests (integration)")
    print("=" * 60)

    # 1) Members list must be {data, meta}
    r = requests.get(f"{API_URL}/members")
    must(r.status_code == 200, f"GET /members expected 200, got {r.status_code}: {r.text}")
    payload = r.json()
    must(isinstance(payload, dict), "GET /members must return object")
    must("data" in payload and isinstance(payload["data"], list), "GET /members must return {data: []}")
    must("meta" in payload and isinstance(payload["meta"], dict), "GET /members must return {meta: {...}}")

    # 2) Visitors list must be {data, meta}
    r = requests.get(f"{API_URL}/visitors")
    must(r.status_code == 200, f"GET /visitors expected 200, got {r.status_code}: {r.text}")
    payload = r.json()
    must(isinstance(payload, dict), "GET /visitors must return object")
    must("data" in payload and isinstance(payload["data"], list), "GET /visitors must return {data: []}")
    must("meta" in payload and isinstance(payload["meta"], dict), "GET /visitors must return {meta: {...}}")

    # 3) Write endpoints must require X-Admin-Token
    r = requests.post(f"{API_URL}/members", json={"name": "token_test_user"})
    must(r.status_code in (401, 403), f"POST /members without token must be 401/403, got {r.status_code}: {r.text}")

    # 4) Check-in should still work without token
    r = requests.post(f"{API_URL}/attendance", json={"date": "2026-04-10", "name": "public_checkin_user"})
    must(r.status_code in (200, 201, 409), f"POST /attendance without token should be allowed, got {r.status_code}: {r.text}")

    if not ADMIN_TOKEN:
        print("ADMIN_TOKEN not set in environment; skipping authorized write checks.")
        print("✅ Passed (partial)")
        return 0

    headers = {"X-Admin-Token": ADMIN_TOKEN}
    r = requests.post(
        f"{API_URL}/members",
        json={"name": "token_test_user_ok", "phone": "0912345678", "group": "測試"},
        headers=headers,
    )
    must(r.status_code in (200, 201, 409), f"POST /members with token expected 200/201/409, got {r.status_code}: {r.text}")

    print("✅ Passed")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"❌ Failed: {e}")
        sys.exit(1)

