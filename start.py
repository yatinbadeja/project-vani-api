import os

print("🔥 start.py is executing...")

if __name__ == "__main__":
    try:
        import uvicorn
        port = int(os.environ.get("PORT", 8010))
        print(f"🚀 Starting server on port {port}...")
        uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
    except Exception as e:
        print(f"❌ Failed to start: {e}")
