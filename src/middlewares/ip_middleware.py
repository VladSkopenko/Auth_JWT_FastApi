from ipaddress import ip_address
from typing import Callable

from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse

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
    """
    The limit_access_by_ip function is a middleware function that limits access to the API by IP address.
    It checks if the client's IP address is in ALLOWED_IPS, and if not, returns a 403 Forbidden response.

    :param request: Request: Get the client's ip address
    :param call_next: Callable: Pass the next function in the pipeline
    :return: A jsonresponse object with a 403 status code and an error message
    :doc-author: Trelent
    """
    ip = ip_address(request.client.host)
    if ip not in ALLOWED_IPS:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Not allowed IP address"},
        )
    response = await call_next(request)
    return response


async def ban_ips(request: Request, call_next: Callable):
    """
    The ban_ips function is a middleware function that checks if the client's IP address
    is in the BANNED_IPS list. If it is, then we return a JSONResponse with status code 403 and
    a detail message explaining why they are banned. Otherwise, we call next(request) to pass
    the request on to the next middleware function or route handler.

    :param request: Request: Access the request object
    :param call_next: Callable: Pass the next function in the chain to be called
    :return: A jsonresponse object if the ip address is banned
    :doc-author: Trelent
    """
    ip = ip_address(request.client.host)
    if ip in BANNED_IPS:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"}
        )
    response = await call_next(request)
    return response
