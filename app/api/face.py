from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter
import nest_asyncio
import uvicorn
import face_recognition
from io import BytesIO
import requests
import os
from supabase import create_client, Client
from app.db import supabase

router = APIRouter()

# ユーザーIDと顔エンコーディングのペアを保持するクラス
class KnownFace:
    def __init__(self, id, face_encoding):
        self.id = id
        self.face_encoding = face_encoding

# Supabaseからデータを取得する関数
def get_known_faces_data():
    response = supabase.table("users").select("id, face_img_uri").execute()
    if response.data:
        return [(item["id"], item["face_img_uri"]) for item in response.data]
    else:
        raise Exception("Failed to fetch data from Supabase")

@router.post("/detect_faces/{exclude_user_id}")
async def detect_faces_excluding_user(exclude_user_id: str, file: UploadFile = File(...)):
    # Supabaseから既知のユーザーIDと対応する画像URLのリストを取得
    known_faces_data = get_known_faces_data()

    # 既知の顔エンコーディングとそれに対応するユーザーIDのリストを作成
    known_faces = []
    for id, image_url in known_faces_data:
        response = requests.get(image_url)
        image = face_recognition.load_image_file(BytesIO(response.content))
        face_encoding = face_recognition.face_encodings(image)[0]
        known_faces.append(KnownFace(id=id, face_encoding=face_encoding))

    # アップロードされた写真を読み込む
    group_photo = face_recognition.load_image_file(BytesIO(await file.read()))

    # 新しい写真から顔の位置を検出
    face_locations = face_recognition.face_locations(group_photo)

    # 顔が検出されない場合の処理
    if not face_locations:
        raise HTTPException(status_code=401, detail="No faces found in the uploaded image")

    # 顔エンコーディングを取得
    face_encodings = face_recognition.face_encodings(group_photo, face_locations)

    # 検出されたユーザーIDを保持するリスト
    detected_ids = []

    # 検出された各顔について処理
    for face_encoding in face_encodings:
        # 既知の顔と比較
        matches = face_recognition.compare_faces([face.face_encoding for face in known_faces], face_encoding, tolerance=0.4)

        id = "unknown"  # デフォルトは "unknown"

        # 一致する顔が見つかった場合
        if True in matches:
            first_match_index = matches.index(True)
            id = known_faces[first_match_index].id

            # 引数のuser_idと一致する場合はスキップ
            if id == exclude_user_id:
                continue

            detected_ids.append(id)

    # 検出されたユーザーIDを出力
    # return {"detected_ids": detected_ids}

    friends_data = []
    for friend_user_id in detected_ids:
        friend_data_response = supabase.table("users").select("*").eq("id", friend_user_id).execute()
        if friend_data_response.data:
            friends_data.append(friend_data_response.data[0])
        else:
            raise HTTPException(status_code=404, detail=f"Data for friend with id {friend_user_id} not found")

    return friends_data
