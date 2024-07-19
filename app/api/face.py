import face_recognition

# ユーザーIDと顔エンコーディングのペアを保持するクラス
class KnownFace:
    def __init__(self, user_id, face_encoding):
        self.user_id = user_id
        self.face_encoding = face_encoding

def detect_faces_excluding_user(group_photo_path, exclude_user_id):
    # 既知のユーザーIDと対応する画像パスのリスト
    known_faces_data = [
        (1, "A.jpg"),
        (2, "B.jpg")
    ]

    # 既知の顔エンコーディングとそれに対応するユーザーIDのリストを作成
    known_faces = []
    for user_id, image_path in known_faces_data:
        image = face_recognition.load_image_file(image_path)
        face_encoding = face_recognition.face_encodings(image)[0]
        known_faces.append(KnownFace(user_id=user_id, face_encoding=face_encoding))

    # 新しく撮った写真（複数人が写っているもの）を読み込む
    group_photo = face_recognition.load_image_file(group_photo_path)

    # 新しい写真から顔の位置を検出
    face_locations = face_recognition.face_locations(group_photo)

    # 顔が検出されない場合の処理
    if not face_locations:
        print("顔が検出されませんでした。")
        return []

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
    print(f"検出されたユーザーID: {detected_userids}")
    return detected_userids

# グループ写真から特定のユーザーIDを除外して顔を検出
group_photo_path = "C.jpg"
exclude_user_id = 1  # ここで除外したいユーザーIDを指定
detect_faces_excluding_user(group_photo_path, exclude_user_id)
