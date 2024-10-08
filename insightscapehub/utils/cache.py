import functools
import json
from .redis import get_client
from datetime import timedelta
from insightscapehub.utils.settings import CACHE_DATA_EXPIRE_MINUTES
from uuid import UUID


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        return super().default(obj)


class DynamicCache:
    def __init__(self):
        self.cache = get_client()
        self.client_available = self.check_client_availability()

    def check_client_availability(self):
        try:
            self.cache.ping()
            return True
        except Exception as e:
            print(f"Cache client is not available: {e}")
            return False

    def cache_key(self, model, query, condition):
        return f"{self.get_model_name(model)}_{query}_{condition}"

    def get(self, key):
        if not self.client_available or key is None:
            return None
        cached_data = self.cache.get(key)
        if cached_data is not None:
            return json.loads(cached_data)
        return None

    def set(
        self, key, data, cache_data_expire_minutes: int = CACHE_DATA_EXPIRE_MINUTES
    ):
        """
        Set a value in the cache with the specified key and data.

        Parameters:
            key (str): The key to identify the data in the cache.
            data (object): The data to be cached.
            cache_data_expire_minutes (int): The expiration time for the cached data in minutes.
                Defaults to CACHE_DATA_EXPIRE_MINUTES if not provided.

        Raises:
            Exception: If there is an error during the caching process.

        Note:
            This function uses JSON serialization and a custom encoder to store the data in the cache.
        """
        if not self.client_available or key is None:
            return
        try:
            serialized_data = json.dumps(data, cls=CustomEncoder)
            self.cache.setex(
                key, timedelta(
                    minutes=cache_data_expire_minutes), serialized_data
            )
        except Exception as e:
            print("Set cache error", e)

    def clear(self, model):
        if not self.client_available:
            return
        model_name = self.get_model_name(model)

        model_name_bytes = model_name.encode("utf-8")

        # Use a list comprehension to filter keys that start with the encoded model_name
        keys_to_remove = [
            key for key in self.cache.keys() if key.startswith(model_name_bytes)
        ]

        for key in keys_to_remove:
            self.cache.delete(key)

    def clear_key(self, key):
        if not self.client_available or key is None:
            return
        self.cache.delete(key)

    def cached(self, func):
        @functools.wraps(func)
        def wrapper(model, db, query={}, condition={}, schema=None):
            if not self.client_available:
                return func(model, db, query, condition, schema)
            cache_key = self.cache_key(model, str(query), str(condition))
            cached_data = self.get(cache_key)
            if cached_data:
                return cached_data
            else:
                data = func(model, db, query, condition, schema)
                self.set(cache_key, data)
                return data

        return wrapper

    def get_model_name(self, model):
        """
        This function will return a model
        """
        model_name = ""
        if isinstance(model, list):
            for _model in model:
                model_name += _model["model"].__name__
        else:
            model_name = model.__name__
        return model_name


cache = DynamicCache()
