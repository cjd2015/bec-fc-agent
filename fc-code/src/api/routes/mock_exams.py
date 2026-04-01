from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_mock_exams():
    return {"code": 0, "message": "success", "data": {"todo": "list_mock_exams"}}


@router.post("/{exam_id}/submit")
def submit_mock_exam(exam_id: int):
    return {"code": 0, "message": "success", "data": {"exam_id": exam_id, "todo": "submit_mock_exam"}}


@router.get("/result/{record_id}")
def get_mock_exam_result(record_id: int):
    return {"code": 0, "message": "success", "data": {"record_id": record_id}}
