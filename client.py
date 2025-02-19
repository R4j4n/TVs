import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from routers.group_router import group_router
from routers.tv_routers import router as get_all_pis_router

app = FastAPI()

# Original routers
app.include_router(get_all_pis_router, tags=["Client Router/ Get all PI's in network."])
app.include_router(group_router, prefix="/groups", tags=["Groups"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],  # Ensure OPTIONS is included
    allow_headers=["*"],  # Allow all headers
)


@app.options("/{full_path:path}")
async def preflight_handler():
    return {"message": "CORS preflight successful"}


# Create an HTTP client for forwarding requests
http_client = httpx.AsyncClient()


@app.api_route(
    "/pi/{pi_host}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)
async def proxy_to_pi(request: Request, pi_host: str, path: str):
    """
    Proxy all requests to individual Pis through this endpoint
    """
    # Handle OPTIONS requests for CORS preflight
    if request.method == "OPTIONS":
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Max-Age": "3600",
            },
        )

    try:
        # Construct the target URL
        target_url = f"http://{pi_host}:8000/{path}"

        # Get the request body if it exists
        body = await request.body()

        # Forward the request headers (except host)
        headers = dict(request.headers)
        headers.pop("host", None)

        # Forward the request to the Pi
        response = await http_client.request(
            method=request.method,
            url=target_url,
            content=body,
            headers=headers,
            params=request.query_params,
        )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503, detail=f"Error communicating with Pi: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run("client:app", reload=True, host="0.0.0.0", port=7777)
