import json
from app.models.questions import Answer,AnswerScale,AnswerSelect, Preferences
from typing import List
from app.models.response import ResponseBody
from app.models.user import User
from app.services.supabase_client import supabase, supabase_admin
from fastapi import status




def verify_question(answer:List[Answer]):
    for i in answer:
        try:
            response=supabase.table("question")\
            .select("*")\
            .eq("id",i.question_id)\
            .execute()
            if len(response.data) < 1:
                raise Exception("Question doesn't exist")
        except Exception as e:
            print(f"There is no question with that id {e}")
            return False
    return True

def preferences_json(answers:List[Answer]):
    return [{"question_id":a.question_id,"value":a.answer.value} for a in answers]

def insert_preferences(pref:Preferences,user:User):
    name=pref.name
    answers:List[Answer]= pref.answers
    # for the joins later on
    user_id=user.id
    try:
        # verify existence of questions
        if not verify_question(answers):
            print("Some questions seem to not exist!")
            return ResponseBody({"error":"question don't exist"},"RequestBody invalid",status_code=status.HTTP_400_BAD_REQUEST)

        json_pref=preferences_json(answers)
        supabase_preferences={"user_id":user_id,"preferences_name":name,"question_json_response":json_pref}

        # verify duplications 
        duplicated = supabase.table("preferences") \
        .select("*") \
        .eq("preferences_name",name) \
        .eq("user_id",user_id) \
        .execute()

        # Check if duplicate entry exists
        if duplicated is None or (duplicated.data and len(duplicated.data) > 0):
            return ResponseBody(
                {"id":duplicated.data[0]["id"]},
                "Preferences already added!",
                status_code=status.HTTP_409_CONFLICT
            )

        response=supabase.table("preferences")\
        .insert(supabase_preferences)\
        .execute()
        # add the preferences id to the response 
        return ResponseBody({"id":response.data[0]["id"]},"Preferences saved!",status_code=status.HTTP_200_OK)

    except Exception as e:
        print("Error fetching questions:", e)
        return ResponseBody(
            {"error": f"{e}"},
            "An unexpected error revealed itself!",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def associate_user_preferences_trip(preference_id:int,trip_id:str,user_id:int):
    try:
        pref_check = supabase.table("preferences")\
        .select("id")\
        .eq("id", preference_id)\
        .execute()

        if not pref_check.data:
            return {"error": f"Preference ID {preference_id} does not exist."}

        trip_check = supabase.table("user_trips")\
        .select("id")\
        .eq("trip_id", trip_id)\
        .eq("user_id", user_id)\
        .execute()

        if not trip_check.data:
            return {"error": f"User Trip ID {trip_check} does not exist."}

        duplicate_check = supabase.table("user_preferences")\
        .select("id")\
        .eq("preference_id", preference_id)\
        .eq("user_trips_id", trip_check.data.id)\
        .execute()

        if duplicate_check.data:
            return {"error": "This user preference already exists."}

        insert_response = supabase.table("user_preferences")\
        .insert({
            "preference_id": preference_id,
            "user_trips_id": trip_check.data.id 
        }).execute()

        return {"success": True, "inserted": insert_response.data}
    except Exception as e:
        print("Error fetching questions:", e)
        return ResponseBody(
            {"error": f"{e}"},
            "An unexpected error revealed itself!",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)        

def get_preferences_form(user:User):
    try:
        print("Calling RPC with:", user.id)
        response = supabase.rpc("get_user_preferences_by_trip", {
            "input_user_id": user.id,
            "input_trip_id": None
        }).execute()
        all_preferences_names_ids=[]
        for item in response.data:
            print(item)
            all_preferences_names_ids.append({"preference_id":item.get("preference_id"),"name":item.get("preference_name")}) 
        return ResponseBody({"preferences":all_preferences_names_ids},"Preferences received sucessfully",status_code=status.HTTP_200_OK)
    except Exception as e:
        print("Error fetching questions:", e)
        return ResponseBody(
            {"error": f"{e}"},
            "An unexpected error revealed itself!",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )        
def get_preference_by_id(id:int,user:User):
    try:
        pref_check = supabase.table("preferences")\
        .select("*")\
        .eq("id", id)\
        .eq("user_id", user.id)\
        .execute()
        if not pref_check.data:
            return {"error": f"Preference ID does not exist."}
        questions=pref_check.data[0]["question_json_response"]
        return ResponseBody(
            {"Preferences":{"name":pref_check.data[0]["preferences_name"],"answers":questions}},
            "",
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        print("Error fetching questions:", e)
        return ResponseBody(
            {"error": f"{e}"},
            "An unexpected error revealed itself!",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
def get_all_preferences_for_user(user: User):
    try:
        pref_check = supabase.table("preferences")\
            .select("*")\
            .eq("user_id", user.id)\
            .execute()
        print(pref_check)

        if not pref_check.data:
            return {"error": "No preferences found for this user."}

        # Format all preferences
        preferences_list = [
            {
                "id": pref["id"],
                "name": pref["preferences_name"],
                "answers": pref["question_json_response"]
            }
            for pref in pref_check.data
        ]

        return ResponseBody(
            {"preferences": preferences_list},
            "",
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        print("Error fetching preferences:", e)
        return ResponseBody(
            {"error": f"{e}"},
            "An unexpected error revealed itself!",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



