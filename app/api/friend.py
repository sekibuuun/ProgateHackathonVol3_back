from fastapi import APIRouter, HTTPException
from app.db import supabase

router = APIRouter()

@router.get("/friends/{user_id}")
def read_friends(user_id: str):
    # まず友達リストを取得
    friends_response = supabase.table("friend").select("friend_id").eq("user_id", user_id).execute()
    if not friends_response.data:
        raise HTTPException(status_code=404, detail="Friends not found")

    # friend_user_id をリストで取得
    friend_user_ids = [friend["friend_id"] for friend in friends_response.data]

    # 友達の user_id に基づいて個別にデータを取得
    friends_data = []
    for friend_user_id in friend_user_ids:
        friend_data_response = supabase.table("users").select("*").eq("id", friend_user_id).execute()
        if friend_data_response.data:
            friends_data.append(friend_data_response.data[0])
        else:
            raise HTTPException(status_code=404, detail=f"Data for friend with id {friend_user_id} not found")

    return friends_data
