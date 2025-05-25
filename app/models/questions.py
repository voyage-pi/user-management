import typing_extensions
from  pydantic import BaseModel
from typing import List,Union
from enum import Enum

class QuestionType(str,Enum):
    SCALE = "scale"
    SELECT = "select"

class AnswerScale(BaseModel):
    value:int 

class AnswerSelect(BaseModel):
    values:List[int|str] # just for 

class Answer(BaseModel):
    question_id:int # this will be the question id 
    answer:Union[AnswerScale,AnswerSelect] # for future question type extensibility

class Preferences(BaseModel):
    answers:List[Answer] 
    name:str

class Question(BaseModel):
    id:int
    question:str
    display:bool
    type:QuestionType
    attributes:str
    description:str
