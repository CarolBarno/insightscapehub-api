from redis import Redis

_existing = dict()


def get_client() -> Redis:
    if _existing.get("client", None):
        return _existing["client"]
    from insightscapehub.utils import settings

    redis_password = settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None

    client: Redis = Redis(
        settings.REDIS_HOST,
        settings.REDIS_PORT,
        password=redis_password,
        db=0 if settings.IS_TESTING else 1,
    )

    _existing["client"] = client

    return client
