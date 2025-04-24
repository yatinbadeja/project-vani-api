import os

print("🔥 start.py is executing...")

if __name__ == "__main__":
    try:
        import uvicorn
        port = int(os.environ.get("PORT", 8030))
        print(f"🚀 Starting server on port {port}...")
        uvicorn.run("app.main:app", host="0.0.0.0", port=port)
    except Exception as e:
        print(f"❌ Failed to start: {e}")
