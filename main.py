import requests
import os
from dotenv import load_dotenv
import jwt
import time


def authenticate():
    global access_token
    r = requests.post(f"{os.getenv('AUTH_URL')}oauth/token", data=creds)
    print(r.request.headers)
    r_json = r.json()
    if r_json.get("access_token") == None:
        print("Error: " + r_json.get("error"))
        print("Error description: " + r_json.get("error_description"))
        exit(-1)
    access_token = r_json.get("access_token")


if __name__ == "__main__":
    global instance
    global creds

    load_dotenv()
    creds = {
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "grant_type": "client_credentials",
    }
    authenticate()
    print("Access token: " + access_token)
    while 1:
        if (
            jwt.decode(access_token, options={"verify_signature": False})["exp"]
            < time.time()
        ):
            authenticate()
        cmd = str(input("Enter command: "))
        if cmd == "ls":
            r = requests.get(
                f"{os.getenv('API_URL')}api/user",
                json={
                    "limit":100,
                    "offset":0
                },
                headers={
                    "Authorization": "Bearer " + access_token,
                    "x-api-version": "1.0",
                },
            )
            if r.status_code == 200:
                print("Users (max. 100):")
                for i in r.json().get("data"):
                    print(
                        "User:",
                        i.get("pairwiseID"),
                        "ID:",
                        i.get("userID"),
                        "ProfileCount:",
                        i.get("profileCount"),
                    )
            else:
                print(r.json())
        elif cmd == "exit":
            break
        elif cmd == "show":
            uid = str(input("Enter user id: "))
            r = requests.get(
                f"{os.getenv('API_URL')}api/user/" + uid,
                headers={
                    "Authorization": "Bearer " + access_token,
                    "x-api-version": "1.0",
                },
            )
            if r.status_code == 200:
                tmp = r.json().get("data")
                print(10 * "=")
                print(
                    "User: " + tmp.get("pairwiseID"),
                    "ID: " + tmp.get("userID"),
                    "ProfileCount: " + str(tmp.get("profileCount")),
                    "MaxProfileCount: " + str(tmp.get("maxProfiles")),
                    "Locked: " + str(tmp.get("locked")),
                    sep="\n",
                )
                print(10 * "=")
            else:
                print(r.json().get("error"))
        elif cmd == "toggle-lock":
            uid = str(input("Enter user id: "))
            r = requests.get(
                f"{os.getenv('API_URL')}api/user/" + uid,
                headers={
                    "Authorization": "Bearer " + access_token,
                    "x-api-version": "1.0",
                },
            )
            if r.status_code == 200:
                r2 = requests.put(
                    f"{os.getenv('API_URL')}api/user/" + uid + "/status",
                    headers={
                        "Authorization": "Bearer " + access_token,
                        "x-api-version": "1.0",
                    },
                    json={"locked": not r.json().get("data").get("locked")},
                )
                if r2.status_code == 200:
                    print("User:",uid,"has been",("unlocked" if r.json().get("data").get("locked") else "locked"))
                else:
                    print(r2.status_code)
                    print(r2.json().get("error"))
            else:
                print(r.json().get("error"))
        else:
            print("Unknown command")
            print("Commands: ls, show, toggle-lock, exit")

    exit(0)
