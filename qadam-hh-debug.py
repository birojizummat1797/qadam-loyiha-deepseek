# -*- coding: utf-8 -*-
"""HH.uz API debug — nima ishlamayapti?"""
import httpx
import json


def test_url(url, params=None, headers=None):
    print(f"\n{'=' * 60}")
    print(f"URL: {url}")
    if params:
        print(f"Params: {params}")
    print('=' * 60)

    try:
        with httpx.Client(timeout=30) as client:
            r = client.get(url, params=params, headers=headers or {})
            print(f"Status: {r.status_code}")
            print(f"Content-Type: {r.headers.get('content-type', '?')}")

            try:
                data = r.json()
                if isinstance(data, dict):
                    print(f"Keys: {list(data.keys())[:10]}")
                    if "items" in data:
                        print(f"Items count: {len(data['items'])}")
                        if data["items"]:
                            first = data["items"][0]
                            print(f"First item keys: {list(first.keys())[:10]}")
                            print(f"First item name: {first.get('name', '?')[:80]}")
                            print(f"First item salary: {first.get('salary')}")
                    if "errors" in data:
                        print(f"ERRORS: {data['errors']}")
                else:
                    print(f"Data: {str(data)[:500]}")
            except Exception as e:
                print(f"JSON parse error: {e}")
                print(f"Raw: {r.text[:500]}")
    except Exception as e:
        print(f"Connection error: {e}")


# Test 1: asosiy HH.uz API
test_url("https://api.hh.uz/vacancies", params={"text": "frontend", "per_page": 5})

# Test 2: HH.ru API (asosiy)
test_url("https://api.hh.ru/vacancies", params={"text": "frontend", "area": 97, "per_page": 5})

# Test 3: HH.uz other endpoint
test_url("https://hh.uz/api/vacancies", params={"text": "frontend"})

# Test 4: User-Agent bilan
test_url(
    "https://api.hh.ru/vacancies",
    params={"text": "frontend", "area": 97, "per_page": 5},
    headers={"User-Agent": "Qadam.io/1.0 (info@qadam.io)"},
)

print()
print("=" * 60)
print("DEBUG TUGADI")
print("=" * 60)