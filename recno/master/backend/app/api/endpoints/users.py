from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def create_user():
    return {"message": "User creation endpoint"}

@router.delete("/{user_id}")
def delete_user(user_id: int):
    return {"message": f"Deleted user {user_id}"}
