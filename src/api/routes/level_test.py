from fastapi import APIRouter

router = APIRouter()


@router.get("/start")
def start_level_test():
    return {"code": 0, "message": "success", "data": {"todo": "start_level_test"}}


@router.post("/submit")
def submit_level_test():
    return {"code": 0, "message": "success", "data": {"todo": "submit_level_test"}}


@router.get("/result/{record_id}")
def get_level_test_result(record_id: int):
    return {"code": 0, "message": "success", "data": {"record_id": record_id}}
