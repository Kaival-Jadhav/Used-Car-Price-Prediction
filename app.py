from flask import Flask, request, jsonify
import pickle
import numpy as np
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Flask JWT settings
app.config["JWT_SECRET_KEY"] = "your-secret-key"
jwt = JWTManager(app)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["used_car_price"]
users_collection = db["users"]

# Load trained model
with open("car_price_model.pkl", "rb") as file:
    model = pickle.load(file)

@app.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    if users_collection.find_one({"email": email}):
        return jsonify({"message": "User already exists"}), 400
    
    hashed_password = generate_password_hash(password)
    users_collection.insert_one({"email": email, "password": hashed_password})
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    user = users_collection.find_one({"email": email})
    
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity=email)
    return jsonify({"access_token": access_token})

@app.route("/predict", methods=["POST"])
@jwt_required()
def predict_price():
    data = request.get_json()
    current_user = get_jwt_identity()
    
    # Extract features
    features = np.array([
        data["Year"], data["Present_Price"], data["Kms_Driven"],
        data["Owner"], data["Fuel_Type_Diesel"], data["Fuel_Type_Petrol"],
        data["Seller_Type_Individual"], data["Transmission_Manual"]
    ]).reshape(1, -1)
    
    prediction = model.predict(features)
    return jsonify({"Predicted_Price": round(prediction[0], 2)})
    
@app.route("/user", methods=["GET"])
@jwt_required()
def get_user():
    current_user = get_jwt_identity()
    return jsonify({"email": current_user})

if __name__ == "__main__":
    app.run(debug=True)
