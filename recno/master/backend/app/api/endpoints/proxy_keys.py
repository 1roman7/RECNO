from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def create_proxy_key():
    return {"message": "Proxy key creation endpoint"}
