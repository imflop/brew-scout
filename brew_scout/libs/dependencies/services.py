from fastapi import Depends

from redis.asyncio.client import Redis

from .common import get_rds_session
from ..services.kv import KVService
from ..services.runner.retry import RetryService
from ..services.runner.service import CommonRunnerService


async def retry_service_factory() -> RetryService:
    return RetryService()


async def common_runner_service_factory(retry_service: RetryService = Depends(retry_service_factory)) -> CommonRunnerService:
    return CommonRunnerService(retry_service)


async def kv_service_factory(client: Redis = Depends(get_rds_session)) -> KVService:
    return KVService(client)
