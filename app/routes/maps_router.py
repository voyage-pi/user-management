from fastapi import APIRouter

from app.services.google_client import fetch_routes
from app.models.request_models import ComputeRoutesRequest
from app.models.response_models import ComputeRoutesResponse

router = APIRouter(prefix="/maps", tags=["maps"])

@router.post("/", response_model=ComputeRoutesResponse)
async def post_maps(request: ComputeRoutesRequest):
    """
    Fetch routes using the POST method with a JSON request body.
    """
    routes = await fetch_routes(request)
    return ComputeRoutesResponse(routes=routes) 
