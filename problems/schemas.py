from pydantic import BaseModel


class Problem(BaseModel):
    id: int
    title: str
    text: str
