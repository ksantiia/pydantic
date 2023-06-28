import pytest
import requests
from pydantic import ValidationError
from serializers import AuthReqModel, BookingRespModel, CreateBookRequest, BookingResponse
from api import url, auth_token, create_booking


class Test:

    # Тесты на проверку получения token
    @pytest.mark.parametrize('username, password, headers', [
        ('admin', 'password123', {'Content-Type': 'application/json'}),  # Передача корректных атрибутов
        ('admin', 'password123', {'Content-Type': ''}),   # Передача атрибутов с ошибкой в headers
        ('admin', 'password123', {}),   # Передача атрибутов с пустым headers
        ('', '', {'Content-Type': 'application/json'}),   # Передаем только heders
        ('jyfj', 'ghg123', {'Content-Type': 'application/json'})    # Передача не корректных username и password
    ])

    def test_auth_req(self, username, password, headers):
        try:
            data = AuthReqModel(username=username, password=password)
        except ValidationError as e:
            if username == '' and password == '':
                assert str(e) == '1 validation error for AuthReqModel'
            else:
                pytest.fail(f'failed to validate request data: {e}')

        response = requests.post(url + 'auth', headers=headers, json=data.dict())

        assert response.status_code == 200, f'failed with status code {response.status_code}'
        if "reason" in response.json() and response.json()["reason"] == "Bad credentials":
            assert "token" not in response.json(), "token is invalid"
        else:
            assert "token" in response.json(), "not contain in token"


#Тесты на проверку создания сущностей(заказа).
#В проверке имеется падающий тест.
    @pytest.mark.parametrize('headers, request_body, expected_status', [
        ({"Content-Type": "application/json", "Accept": "application/json"}, # Передача корректных атрибутов
         {"firstname": "Jim", "lastname": "Brown", "totalprice": 111, "depositpaid": True,
          "bookingdates": {"checkin": "2018-01-01", "checkout": "2019-01-01"},
          "additionalneeds": "Breakfast"}, 200),
        ({"Content-Type": "text/plain", "Accept": "text/plain"},  # Передача атрибутов с ошибкой в headers. Падающий тест: Ошибка ответа по status_code
         {"firstname": "Jim", "lastname": "Brown", "totalprice": 111, "depositpaid": True,
          "bookingdates": {"checkin": "2018-01-01", "checkout": "2019-01-01"},
          "additionalneeds": "Breakfast"}, 415),
        (None, {"firstname": "Jim", "lastname": "Brown", "totalprice": 111, "depositpaid": True,
                "bookingdates": {"checkin": "2018-01-01", "checkout": "2019-01-01"}, # Передача атрибутов с пустым headers
                "additionalneeds": "Breakfast"}, 200)
    ])

    def test_created_booking(self, headers, request_body, expected_status):

        try:
            request_data = CreateBookRequest(**request_body)
        except ValidationError as e:
            pytest.fail(f'failed to validate request data: {e}')

        response = requests.post(url + 'booking', headers=headers, json=request_data.dict())

        assert response.status_code == expected_status, f'failed with status code {response.status_code}'

        if expected_status == 200:
            try:
                response_data = response.json()
                booking_response = BookingResponse(**response_data)
            except (ValidationError, TypeError) as e:
                pytest.fail(f'failed to validate request data: {e}')

            assert booking_response.bookingid is not None and isinstance(booking_response.bookingid, int), \
                'BooKing ID is missing or invalid'
            assert isinstance(booking_response.booking, CreateBookRequest), 'BooKing data is missing or invalid'
            booking = booking_response.booking
            assert booking.firstname == request_data.firstname, 'Invalid firstname'
            assert booking.lastname == request_data.lastname, 'Invalid lastname'
            assert booking.totalprice == request_data.totalprice, 'Invalid totalprice'
            assert booking.depositpaid == request_data.depositpaid, 'Invalid depositpaid'
            assert booking.bookingdates.dict() == request_data.bookingdates.dict(), 'Invalid bookingdates'
            assert booking.additionalneeds == request_data.additionalneeds, 'Invalid additionalneeds'


# Тесты на проверку получения сущностей
    @pytest.mark.parametrize('bookingid, expected_status, headers', [
        (1, 200, {"Accept": "application/json"}),   # Передача корректных атрибутов
        (0, 404, {"Accept": "application/json"}),   # Передача значения id, как 0
        (-1, 404, {"Accept": "application/json"}),  # Передача значения id отрицательным
        ('r', 404, {"Accept": "application/json"}),  # Передача значения id в виде строки
        (1, 418, {"Accept": ""}),   # Передача атрибутов с ошибкой в headers.
        (1, 200, None)   # Передача атрибутов с пустым headers
    ])

    def test_get_booking(self, bookingid, expected_status, headers):

        response = requests.get(url + f'booking/{bookingid}', headers=headers)

        assert response.status_code == expected_status, f'failed with status code {response.status_code}'

        if expected_status == 200:
            try:
                data = response.json()
                booking = BookingRespModel(**data)
            except (ValidationError, TypeError) as e:
                pytest.fail(f'failed to validate request data: {e}')

            assert booking.firstname != '', 'firstname is missing'
            assert booking.lastname != '', 'lastname is missing'
            assert booking.totalprice >= 0, 'Tot.price is negative'
            assert isinstance(booking.depositpaid, bool), 'Depositpaid must be a bool'
            assert isinstance(booking.bookingdates, dict), 'Bookingdates must be a dict'
            assert 'checkin' in booking.bookingdates and isinstance(booking.bookingdates['checkin'], str), \
                'Checkin date is missing or invalid'
            assert 'checkout' in booking.bookingdates and isinstance(booking.bookingdates['checkout'], str), \
                'Checkout date is missing or invalid'

# Тесты на проверку удаления сущностей.
    @pytest.mark.parametrize(
        'auth_token, create_booking, content_type, expected_status',
        [(auth_token(), create_booking(auth_token), 'application/json', 201),   # Передача корректных атрибутов
         ('jhjhkjnl', create_booking(auth_token), 'application/json', 403),   # Передача несуществующего token
         (auth_token(), '0', 'application/json', 405),    # Передача данных о сущностях в виде строки со значением "0"
         (auth_token(), create_booking(auth_token), 'text/plain', 415)]  # Передача content_type не в json формате
    )

    def test_delete_booking(self, auth_token, create_booking, content_type, expected_status):
        headers = {
            'Content-Type': f'{content_type}',
            'Cookie': f'{auth_token}'
        }

        response = requests.delete(url + 'booking' + f'{create_booking}', headers=headers)

        if response.status_code == 201:
            assert response.status_code == expected_status, f'failed with status code {response.status_code}'
            assert response.text == 'Created'
        elif response.status_code == 403:
            assert response.status_code == expected_status, f'failed with status code {response.status_code}'
            assert response.text == 'Forbidden', 'Created'
        elif response.status_code == 405:
            assert response.status_code == expected_status, f'failed with status code {response.status_code}'
            assert response.text == 'Method Not Allowed', 'Created'
        elif response.status_code == 415:
            assert response.status_code == expected_status, f'failed with status code {response.status_code}'
            assert response.text == 'TypeError', 'Created'