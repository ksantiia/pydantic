import requests
from serializers import AuthResp, BookingResponse


url = 'https://restful-booker.herokuapp.com/'

def auth_token():
    headers = {'Content-Type': 'application/json'}
    data = {
        'username': 'admin',
        'password': 'password123'
    }
    response = requests.post(url + 'auth', headers=headers, json=data)
    response_model = AuthResp(**response.json())

    return response_model.token

print(auth_token)

def create_booking(auth_token):
    headers = {"Content-Type": "application/json"}
    data = {
        "firstname": "Jim",
        "lastname": "Brown",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2018-01-01",
            "checkout": "2019-01-01"
        },
        "additionalneeds": "Breakfast"
    }

    response = requests.post(url + 'booking', headers=headers, json=data)
    response_model = BookingResponse(**response.json())
    return response_model.bookingid
print(create_booking)





