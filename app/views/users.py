from app.routers import auth_router

@auth_router.get('/')
async def read_root():
    return {"message": "hello world"}