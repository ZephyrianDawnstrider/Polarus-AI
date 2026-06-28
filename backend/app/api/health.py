from faspiptapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint.
    Used to verify that the backend is running.
    """

    return {
        "status": "healthy",
        "service": "Polarus AI",
        "version": "0.0.1"
    }