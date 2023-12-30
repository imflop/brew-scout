import dataclasses as dc
import typing as t
from collections import abc

from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import Nominatim
from geopy.distance import distance, Distance

from brew_scout import MODULE_NAME, VERSION


P = t.ParamSpec("P")


@dc.dataclass(frozen=True, slots=True)
class GeoClient:
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Nominatim:
        return Nominatim(user_agent=self._get_user_agent(), adapter_factory=AioHTTPAdapter)

    @staticmethod
    def calculate_distance(from_coordinates: abc.Sequence[float], to_coordinates: abc.Sequence[float]) -> Distance:
        return distance(from_coordinates, to_coordinates).kilometers

    @staticmethod
    def _get_user_agent() -> str:
        return f"{MODULE_NAME}/{VERSION}"
