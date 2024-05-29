from fastapi import APIRouter

from . import common, admin, shops, hooks


API_BASE_URL_PREFIX = "/api/v1"


router = APIRouter(prefix=API_BASE_URL_PREFIX)
router.include_router(common.router)
router.include_router(shops.router)
router.include_router(hooks.router)


internal_router = APIRouter()
internal_router.include_router(admin.router)
