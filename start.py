import os

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8030))
    print(f"Starting server on port {port}...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)