from flask import Flask, jsonify
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

app = Flask(__name__)

# MongoDB connection with error handling
try:
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    # Verify connection by sending a ping
    client.admin.command('ping')
    db = client['document']
    print("Successfully connected to MongoDB!")
except ServerSelectionTimeoutError as e:
    print(f"Failed to connect to MongoDB: {e}")
    
@app.route("/db-test")
def test_connection():
    try:
        # Test the connection by listing all collections
        collections = db.list_collection_names()
        return jsonify({
            "status": "success",
            "message": "Connected to MongoDB!",
            "collections": list(collections)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Database error: {str(e)}"
        }), 500

@app.route("/")
def home():
    return "Welcome to the Backend Server!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
