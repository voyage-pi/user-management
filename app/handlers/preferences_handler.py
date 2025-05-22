from app.models.questions import Answer,AnswerScale,AnswerSelect, Preferences
from typing import List
from app.services.supabase_client import supabase, supabase_admin





def verify_question(id:int):
    pass

def decompose_answer(answer:Answer):
    pass


def insert_preferences(pref:Preferences):
    name=pref.name
    answers:List[Answer]= pref.answers


