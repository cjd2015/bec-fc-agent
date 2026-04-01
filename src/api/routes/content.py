from fastapi import APIRouter

router = APIRouter()


@router.post("/import")
def import_content():
    return {"code": 0, "message": "success", "data": {"todo": "import_content"}}
