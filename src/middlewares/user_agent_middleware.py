import re
from typing import Callable

from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse

user_agent_ban_list = [r"bot-Yandex", r"Googlebot"]


async def user_agent_ban_middleware(request: Request, call_next: Callable):
    """
    The user_agent_ban_middleware function is a middleware function that checks the user-agent header of an incoming request.
    If the user-agent matches any of the patterns in our ban list, then we return a 403 Forbidden response with a detail message.
    Otherwise, we call next and return whatever response comes back from that.

    :param request: Request: Access the request object
    :param call_next: Callable: Call the next middleware in the chain
    :return: A jsonresponse object with a status code of 403 and a content of {&quot;detail&quot;: &quot;you are banned&quot;}
    :doc-author: Trelent
    """
    user_agent = request.headers.get("user-agent")
    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "You are banned"},
            )
    response = await call_next(request)
    return response
