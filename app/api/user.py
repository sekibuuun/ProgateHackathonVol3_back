# app/api/user.py
from fastapi import APIRouter
from app.db import supabase  # db.pyからsupabaseクライアントをインポート

router = APIRouter()

@router.get("/users/{user_id}")
def read_user(user_id: int):
    user = supabase.table("test_user").select("*").eq("user_id", user_id).execute()
    return user.data
