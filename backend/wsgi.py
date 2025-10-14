from app.main import app

# This is what Gunicorn will look for
application = app

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

