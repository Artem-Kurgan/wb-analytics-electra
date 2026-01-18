from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_dashboard():
    return {"message": "Dashboard route"}
