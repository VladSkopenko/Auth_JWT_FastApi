from fastapi import Request, status
from ipaddress import ip_address
from fastapi.responses import JSONResponse
from typing import Callable

ALLOWED_IPS = [
    ip_address("192.168.1.0"),
    ip_address("172.16.0.0"),
    ip_address("127.0.0.1"),
]
BANNED_IPS = [
    ip_address("190.235.111.156"),
    ip_address("82.220.71.77"),
    ip_address("45.100.28.227"),
]


async def limit_access_by_ip(request: Request, call_next: Callable):
    ip = ip_address(request.client.host)
    if ip not in ALLOWED_IPS:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Not allowed IP address"},
        )
    response = await call_next(request)
    return response


async def ban_ips(request: Request, call_next: Callable):
    ip = ip_address(request.client.host)
    if ip in BANNED_IPS:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"}
        )
    response = await call_next(request)
    return response
