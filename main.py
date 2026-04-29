import uvicorn

if __name__ == "__main__":
    print("Starting server...")
    print("server run in port http://127.0.0.1:18082")
    uvicorn.run(
        "app.api.app:app",
        host="0.0.0.0",
        port=18082,
        reload=True,
    )
