
from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter
import nest_asyncio
import uvicorn
import face_recognition
from io import BytesIO
import requests
import os
from supabase import create_client, Client
from app.db import supabase
import numpy as np
from PIL import Image
import logging

router = APIRouter()

# Simple cache for image URLs and their corresponding face encodings
image_cache = {}

class KnownFace:
    def __init__(self, id: str, face_encoding: np.ndarray):
        self.id = id
        self.face_encoding = face_encoding

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
        if image_url in image_cache:
            face_encodings = image_cache[image_url]
        else:
            response = requests.get(image_url)
            image = face_recognition.load_image_file(BytesIO(response.content))
            image = Image.fromarray(image)
            face_encodings = []
            for angle in range(0, 360, 90):
                rotated_image = np.array(image.rotate(angle))
                encodings = face_recognition.face_encodings(rotated_image)
                if len(encodings) == 0:
                    continue
                face_encoding = encodings[0]
                face_encodings.append(face_encoding)
                break
            image_cache[image_url] = face_encodings
        
        for face_encoding in face_encodings:
            known_faces.append(KnownFace(id=id, face_encoding=face_encoding))

    # アップロードされた写真を読み込む
    group_photo = face_recognition.load_image_file(BytesIO(await file.read()))

    # 顔エンコーディングを取得
    face_locations = face_recognition.face_locations(group_photo)
    face_encodings = face_recognition.face_encodings(group_photo, face_locations)
    if len(face_encodings) == 0:
        raise HTTPException(status_code=401, detail="No faces found in the uploaded image")
    elif len(face_encodings) == 1:
        raise HTTPException(status_code=401, detail="At least two people must be in the image")

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
        supabase.table("friend").insert({"user_id": exclude_user_id, "friend_id": friend_user_id}).execute()
        
        friend_data_response = supabase.table("users").select("*").eq("id", friend_user_id).execute()
        if friend_data_response.data:
            friends_data.append(friend_data_response.data[0])
        else:
            raise HTTPException(status_code=404, detail=f"Data for friend with id {friend_user_id} not found")

    return friends_data
