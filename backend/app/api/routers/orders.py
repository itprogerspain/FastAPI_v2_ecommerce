from fastapi import APIRouter, Depends, status, Query
from app.api.deps import get_order_service, get_current_user
from app.application.orders.service import OrderService
from app.application.orders.schemas import Order as OrderSchema, OrderList

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/checkout",
    response_model=OrderSchema,
    status_code=status.HTTP_201_CREATED,
)
async def checkout_order(
    current_user=Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):
    return await order_service.checkout(current_user.id)


@router.get("/", response_model=OrderList)
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user=Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):
    """
    Returns the current user's orders with simple pagination.
    """
    return await order_service.list_orders(current_user.id, page, page_size)


@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(
    order_id: int,
    current_user=Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):
    """
    Returns order with items and products.
    Access restricted to the owner.
    """
    return await order_service.get_order(current_user.id, order_id)
