import jwt
from fastapi import Response, status, Request
from src.configurations.settings import settings


def protect_with_token(f):
    async def protector(request: Request, *args, **kwargs):
        try:
            body = await request.json()
            token = body.get("token", None)
            if not token:
                return Response(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content="No token provided")
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            email: str = payload.get("sub")
            if email is None:
                return Response(status_code=status.HTTP_401_UNAUTHORIZED, content="Could not validate email")
        except jwt.PyJWTError:
            return Response(status_code=status.HTTP_401_UNAUTHORIZED, content="Could not validate email")

        return await f(*args, **kwargs)

    import inspect
    protector.__signature__ = inspect.Signature(
        parameters=[
            *inspect.signature(f).parameters.values(),
            
            *filter(
                lambda p: p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD),
                inspect.signature(protector).parameters.values()
            )
        ],
        return_annotation=inspect.signature(f).return_annotation,
    )

    return protector
