from collections import abc

from fastapi import APIRouter, Depends

from ...libs.dependencies.common import resource_provider_factory
from ...libs.managers import ResourceProvider
from ...libs.serializers.shops import CoffeeShopsOut
from ...libs.dal.models.shops import CoffeeShopModel


router = APIRouter(tags=["Coffee Shops"])


@router.get("/shops", response_model=abc.Sequence[CoffeeShopsOut])
async def get_shops(rp: ResourceProvider = Depends(resource_provider_factory)) -> abc.Sequence[CoffeeShopModel]:
    return await rp.coffee_shop_service.get_coffee_shops()
