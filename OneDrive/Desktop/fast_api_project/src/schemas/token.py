from pydantic import BaseModel

__all__ = ["IncomingData"]


class IncomingData(BaseModel):
    email: str
    password: str
