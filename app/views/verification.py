from typing import Callable
from fastapi import BackgroundTasks, Depends
from insightscapehub.utils.db import Session, get_db
from app.routers import verify_router
from insightscapehub.dependencies.verification import GetTokenObj, get_or_extend_token_life, get_token_obj
from insightscapehub.schemas.verification import VerificationTokenSafeResponse
import insightscapehub.crud.verification as crud
from insightscapehub.schemas.verification import InitialVerificationInput


@verify_router.get(
    "/{token}/",
    summary="Get Verification Token",
    responses={200: {"model": VerificationTokenSafeResponse}}
)
def get_token(token: str, get_token: GetTokenObj = Depends(get_token_obj)):
    return crud.get_token(token, get_token)


@verify_router.post(
    "/{token}/resend/",
    summary="Resend Verification Token",
    responses={200: {"model": VerificationTokenSafeResponse}}
)
def request_verification(
    token: str,
    tasks: BackgroundTasks,
    get_extend_token: Callable = Depends(get_or_extend_token_life)
):
    return crud.request_verification(token, bg=tasks, get_extend_token=get_extend_token)


@verify_router.post(
    "/{token}/verify/",
    responses={200: {"model": VerificationTokenSafeResponse}}
)
def verify_token(
    token: str,
    data: InitialVerificationInput,
    db: Session = Depends(get_db),
    get_token: GetTokenObj = Depends(get_token_obj)
):
    return crud.verify_token(token, data, db, get_token)
