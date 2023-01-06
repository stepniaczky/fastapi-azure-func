from models.product import Product
from models.order import Order
from models.status import Status, StatusLevel
from models.category import Category
from config.config import *
from typing import Union, Any
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from utils.utils import (
    ALGORITHM,
    JWT_SECRET_KEY
)

from jose import jwt
from pydantic import ValidationError
from utils.schemas import TokenPayload, SystemUser

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="api/login",
    scheme_name="JWT"
)


async def get_current_user(token: str = Depends(reuseable_oauth)) -> SystemUser:
    try:
        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    users_collection = get_collection('users')
    user = users_collection.find_one({'email': token_data.sub})

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return SystemUser(**user)


def init_db():
    statuses_collection = get_collection('statuses')
    categories_collection = get_collection('categories')

    categories = ['electronics', 'clothes', 'books', 'food', 'other']

    for _id, name in StatusLevel.items():
        if statuses_collection.find_one({'name': name}) is None:
            new_status = Status(_id=_id, name=name)
            statuses_collection.insert_one(new_status.__dict__)

    for i, category in enumerate(categories):
        if categories_collection.find_one({'name': category}) is None:
            new_category = Category(name=category, _id=i)
            categories_collection.insert_one(new_category.__dict__)


async def retrieve_user(email):
    users_collection = get_collection('users')
    user = users_collection.find_one({'email': email})

    return user


async def add_new_user(user):
    users_collection = get_collection('users')
    users_collection.insert_one(user.__dict__)


async def retrieve_products():
    product_collection = get_collection('products')
    products_cursor = product_collection.find()

    products = []
    for product in products_cursor:
        products.append(Product(**product))

    return products


async def retrieve_product(id):
    product_collection = get_collection('products')
    product = product_collection.find_one({'_id': id})

    return product


async def add_new_product(product):
    categories = [category.name for category in await retrieve_categories()]

    if product.category in categories:
        product_collection = get_collection('products')
        product_collection.insert_one(product.__dict__)
        return product

    return False


async def update_product_data(id, req):
    product_collection = get_collection('products')
    categories = [category.name for category in await retrieve_categories()]

    if product_collection.find_one({'_id': id}):
        if 'category' in req:
            if req['category'] not in categories:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category does not exist"
                )
        product_collection.update_one({'_id': id}, {'$set': req})
        return id
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Product not found"
    )


async def retrieve_categories():
    categories_collection = get_collection('categories')
    categories_cursor = categories_collection.find()

    categories = []
    for category in categories_cursor:
        categories.append(Category(**category))

    return categories


async def retrieve_orders():
    orders_collection = get_collection('orders')
    orders_cursor = orders_collection.find()

    orders = []
    for order in orders_cursor:
        orders.append(Order(**order))

    return orders


async def add_new_order(order):
    for product in order.ordered_products.keys():
        p = await retrieve_product(product)
        if not p:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product} does not exist in the database"
            )

    for product_quantity in order.ordered_products:
        if type(product_quantity) != int:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product quantity must be an integer"
            )

        if product_quantity < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product quantity must be greater than 0"
            )

    orders_collection = get_collection('orders')
    orders_collection.insert_one(order.__dict__)
    return order


async def update_order_data(id, req):
    if "ordered_products" in req.keys():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update ordered products"
        )

    orders_collection = get_collection('orders')
    statuses = [status.name for status in await retrieve_statuses()]

    order = orders_collection.find_one({'_id': id})

    if order:
        if order['status'] == StatusLevel[3]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is cancelled"
            )

        if 'status' in req.keys():
            if req['status'] not in statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Incorrect status for the order"
                )

            curr_status_level = [
                k for k, v in StatusLevel.items() if v == order['status']][0]
            new_status_level = [
                k for k, v in StatusLevel.items() if v == req['status']][0]

            if new_status_level < curr_status_level:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Incorrect status for the order"
                )

        orders_collection.update_one({'_id': id}, {'$set': req})
        return {"_id": id}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Order not found"
    )


async def retrieve_orders_by_status(id):
    statuses = [status.name for status in await retrieve_statuses()]

    if id not in statuses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Status not found"
        )

    orders_collection = get_collection('orders')
    orders_cursor = orders_collection.find({'status': id})
    orders = []
    for order in orders_cursor:
        orders.append(Order(**order))
    return orders


async def retrieve_statuses():
    statuses_collection = get_collection('statuses')
    statuses_cursor = statuses_collection.find()

    statuses = []
    for status in statuses_cursor:
        statuses.append(Status(**status))

    return statuses
