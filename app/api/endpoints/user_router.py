from http import HTTPStatus

from fastapi import APIRouter

from app.schemas.user_schema import UserCreate, UserResponse

router = APIRouter()


@router.post("/criar-usuario", response_model=UserResponse, status_code=HTTPStatus.CREATED)
def create_usuario(user: UserCreate):

    return user
