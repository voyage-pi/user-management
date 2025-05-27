from app.services.middleware import require_auth, get_current_user
from app.handlers.preferences_handler import get_all_preferences_for_user, get_preference_by_id, get_preferences_form, insert_preferences, update_preferences
from app.models.questions import Preferences, Answer
from typing import List
from fastapi import APIRouter, Request, status
from app.models.response import ResponseBody
import requests

router = APIRouter(prefix="/preferences", tags=[])

# Create a separate router for trip-related preferences without a prefix
# This will be mounted directly at the application level
trip_preferences_router = APIRouter(tags=["trip-preferences"])

@router.post("/")
@require_auth
async def add_user_preferences(pref: Preferences, request: Request):
    user = get_current_user(request)
    return insert_preferences(pref, user)

@router.get("/")
@require_auth
async def get_user_list_preferences(request: Request):
    user = get_current_user(request)
    return get_preferences_form(user)

@router.get("/{id}")
@require_auth
async def get_pref_id(id: int, request: Request):
    user = get_current_user(request)
    return get_preference_by_id(id, user)

@router.put("/{id}")
@require_auth
async def update_pref_id(id: int, pref: Preferences, request: Request):
    user = get_current_user(request)
    return update_preferences(id, pref.answers, user)

@router.get("/user")
@require_auth
async def get_all_pref_user(request: Request):
    user = get_current_user(request)
    return get_all_preferences_for_user(user)

@trip_preferences_router.put("/preferences/trip/{trip_id}")
@require_auth
async def update_trip_preferences(trip_id: str, preferences_data: dict, request: Request):
    """Update preferences and trigger trip regeneration"""
    try:
        print(f"Trip preferences endpoint called with trip_id: {trip_id}")
        print(f"Request data: {preferences_data}")
        
        user = get_current_user(request)
        print(f"User authenticated: {user}")
        
        # Extract data from request
        preference_id = preferences_data.get("preference_id")
        answers_data = preferences_data.get("answers", [])
        
        print(f"Preference ID: {preference_id}")
        print(f"Answers data: {answers_data}")
        
        if not preference_id:
            print("Missing preference_id in request")
            return ResponseBody(
                {"error": "Preference ID is required"},
                "Preference ID is required",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        # Convert the answers to the expected format
        answers = []
        for answer_data in answers_data:
            # Create Answer objects from the data
            answer = Answer(
                question_id=answer_data["question_id"],
                answer={"value": answer_data["value"]}  # Assuming AnswerScale format
            )
            answers.append(answer)
        
        print(f"Converted answers: {answers}")
        
        # Update preferences using existing handler
        update_result = update_preferences(preference_id, answers, user)
        print(f"Update preferences result: {update_result.status_code}")
        
        # If preferences update failed, return error
        if update_result.status_code != status.HTTP_200_OK:
            print(f"Preferences update failed with status: {update_result.status_code}")
            return update_result
        
        # Forward to trip-management service to regenerate trip
        trip_management_url = "http://trip-management:8080/api/trip/{}/preferences".format(trip_id)
        print(f"Calling trip management service at: {trip_management_url}")
        
        # Get the voyage cookie to forward authentication
        voyage_cookie = request.cookies.get("voyage_at")
        print(f"Found voyage cookie: {voyage_cookie is not None}")
        
        # Forward the request to trip-management service
        try:
            response = requests.put(
                trip_management_url,
                json=preferences_data,
                cookies={"voyage_at": voyage_cookie} if voyage_cookie else None,
                timeout=60
            )
            print(f"Trip management response status: {response.status_code}")
            print(f"Trip management response text: {response.text[:200]}...")
            
            if response.status_code == 200:
                # Return the trip-management response
                return response.json()
            else:
                error_response = {"error": "Failed to regenerate trip"}
                try:
                    if response.text:
                        error_response = response.json()
                except:
                    pass
                
                print(f"Error response: {error_response}")
                return ResponseBody(
                    error_response,
                    "Failed to regenerate trip",
                    status_code=response.status_code,
                )
        except Exception as req_error:
            print(f"Request to trip management failed: {str(req_error)}")
            return ResponseBody(
                {"error": str(req_error)},
                "Error connecting to trip management service",
                status_code=status.HTTP_502_BAD_GATEWAY,
            )
            
    except Exception as e:
        print(f"Error in update_trip_preferences: {str(e)}")
        import traceback
        traceback.print_exc()
        return ResponseBody(
            {"error": str(e)},
            "Error updating trip preferences",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )