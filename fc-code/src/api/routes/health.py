from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {"code": 0, "message": "success", "data": {"status": "ok"}}
