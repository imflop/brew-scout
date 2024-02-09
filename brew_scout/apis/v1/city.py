from collections import abc

from fastapi import APIRouter, Depends

from ...libs.dependencies.services import city_service_factory
from ...libs.services.city import CityService
from ...libs.dal.models.cities import CityModel
from ...libs.serializers.cities import CityOut


router = APIRouter(tags=["Cities"])


@router.get("/cities", response_model=abc.Sequence[CityOut])
async def get_cities(service: CityService = Depends(city_service_factory)) -> abc.Sequence[CityModel]:
    return await service.get_cities()
