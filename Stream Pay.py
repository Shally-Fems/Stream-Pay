from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import auth, credentials, firestore
import random, string

app = Flask(__name__)

# Firebase Initialization
cred = credentials.Certificate("path/to/your/firebase/credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# AdMob & Facebook Ads Configuration
ADMOB_REWARDED_AD_ID = "your-admob-id-here"
FACEBOOK_AD_ID = "your-facebook-ad-id-here"

# Generate Unique Referral Link
def generate_referral_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# User Signup/Login
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    nationality = data.get("nationality")
    
    try:
        user = auth.create_user(email=email, password=password)
        referral_code = generate_referral_code()
        
        db.collection("users").document(user.uid).set({
            "email": email,
            "referral_code": referral_code,
            "nationality": nationality,
            "earnings": 0.0
        })
        return jsonify({"message": "User created successfully", "uid": user.uid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    try:
        user = auth.get_user_by_email(email)
        return jsonify({"message": "Login successful", "uid": user.uid}), 200
    except Exception as e:
        return jsonify({"error": "Invalid credentials"}), 401

# Google, Facebook, Apple Login Routes
@app.route('/social-login', methods=['POST'])
def social_login():
    data = request.json
    id_token = data.get("id_token")
    provider = data.get("provider")  # 'google', 'facebook', or 'apple'
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
        user_email = decoded_token.get("email")
        
        user_ref = db.collection("users").document(uid)
        if not user_ref.get().exists:
            referral_code = generate_referral_code()
            user_ref.set({
                "email": user_email,
                "referral_code": referral_code,
                "earnings": 0.0
            })
        
        return jsonify({"message": "Social login successful", "uid": uid}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
