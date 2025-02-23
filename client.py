import httpx
import uvicorn
from fastapi import FastAPI, File, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from routers.group_router import group_router
from routers.tv_routers import router as get_all_pis_router
from server.src.video_compressor import VideoCompressor

app = FastAPI()

# Original routers
app.include_router(get_all_pis_router, tags=["Client Router/ Get all PI's in network."])
app.include_router(group_router, prefix="/groups", tags=["Groups"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "http://localhost:3000",
    ],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],  # Ensure OPTIONS is included
    allow_headers=["*"],  # Allow all headers
)


@app.options("/{full_path:path}")
async def preflight_handler():
    return {"message": "CORS preflight successful"}


http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(timeout=600.0),  # 10 minutes timeout
    limits=httpx.Limits(
        max_connections=100, max_keepalive_connections=20, keepalive_expiry=60.0
    ),
)


import logging
import os
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

# Initialize video compressor with desired settings
video_compressor = VideoCompressor(target_resolution=240, target_fps=14)


@app.api_route(
    "/pi/{pi_host}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)
async def proxy_to_pi(request: Request, pi_host: str, path: str):
    """
    Proxy all requests to individual Pis through this endpoint
    """
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
        target_url = f"http://{pi_host}:8000/{path}"
        logger.info(f"Proxying request to: {target_url}")

        # Get headers from original request
        headers = dict(request.headers)
        headers.pop("host", None)

        if path == "upload" and request.method == "POST":
            try:
                form = await request.form()
                original_file = form.get("file")
                if not original_file:
                    raise HTTPException(status_code=400, detail="No file provided")

                logger.info(f"Processing file: {original_file.filename}")

                # Use temporary directory for processing
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Save original file
                    temp_input_path = os.path.join(temp_dir, original_file.filename)
                    temp_output_path = os.path.join(
                        temp_dir, f"compressed_{original_file.filename}"
                    )

                    content = await original_file.read()
                    with open(temp_input_path, "wb") as f:
                        f.write(content)

                    logger.info("Starting video compression")
                    compression_success = video_compressor.compress_video(
                        input_path=temp_input_path, output_path=temp_output_path
                    )

                    if not compression_success:
                        raise HTTPException(
                            status_code=500, detail="Video compression failed"
                        )

                    logger.info("Reading compressed file")
                    with open(temp_input_path, "rb") as f:
                        original_content = f.read()
                    with open(temp_output_path, "rb") as f:
                        compressed_content = f.read()

                    logger.info(f"Original size: {len(original_content)} bytes")
                    logger.info(f"Compressed size: {len(compressed_content)} bytes")

                # Remove any existing content-length and content-type headers
                headers.pop("content-length", None)
                headers.pop("content-type", None)
                headers.pop("transfer-encoding", None)

                # Create AsyncClient with specific config for multipart
                async with httpx.AsyncClient(timeout=600.0) as client:
                    # First create the request without sending
                    req = client.build_request(
                        "POST",
                        target_url,
                        files={
                            "original_file": (
                                original_file.filename,
                                original_content,
                                "video/mp4",
                            ),
                            "compressed_file": (
                                f"compressed_{original_file.filename}",
                                compressed_content,
                                "video/mp4",
                            ),
                        },
                        headers=headers,
                    )

                    # Send the prepared request
                    response = await client.send(req)

                    logger.info(f"Pi response status: {response.status_code}")
                    logger.info(f"Pi response: {response.text}")

                    if response.status_code >= 400:
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=f"Pi error: {response.text}",
                        )

                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                )

            except Exception as e:
                logger.error(f"Upload error: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        else:
            # Regular request handling
            body = await request.body()

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
        logger.error(f"Request error: {str(e)}")
        raise HTTPException(
            status_code=503, detail=f"Error communicating with Pi: {str(e)}"
        )
    except Exception as e:
        logger.error(f"General error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("client:app", reload=True, host="0.0.0.0", port=7777)
