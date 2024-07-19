from fastapi import FastAPI
import os
from supabase import create_client, Client

app = FastAPI()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/users/{user_id}")
def read_user(user_id: int):
    user = supabase.table("test_user").select("*").eq("user_id", user_id).execute()
    return user.data
