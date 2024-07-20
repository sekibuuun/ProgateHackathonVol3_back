# app/main.py
from fastapi import FastAPI
from app.api.user import router as user_router

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(user_router)
