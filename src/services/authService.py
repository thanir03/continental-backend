from src.db import convertToDict

def getUserByEmail(cur, email: str):
  cur.execute("SELECT name, email, auth, password FROM app_user where email = %s;", (email,))
  res = cur.fetchone()
  return convertToDict(res, ["name", "email", "auth", "password"])
   


def insertNewUser(cur, email: str, name: str, auth_type:str, password: str= ""):
  if auth_type == "google":
    cur.execute("INSERT INTO app_user (email, name, auth) values (%s, %s, %s);", (email, name, 'oauth_google'))
  else : 
    cur.execute("INSERT INTO app_user (email, name, auth, password) values (%s, %s, %s, %s);", (email, name, auth_type, password))



def updateAuthMethod(cur, email: str, auth_method:str, name:str , password: str= ""):
  if auth_method == "oauth_google":
    cur.execute("UPDATE  app_user SET auth = %s, password = %s, name =%s WHERE email = %s;", ('password', password, name, email))
  else : 
    cur.execute("UPDATE  app_user SET auth = %s, password = %s, name =%s WHERE email = %s;", ('oauth_google', None, name, email))
