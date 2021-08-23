from django.core.cache import cache
import requests


class CitiesProxy:
    instance = None

    def load_data(self):
        full_data = cache.get("cities_data", None)
        if full_data is None:
            try:
                response = requests.get("https://api.divar.ir/v8/places/cities",  timeout=1)
                full_data = response.json()
                cache.set("cities_data", full_data, 60 * 60 * 24)
            except requests.ConnectionError:
                full_data = None
            except requests.ReadTimeout:
                full_data = None
        return full_data

    def get_city_name_tuple(self):
        full_data = self.load_data()
        if full_data is None:
            return []
        city_name_tuple = [(city["name"], city["name"]) for city in full_data["cities"]]
        return city_name_tuple

    @staticmethod
    def get_instance():
        if CitiesProxy.instance is None:
            CitiesProxy.instance = CitiesProxy()
        return CitiesProxy.instance
