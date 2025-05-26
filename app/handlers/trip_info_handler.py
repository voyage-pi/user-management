from typing import List, Dict
import httpx
from fastapi import HTTPException
from app.services.supabase_client import supabase
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TRIP_MANAGEMENT_URL = "http://trip-management:8080"

async def get_user_trip_stats(user_id: str, auth_token: str = None):
    """
    Get trip statistics for a user including:
    - Number of trips
    - Number of countries visited
    - Number of cities visited
    - Number of days traveled
    """
    try:
        # Get all trip IDs for the user from Supabase
        response = supabase.table('user_trips').select('trip_id').eq('user_id', user_id).neq('status', 'pending').execute()
        trip_ids = [record['trip_id'] for record in response.data]
        
        logger.info(f"Found {len(trip_ids)} trips for user {user_id}")

        if not trip_ids:
            return {"message": "No trips found for this user", "data": {
                "total_trips": 0,
                "countries_visited": 0,
                "cities_visited": 0,
                "total_days": 0,
                "saved": 0
            }}

        # Get trip details from trip-management service
        stats = {
            "total_trips": len(trip_ids),
            "countries_visited": set(),
            "cities_visited": set(),
            "total_days": 0,
            "saved": 0
        }

        # Prepare headers with auth token if available
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if auth_token:
            # Try different authorization header formats
            headers["Authorization"] = f"Bearer {auth_token}"
            # Also set cookie to mimic browser behavior
            cookies = {"voyage_at": auth_token}
            logger.info(f"Using auth token: {auth_token[:10]}... (first 10 chars)")
            logger.info(f"Headers: {headers}")
        else:
            logger.warning("No auth token provided for trip-management API calls")
            cookies = {}

        async with httpx.AsyncClient() as client:
            for trip_id in trip_ids:
                try:
                    logger.info(f"Requesting trip details for trip_id: {trip_id}")
                    response = await client.get(
                        f"{TRIP_MANAGEMENT_URL}/api/trips/{trip_id}", 
                        headers=headers,
                        cookies=cookies,
                        timeout=10.0
                    )
                    
                    logger.info(f"Trip API response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        trip_data = response.json()
                        itinerary = trip_data.get("response", {}).get("itinerary", {})
                        
                        # Add country and city from itinerary level
                        if "country" in itinerary:
                            logger.info(f"Country: {itinerary['country']}")
                            stats["countries_visited"].add(itinerary["country"])
                        if "city" in itinerary:
                            logger.info(f"City: {itinerary['city']}")
                            stats["cities_visited"].add(itinerary["city"])
                        
                        # Count days based on the days array length
                        if "days" in itinerary:
                            stats["total_days"] += len(itinerary["days"])
                            logger.info(f"Total days: {stats['total_days']}")
                    else:
                        logger.error(f"Failed to get trip {trip_id}. Status: {response.status_code}, Response: {response.text}")
                except Exception as e:
                    logger.error(f"Error getting trip {trip_id}: {str(e)}")

        # Convert sets to counts
        stats["countries_visited"] = len(stats["countries_visited"])
        stats["cities_visited"] = len(stats["cities_visited"])
        stats["saved"] = len(supabase.table('user_places').select('place_id').eq('user_id', user_id).execute().data)

        logger.info(f"Final stats: {stats}")
        return {"message": "Trip statistics retrieved successfully", "data": stats}
    except Exception as e:
        logger.error(f"Error in get_user_trip_stats: {str(e)}")
        # Return default stats instead of failing
        return {"message": f"Error retrieving trip statistics: {str(e)}", "data": {
            "total_trips": len(trip_ids) if 'trip_ids' in locals() else 0,
            "countries_visited": 0,
            "cities_visited": 0,
            "total_days": 0,
            "saved": 0
        }}

async def get_user_trips(user_id: str):
    """
    Get all trip IDs for a user
    """
    try:
        response = supabase.table('user_trips').select('trip_id').eq('user_id', user_id).neq('status', 'pending').execute()
        trip_ids = [record['trip_id'] for record in response.data]
        return {"message": "Trip IDs retrieved successfully", "data": {"trip_ids": trip_ids}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_shared_trips(user_id: str, other_user_id: str, auth_token: str = None):
    """
    Get all trips that are shared between user_id and other_user_id (i.e., both are participants in the same trip)
    """
    try:
        # Get all trip IDs for user_id
        user1_trips = supabase.table('user_trips').select('trip_id').eq('user_id', user_id).execute()
        user1_trip_ids = set(record['trip_id'] for record in user1_trips.data)

        # Get all trip IDs for other_user_id
        user2_trips = supabase.table('user_trips').select('trip_id').eq('user_id', other_user_id).execute()
        user2_trip_ids = set(record['trip_id'] for record in user2_trips.data)

        # Find common tripsz
        shared_trip_ids = user1_trip_ids.intersection(user2_trip_ids)

        return {"message": "Shared trips retrieved successfully", "data": {"shared_trips_ids": shared_trip_ids}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_last_shared_trip(user_id: str, other_user_id: str, auth_token: str = None):
    """
    Get details of the last trip between two users
    """
    try:
        # Get trips shared between both users
        user1_trips = supabase.table('user_trips').select('trip_id').eq('user_id', user_id).execute()
        user1_trip_ids = set(record['trip_id'] for record in user1_trips.data)
        
        user2_trips = supabase.table('user_trips').select('trip_id').eq('user_id', other_user_id).execute()
        user2_trip_ids = set(record['trip_id'] for record in user2_trips.data)
        
        # Find common trips
        shared_trip_ids = user1_trip_ids.intersection(user2_trip_ids)
        
        if not shared_trip_ids:
            return {"message": "No shared trips found between these users", "data": None}
            
        # Get details of all shared trips from trip-management to find the most recent
        shared_trips = []
        for trip_id in shared_trip_ids:
            trip_details = await get_trip_details(trip_id, auth_token)
            shared_trips.append(trip_details)

        if not shared_trips:
            return {"message": "No trip details found", "data": None}
        
        # Sort by start date and get the most recent
        last_trip = sorted(shared_trips, key=lambda x: x.get("data", {}).get("start_date", ""), reverse=True)[0]
        return {"message": "Last shared trip retrieved successfully", "data": last_trip}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_trip_details(trip_id: str, auth_token: str = None):
    """
    Get detailed information for a specific trip
    """
    try:
        # Prepare headers with auth token if available
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
            cookies = {"voyage_at": auth_token}
            logger.info(f"Using auth token for trip details: {auth_token[:10]}... (first 10 chars)")
        else:
            logger.warning(f"No auth token provided for get_trip_details({trip_id})")
            cookies = {}
            
        async with httpx.AsyncClient() as client:
            logger.info(f"Requesting details for trip: {trip_id}")
            response = await client.get(
                f"{TRIP_MANAGEMENT_URL}/api/trips/{trip_id}", 
                headers=headers,
                cookies=cookies,
                timeout=10.0
            )
            
            logger.info(f"Trip details response status: {response.status_code}")
            
            if response.status_code == 200:
                trip_data = response.json()
                return {"message": "Trip details retrieved successfully", "data": trip_data.get("response", {}).get("itinerary", {})}
            else:
                logger.error(f"Failed to get trip details for {trip_id}. Status: {response.status_code}, Response: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=f"Trip not found: {response.text}")
    except Exception as e:
        logger.error(f"Error in get_trip_details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))