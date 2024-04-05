import re
from typing import Callable

from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse

user_agent_ban_list = [r"bot-Yandex", r"Googlebot"]


async def user_agent_ban_middleware(request: Request, call_next: Callable):
    user_agent = request.headers.get("user-agent")
    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "You are banned"},
            )
    response = await call_next(request)
    return response
