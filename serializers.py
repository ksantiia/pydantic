from pydantic import BaseModel, Field

# Модели для получения ключа
class AuthReqModel(BaseModel):
    username: str = Field(...)
    password: str = Field(...)

class AuthResp(BaseModel):
    token: str

#Модели для работы с сущностью
class BookingDate(BaseModel):
    checkin: str
    checkout: str

class BookingRespModel(BaseModel):
    firstname: str = Field(...)
    lastname: str = Field(...)
    totalprice: int = Field(...)
    depositpaid: bool = Field(...)
    bookingdates: dict = Field(...)
    additionalneeds: str = Field(None)

class CreateBookRequest(BaseModel):
    firstname: str = Field(...)
    lastname: str = Field(...)
    totalprice: int = Field(...)
    depositpaid: bool = Field(...)
    bookingdates: BookingDate = Field(...)
    additionalneeds: str = Field(...)

class BookingResponse(BaseModel):
    bookingid: int
    booking: CreateBookRequest

class Booking(BaseModel):
    firstname: str = Field(...)
    lastname: str = Field(...)
    totalprice: int = Field(...)
    depositpaid: bool = Field(...)
    bookingdates: dict = Field(...)
    additionalneeds: str = Field(...)

class CreateBookResponse(BaseModel):
    bookingid: int


