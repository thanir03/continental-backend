from flask import Blueprint, request, jsonify
from src.db import DB
from src.auth.AuthDb import getUserByEmail, insertNewUser, updateAuthMethod
from src.utils import validatePassword, generateJwt, validateEmail
import bcrypt
import jwt
import os

auth_bp = Blueprint("Auth",__name__)

@auth_bp.route("/google-auth", methods=["POST"])
def google_auth():
  data = request.json
  if "email" not in data or "name" not in data:
    return jsonify({"status": False, "message": "Invalid paramaters", "type": "invalid-params"}), 400
  
  email = data["email"]
  name = data["name"]
  
  conn = DB.conn
  cur = conn.cursor()
  userDetails = getUserByEmail(cur, email)
  if userDetails: 
    if userDetails["auth"] == "password":
        # Account exist with same email with password login
        return jsonify({ "status" : False,  "type": "user-account-login-password", "message": "User have already registered using password" }), 409
    del userDetails["password"]
    return jsonify({ "status" : True, "user": userDetails, "accessToken": generateJwt(email, "password") }), 200
  
  insertNewUser(cur, email, name, "oauth_google")
  conn.commit()
  user = getUserByEmail(cur, email)
  del user["password"]
  return jsonify({ "status" : True, "user": user, "accessToken": generateJwt(email, "password") }), 200



@auth_bp.route("/login", methods=["POST"])
def login():
  conn = DB.conn
  data = request.json
  if "email" not in data or "password" not in data:
        return jsonify({"status": False, "message": "Invalid paramaters", "type": "invalid-params"}), 400
  
  email = data["email"]
  password = data["password"]

  cur = conn.cursor()
  res = getUserByEmail(cur, email)
  if not res: 
    return jsonify({"status": False, "message": "Email not found"}), 404
  
  if res["auth"] == "oauth_google":
     return jsonify({"status": False, "message": "Account is registered using Google"}), 409
 
  print(res["password"])
  isValidUser = bcrypt.checkpw(password.encode("utf-8"), res["password"].encode("utf-8"))
  if not isValidUser: return jsonify({"status" : False, "message": "Invalid password" })
  del res["password"]
  return jsonify({"status": True, "accessToken": generateJwt(email, "password"), "user": res}), 200



@auth_bp.route("/register", methods=["POST"])
def register():
  data = request.json # json data 

  if "email" not in data or "password" not in data or "name" not in data:
        return jsonify({"status": False, "message": "Invalid paramaters", "type": "invalid-params"}), 400
  
  name = data["name"]
  email = data["email"]
  password = data["password"]
  
  if not validateEmail(email):
    return jsonify({"status": False, "message": "Invalid email" }), 400

  conn = DB.conn
  cur = conn.cursor()
  res = getUserByEmail(cur, email)
  if res and len(res) > 0:
    if res["auth"] == "oauth_google":
      #  User already registered using google account
       return jsonify({ "status" : False,  "type": "user-account-login-google", "message": "User have already registered using google oauth" }), 409
    return jsonify({"status": False, "message": "User already exist" }), 409
  
  
  if not validatePassword(password): 
    return jsonify({"status": False, "message": "Password doesn't satisfy requirements" }), 400
  hashedPwd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
  insertNewUser(cur, email, name, "password", hashedPwd.decode('utf-8'))
  conn.commit()
  userObject = getUserByEmail(cur, email)

  del userObject["password"]
  return jsonify({"status": True, "accessToken": generateJwt(email, "password"), "user": userObject })


@auth_bp.route("/validate-token", methods=["POST"])
def validate_token():
  data = request.json
  if "access_token" not in data :
        return jsonify({"status": False, "message": "Invalid paramaters", "type": "invalid-params"}), 400
  
  accessToken = data["access_token"]
  try: 
    payload = jwt.decode(accessToken ,os.getenv("JWT_SECRET"),  algorithms="HS256")
  except jwt.ExpiredSignatureError:
    return {"status": False, "message": "Expired Token"} , 401
  except jwt.InvalidTokenError as e:
    print(e)
    return  {"status": False, "message" : "Invalid token"} , 401
  except Exception:
    return  {"status": False, "message": "Unknown Exception"} , 401
  
  conn = DB.conn
  cur = conn.cursor()
  userDetails = getUserByEmail(cur, payload["email"])
  if not userDetails:
    return jsonify({"status": True, "message": "Unknown error occurred"})
  del userDetails["password"]
  return jsonify({"status": True, "user": userDetails}), 200



@auth_bp.route("/convert-auth-method", methods=["POST"])
def convertAuthMethod():
  data = request.json
  if "email" not in data or "name" not in data:
    return jsonify({"status": False, "message": "Invalid paramaters", "type": "invalid-params"}), 400
  email = data["email"] 
  name = data["name"] 

  conn = DB.conn
  cur = conn.cursor()
  res = getUserByEmail(cur, email)
  if not res: 
     return jsonify({"status": False, "message": "Email not found"}), 404

  password = None  
  auth_method = res["auth"]
  if auth_method == "oauth_google":
    if "password" not in data: 
      return jsonify({"status": False, "message": "Password not found", "type": "invalid-params"}), 400
    password = data["password"]
    if not validatePassword(password):
       return jsonify({"status": False, "message": "Password doesn't satisfy requirements" }), 400
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode("utf-8")

  
  updateAuthMethod(cur, email, auth_method, name, password)
  conn.commit()
  return {"status" : True, "message": "Successfully updated auth method"}

