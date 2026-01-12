import logging

from fastapi import APIRouter


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/sign-up")
async def sign_up():
    pass