#!/opt/conda/bin/python3.10
# app/main.py
from fastapi import FastAPI
from app.api.user import router as user_router
from app.api.friend import router as friend_router
from app.api.face import router as face_router

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(user_router)
app.include_router(friend_router)
app.include_router(face_router)