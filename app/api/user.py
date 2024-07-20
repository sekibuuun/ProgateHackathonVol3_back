# app/api/user.py
from fastapi import APIRouter, HTTPException
from app.db import supabase
from app.models import UserUpdate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.app")

router = APIRouter()

@router.get("/users/{user_id}")
def read_user(user_id: int):
    user = supabase.table("test_user").select("*").eq("user_id", user_id).execute()
    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")
    return user.data

@router.patch("/users/{user_id}")
async def update_user(user_id: int, user_update: UserUpdate):
    update_data = user_update.dict(exclude_unset=True)
    logger.info(f"update_data: {update_data}")

    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided to update")

    response = supabase.table("test_user").update(update_data).eq("user_id", user_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")

    return response.data
