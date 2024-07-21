from fastapi import APIRouter, HTTPException
from app.db import supabase
import logging

router = APIRouter()

@router.get("/friends/{user_id}")
def read_friends(user_id: str):
    # まず友達リストを取得
    all_friend_response = []
# フレンドリストのレスポンスを取得
    user_friend_response = supabase.table("friend").select("friend_id").eq("user_id", user_id).execute()
    friend_user_response = supabase.table("friend").select("user_id").eq("friend_id", user_id).execute()

    # レスポンスデータをリストに追加
    all_friend_response = []
    all_friend_response.append(user_friend_response.data)
    all_friend_response.append(friend_user_response.data)

    # フラットなリストに変換する
    friend_user_ids = [item['user_id'] for sublist in all_friend_response for item in sublist]

    logging.getLogger("uvicorn").info(friend_user_ids)

    if not all_friend_response:
        raise HTTPException(status_code=404, detail="Friends not found")
    
    # 友達の user_id に基づいて個別にデータを取得
    friends_data = []
    for friend_user_id in friend_user_ids:
        friend_data_response = supabase.table("users").select("*").eq("id", friend_user_id).execute()
        if friend_data_response.data:
            friends_data.append(friend_data_response.data[0])
        else:
            raise HTTPException(status_code=404, detail=f"Data for friend with id {friend_user_id} not found")

    return friends_data
