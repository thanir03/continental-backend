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