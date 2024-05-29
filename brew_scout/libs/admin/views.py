from sqladmin import ModelView

from ..dal.models.shops import CoffeeShopModel, CityModel, CountryModel


class CountryModelAdminView(ModelView, model=CountryModel):
    column_list = [
        CountryModel.id,
        CountryModel.name,
        CountryModel.cities,
        CountryModel.created_at,
        CountryModel.updated_at,
    ]
    column_details_list = [
        CountryModel.id,
        CountryModel.name,
        CountryModel.cities,
        CountryModel.created_at,
        CountryModel.updated_at,
    ]
    form_ajax_refs = {
        "cities": {
            "fields": ("id", "name"),
            "order_by": "name",
        }
    }


class CityModelAdminView(ModelView, model=CityModel):
    column_list = [CityModel.id, CityModel.name, CityModel.created_at, CityModel.updated_at, CityModel.country]

    @staticmethod
    def country_format(country: CountryModel) -> str:
        return country.name


class CoffeeShopModelAdminView(ModelView, model=CoffeeShopModel):
    column_list = [CoffeeShopModel.id, CoffeeShopModel.name, CoffeeShopModel.city, CoffeeShopModel.created_at]
    form_ajax_refs = {
        "city": {
            "fields": ("id", "name"),
            "order_by": "id",
        }
    }

    @staticmethod
    def city_format(city: CityModel) -> str:
        return city.name


CityModelAdminView.column_type_formatters.update({CountryModel: CityModelAdminView.country_format})
CoffeeShopModelAdminView.column_type_formatters.update({CityModel: CoffeeShopModelAdminView.city_format})
