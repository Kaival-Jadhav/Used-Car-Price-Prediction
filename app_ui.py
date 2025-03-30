import streamlit as st
import requests

API_URL = "http://127.0.0.1:5000/predict"
LOGIN_URL = "http://127.0.0.1:5000/login"
REGISTER_URL = "http://127.0.0.1:5000/register"

st.title("🚗 Used Car Price Prediction")

def login():
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")
    
    if login_button:
        response = requests.post(LOGIN_URL, json={"email": email, "password": password})
        if response.status_code == 200:
            st.session_state.token = response.json()["access_token"]
            st.success("Login Successful")
        else:
            st.error("Login failed. Invalid credentials.")

def register():
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    register_button = st.button("Register")
    
    if register_button:
        response = requests.post(REGISTER_URL, json={"email": email, "password": password})
        if response.status_code == 201:
            st.success("User Registered Successfully")
        else:
            st.error("User registration failed")

if "token" not in st.session_state:
    option = st.radio("Select option", ("Login", "Register"))
    if option == "Login":
        login()
    elif option == "Register":
        register()
else:
    st.write(f"Welcome, {st.session_state.token}")

    year = st.number_input("Year of Purchase", 2000, 2025, 2015)
    present_price = st.number_input("Showroom Price (in lakhs)", 0.0, 50.0, 5.5)
    kms_driven = st.number_input("Kilometers Driven", 0, 300000, 30000)
    owner = st.selectbox("Previous Owners", [0, 1, 2, 3])
    fuel_type = st.selectbox("Fuel Type", ["Petrol", "Diesel", "CNG"])
    seller_type = st.selectbox("Seller Type", ["Dealer", "Individual"])
    transmission = st.selectbox("Transmission", ["Manual", "Automatic"])

    fuel_type_diesel = 1 if fuel_type == "Diesel" else 0
    fuel_type_petrol = 1 if fuel_type == "Petrol" else 0
    seller_type_individual = 1 if seller_type == "Individual" else 0
    transmission_manual = 1 if transmission == "Manual" else 0

    if st.button("Predict Price"):
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        data = {
            "Year": year,
            "Present_Price": present_price,
            "Kms_Driven": kms_driven,
            "Owner": owner,
            "Fuel_Type_Diesel": fuel_type_diesel,
            "Fuel_Type_Petrol": fuel_type_petrol,
            "Seller_Type_Individual": seller_type_individual,
            "Transmission_Manual": transmission_manual
        }
        
        response = requests.post(API_URL, json=data, headers=headers)
        
        if response.status_code == 200:
            predicted_price = response.json().get("Predicted_Price", "Error")
            st.success(f"💰 Estimated Car Price: ₹{predicted_price} lakhs")
        else:
            st.error("Error in API request. Please check the server.")
