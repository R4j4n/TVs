import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from routers.group_router import group_router
from routers.tv_routers import router as get_all_pis_router

app = FastAPI()
app.include_router(get_all_pis_router, tags=["Clinet Router/ Get all PI's in network."])
app.include_router(group_router, prefix="/groups", tags=["Groups"])

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":

    uvicorn.run("client:app", reload=True, host="0.0.0.0", port=7777)
