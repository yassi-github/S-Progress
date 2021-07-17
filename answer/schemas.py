from pydantic import BaseModel


# send script answer用のrequest model。
class ProblemAnswer(BaseModel):
    username: str
    script: str


# result answer. response model.
class ProblemAnswerResult(BaseModel):
    problem_id: int
    username: str
    script: str
    is_correct: bool
    result: str
