from app import app

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",   # local only → fixes Windows policy block
        port=8000           # safe port → rarely blocked
    )
