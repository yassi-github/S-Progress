from pydantic import BaseModel


class MyProblem(BaseModel):
    id: int
    title: str
    text: str
