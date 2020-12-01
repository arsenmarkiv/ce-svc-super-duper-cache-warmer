from src.cachewarmer.app import app

if __name__ == "__main__":
    app.run(threaded=True, debug=True)