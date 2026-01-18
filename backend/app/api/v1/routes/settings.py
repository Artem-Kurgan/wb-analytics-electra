from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_settings():
    return {"message": "Settings route"}
