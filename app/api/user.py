# app/api/user.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import supabase
from app.models import UserUpdate

router = APIRouter()

@router.get("/users/{user_id}")
def read_user(user_id: int):
    user = supabase.table("test_user").select("*").eq("user_id", user_id).execute()
    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")
    return user.data

@router.patch("/users/{user_id}")
def update_user(user_id: int, user_update: UserUpdate):
    response = supabase.table("test_user").update(user_update.dict()).eq("user_id", user_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")
    return response.data
