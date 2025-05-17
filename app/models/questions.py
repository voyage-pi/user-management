import typing_extensions
from  pydantic import BaseModel
from enum import Enum

class QuestionType(str,Enum):
    SCALE = "scale"
    SELECT = "select"

class Question(BaseModel):
    id:int
    question:str
    display:bool
    type:QuestionType
    attributes:str
    description:str
