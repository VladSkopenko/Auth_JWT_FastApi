from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status

from src.database.models import Role
from src.database.models import User
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: list[Role]):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance of the class, and defines what attributes it has.
        In this case, we are setting up a Permission object that will have an attribute called allowed_roles.

        :param self: Represent the instance of the class
        :param allowed_roles: list[Role]: Define the allowed roles for a user
        :return: Nothing
        :doc-author: Trelent
        """
        self.allowed_roles = allowed_roles

    async def __call__(
        self, request: Request, user: User = Depends(auth_service.get_current_user)
    ):
        """
        The __call__ function is a decorator that allows us to use the class as a function.
        It takes in two arguments: request and user. The request argument is passed by FastAPI,
        and it contains all of the information about the incoming HTTP request (e.g., headers, body).
        The user argument is passed by our auth_service dependency, which we defined earlier.

        :param self: Access the class attributes
        :param request: Request: Access the request object
        :param user: User: Get the current user, and the request: request parameter is used to access the request object
        :return: A function that takes a request and user as arguments
        :doc-author: Trelent
        """
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            )
