from typing import List, Dict
import httpx
from fastapi import HTTPException
from app.services.supabase_client import supabase
from datetime import datetime

TRIP_MANAGEMENT_URL = "http://trip-management:8080"

async def get_user_trip_stats(user_id: str):
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

        if not trip_ids:
            return {"message": "No trips found for this user", "data": {
                "total_trips": 0,
                "countries_visited": 0,
                "cities_visited": 0,
                "total_days": 0
            }}

        # Get trip details from trip-management service
        stats = {
            "total_trips": len(trip_ids),
            "countries_visited": set(),
            "cities_visited": set(),
            "total_days": 0
        }

        async with httpx.AsyncClient() as client:
            for trip_id in trip_ids:
                response = await client.get(f"{TRIP_MANAGEMENT_URL}/api/trips/{trip_id}")
                if response.status_code == 200:
                    trip_data = response.json()
                    itinerary = trip_data.get("response", {}).get("itinerary", {})
                    
                    # Add country and city from itinerary level
                    if "country" in itinerary:
                        print(itinerary["country"])
                        stats["countries_visited"].add(itinerary["country"])
                    if "city" in itinerary:
                        print(itinerary["city"])
                        stats["cities_visited"].add(itinerary["city"])
                    
                    # Count days based on the days array length
                    if "days" in itinerary:
                        stats["total_days"] += len(itinerary["days"])
                        print(stats["total_days"])
        # Convert sets to counts
        stats["countries_visited"] = len(stats["countries_visited"])
        stats["cities_visited"] = len(stats["cities_visited"])

        return {"message": "Trip statistics retrieved successfully", "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

async def get_shared_trips(user_id: str, other_user_id: str):
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

async def get_last_shared_trip(user_id: str, other_user_id: str):
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
            trip_details = await get_trip_details(trip_id)
            shared_trips.append(trip_details)

        if not shared_trips:
            return {"message": "No trip details found", "data": None}
        
        # Sort by start date and get the most recent
        last_trip = sorted(shared_trips, key=lambda x: x.get("data", {}).get("start_date", ""), reverse=True)[0]
        return {"message": "Last shared trip retrieved successfully", "data": last_trip}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_trip_details(trip_id: str):
    """
    Get detailed information for a specific trip
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{TRIP_MANAGEMENT_URL}/api/trips/{trip_id}")
            if response.status_code == 200:
                trip_data = response.json()
                return {"message": "Trip details retrieved successfully", "data": trip_data.get("response", {}).get("itinerary", {})}
            else:
                raise HTTPException(status_code=404, detail="Trip not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 