from fastapi import FastAPI
from app.api.endpoints import subscriptions, users, proxy_keys

app = FastAPI(title="RECNO Master API", version="1.0.0")

app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["Subscriptions"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(proxy_keys.router, prefix="/api/keys", tags=["Proxy Keys"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to RECNO Master API"}
