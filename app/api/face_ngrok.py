from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import nest_asyncio
from pyngrok import ngrok
import uvicorn
import face_recognition
from io import BytesIO
import requests
from google.colab import userdata
from supabase import create_client, Client

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

url = userdata.get("SUPABASE_URL")
key = userdata.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# ユーザーIDと顔エンコーディングのペアを保持するクラス
class KnownFace:
    def __init__(self, user_id, face_encoding):
        self.user_id = user_id
        self.face_encoding = face_encoding

# Supabaseからデータを取得する関数
def get_known_faces_data():
    response = supabase.table("test_user").select("user_id, face_img_uri").execute()
    if response.data:
        return [(item["user_id"], item["face_img_uri"]) for item in response.data]
    else:
        raise Exception("Failed to fetch data from Supabase")

@app.post("/detect_faces/{exclude_user_id}")
async def detect_faces_excluding_user(exclude_user_id: int, file: UploadFile = File(...)):
    # Supabaseから既知のユーザーIDと対応する画像URLのリストを取得
    known_faces_data = get_known_faces_data()

    # 既知の顔エンコーディングとそれに対応するユーザーIDのリストを作成
    known_faces = []
    for user_id, image_url in known_faces_data:
        response = requests.get(image_url)
        image = face_recognition.load_image_file(BytesIO(response.content))
        face_encoding = face_recognition.face_encodings(image)[0]
        known_faces.append(KnownFace(user_id=user_id, face_encoding=face_encoding))

    # アップロードされた写真を読み込む
    group_photo = face_recognition.load_image_file(BytesIO(await file.read()))

    # 新しい写真から顔の位置を検出
    face_locations = face_recognition.face_locations(group_photo)

    # 顔が検出されない場合の処理
    if not face_locations:
        return {"message": "顔が検出されませんでした。", "detected_userids": []}

    print(f"{len(face_locations)} 人の顔が検出されました。")

    # 顔エンコーディングを取得
    face_encodings = face_recognition.face_encodings(group_photo, face_locations)

    # 検出されたユーザーIDを保持するリスト
    detected_userids = []

    # 検出された各顔について処理
    for face_encoding in face_encodings:
        # 既知の顔と比較
        matches = face_recognition.compare_faces([face.face_encoding for face in known_faces], face_encoding, tolerance=0.5)

        userid = "unknown"  # デフォルトは "unknown"

        # 一致する顔が見つかった場合
        if True in matches:
            first_match_index = matches.index(True)
            userid = known_faces[first_match_index].user_id

            # 引数のuser_idと一致する場合はスキップ
            if userid == exclude_user_id:
                continue

            detected_userids.append(userid)

    # 検出されたユーザーIDを出力
    return {"detected_userids": detected_userids}

# ngrokの設定
ngrok.set_auth_token(userdata.get("YOUR_NGROK_AUTH_TOKEN"))  # <YOUR_NGROK_AUTH_TOKEN>をあなたのngrok認証トークンに置き換えてください

ngrok_tunnel = ngrok.connect(8000)
print('PUBLIC_URL:', ngrok_tunnel.public_url)

nest_asyncio.apply()
uvicorn.run(app, port=8000)
