from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 10000, interval: int = 60):
        super().__init__(app)
        self.limit = int(limit)
        self.interval = int(interval)
        self.rate_limits = {}

    async def dispatch(self, request: Request, call_next):
        remote_address = request.client.host
        now = int(time.time())

        if self.is_rate_limited(remote_address, now):
            return Response("Too Many Requests", status_code=429)

        self.increment_request_count(remote_address, now)

        response = await call_next(request)

        return response

    def is_rate_limited(self, remote_address: str, now: int) -> bool:
        key = f"{remote_address}:{now // self.interval}"
        request_count = self.rate_limits.get(key, 0)
        return request_count > self.limit

    def increment_request_count(self, remote_address: str, now: int):
        key = f"{remote_address}:{now // self.interval}"
        request_count = self.rate_limits.get(key, 0)
        self.rate_limits[key] = request_count + 1
