from datetime import datetime, timedelta, timezone
import jwt
import os
import re

def validatePassword(password: str): 
  password = password.strip()
  hasLowerCase, hasUpperCase, hasDigit, hasSpecialCharacter, satisfyMinLength = False, False, False, False, False

  satisfyMinLength = len(password) > 4

  for char in password:
    if char.islower():
      hasLowerCase = True
    if char.isupper():
      hasUpperCase = True
    if char.isdigit():
      hasDigit = True
    if char in ['@', '$','!','%', '*', '?', '&', '/']:
      hasSpecialCharacter = True

  return hasUpperCase and hasLowerCase and hasDigit and hasSpecialCharacter and satisfyMinLength 


def validateEmail(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


def generateJwt(email:str, auth_type: str):
  expirationTime = datetime.now(tz=timezone.utc) + timedelta(days=30)
  payload = {"email": email, "auth_type": auth_type, "type": "access_token", "exp": expirationTime}
  token = jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")
  return token

def validateJWT(accessToken : str):
  try: 
    payload = jwt.decode(accessToken ,os.getenv("JWT_SECRET"),  algorithms="HS256")
    return {"status": True, "payload" : payload}
  except jwt.ExpiredSignatureError:
    return {"status": False, "message": "Expired Token"}
  except jwt.InvalidTokenError as e:
    return  {"status": False, "message" : "Invalid token"}
  except Exception:
    return  {"status": False, "message": "Unknown Exception"}

def capitilize_str(s:str):
  return s.capitalize().strip()


def loginEndpointMiddleware(cur, request):
  auth = request.headers.get("Authorization")
  if not auth:
      return {"status": False, "message": "Authorization header not provided", "type": "not-logged-in"}
  authTokenized = auth.split(" ")

  if len(authTokenized) == 1 or len(authTokenized) == 0:
      return {"status": False, "message": "Invalid Authorization heaeder provided", "type": "not-logged-in"}

  accessToken = authTokenized[1]
  jwtRes = validateJWT(accessToken)
  if not jwtRes["status"]: return jwtRes
  cur.execute("SELECT * FROM APP_USER where email = %s", (jwtRes["payload"]["email"],))
  res = cur.fetchone()
  if not res: 
    return {"status": False, "message": "User not found", "action": "log_out"}
  return jwtRes