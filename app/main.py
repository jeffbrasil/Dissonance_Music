from fastapi import FastAPI

from app.api.endpoints import user_router, playlist_router, track_router
app = FastAPI()


app.include_router(user_router.router, prefix="/users", tags=["Usuario"])
app.include_router(playlist_router.router, prefix="/playlists", tags=["Playlists"])
app.include_router(track_router.router, prefix="/tracks", tags=["Tracks"])
