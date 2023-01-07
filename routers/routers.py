import requests
from typing import List

from fastapi import APIRouter, Body, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

from utils.schemas import UserOut, UserAuth, TokenSchema, NewOrder, ProductCreate, ProductUpdate
from models.product import Product
from models.order import Order
from models.user import User
from database.database import *
from utils.utils import *


router = APIRouter()


@router.post('/signup', tags=['login'], summary="Create new user", response_model=UserOut)
async def create_user(data: UserAuth):

    user = await retrieve_user(data.email)

    if user:
        raise HTTPException(
            status_code=_400_BAD_REQUEST,
            detail="User with this email already exist"
        )

    hashed_pass = get_hashed_password(data.password)
    user = User(first_name=data.first_name, last_name=data.last_name,
                email=data.email, password=hashed_pass, phone_number=data.phone_number)
    await add_new_user(user)
    return user


@router.post('/login', tags=['login'], summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await retrieve_user(form_data.username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user['password']
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    return {
        "access_token": create_access_token(user['email']),
        "refresh_token": create_refresh_token(user['email']),
    }


@router.get('/me', tags=['login'], summary='Get details of currently logged in user', response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
    return user


@router.get("/products", tags=['products'], summary="Get all products")
async def get_products():
    products = await retrieve_products()

    return products


@router.get("/products/{id}", tags=['products'], summary="Get product by id")
async def get_product(id: str):
    product = await retrieve_product(id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product doesn't exist"
        )

    return product


@router.post("/products", tags=['products'], summary='Create new product', dependencies=[Depends(get_current_user)])
async def add_product(product: ProductCreate = Body(...)):
    p = Product(**product.dict())
    new_product = await add_new_product(p)

    if not new_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product creation failed"
        )

    return new_product


@router.put("/products/{id}", tags=['products'], summary='Update product by id', dependencies=[Depends(get_current_user)])
async def update_product(id: str, req: ProductUpdate = Body(...)):
    updated_product = await update_product_data(id, req.__dict__)

    return updated_product


@router.get("/categories", tags=['categories'], summary="Get all categories")
async def get_categories():
    categories = await retrieve_categories()

    return categories


@router.get("/orders", tags=['orders'], summary="Get all orders")
async def get_orders():
    orders = await retrieve_orders()

    return orders


@router.post("/orders", tags=['orders'], summary='Create new order', dependencies=[Depends(get_current_user)])
async def add_order(order: NewOrder = Body(...)):
    o = Order(**order.dict(), status='Unapproved')
    new_order = await add_new_order(o)

    if not new_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order creation failed"
        )

    return order


@router.put("/orders/{id}", tags=['orders'], summary='Update order by id', dependencies=[Depends(get_current_user)])
async def update_order(id: str, req: dict = Body(...)):
    updated_order = await update_order_data(id, req)

    return updated_order


@router.get("/orders/status/{id}", tags=['orders'], summary="Get orders by status")
async def get_orders_by_status(id: str):
    orders = await retrieve_orders_by_status(id)

    return orders


@router.get("/status", tags=['status'], summary="Get all statuses")
async def get_statuses():
    statuses = await retrieve_statuses()

    return statuses
