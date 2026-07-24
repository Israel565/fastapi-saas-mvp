import httpx, time

BASE = "http://localhost:8000"
EMAIL = f"u{int(time.time())}@test.com"
PASS = "demo1234"
print("using", EMAIL, flush=True)

with httpx.Client(base_url=BASE, timeout=10) as c:
    print("health:", c.get("/health").status_code, flush=True)

    r = c.post("/auth/register", json={"email": EMAIL, "password": PASS})
    print("register:", r.status_code, "token?", "access_token" in r.json(), flush=True)
    token = r.json().get("access_token")

    r = c.post("/auth/login", json={"email": EMAIL, "password": PASS})
    print("login:", r.status_code, "token?", "access_token" in r.json(), flush=True)
    if not token:
        token = r.json().get("access_token")

    if token:
        r = c.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        print("me:", r.status_code, r.json().get("email"), flush=True)

        r = c.post("/api/chat", json={"message": "hi"},
                   headers={"Authorization": f"Bearer {token}"})
        print("chat:", r.status_code, (r.json().get("detail") or r.json().get("reply", ""))[:60], flush=True)

        r = c.post("/billing/checkout", headers={"Authorization": f"Bearer {token}"})
        print("checkout:", r.status_code, (r.json().get("detail") or "")[:60], flush=True)
print("SMOKE DONE", flush=True)
