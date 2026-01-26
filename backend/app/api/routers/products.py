from fastapi import APIRouter

# Create a router with a prefix and a tag
router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/")
async def get_all_products():
    """
    Retrieve a complete list of all products.

    Returns a stub response with status, data, and message.
    """
    return {
        "status": "success",
        "data": None,  # Placeholder for actual product list
        "message": "Retrieved all products successfully (stub)"
    }


@router.post("/")
async def create_product():
    """
    Create a new product.

    Returns a stub response with status, data, and message.
    """
    return {
        "status": "success",
        "data": None,  # Placeholder for the created product
        "message": "Product created successfully (stub)"
    }


@router.get("/category/{category_id}")
async def get_products_by_category(category_id: int):
    """
    Retrieve all products belonging to a specific category.

    Returns a stub response with status, data, and message.
    """
    return {
        "status": "success",
        "data": None,  # Placeholder for products in the category
        "message": f"Retrieved products for category ID {category_id} (stub)"
    }


@router.get("/{product_id}")
async def get_product(product_id: int):
    """
    Retrieve detailed information about a product by its ID.

    Returns a stub response with status, data, and message.
    """
    return {
        "status": "success",
        "data": None,  # Placeholder for product details
        "message": f"Retrieved product with ID {product_id} successfully (stub)"
    }


@router.put("/{product_id}")
async def update_product(product_id: int):
    """
    Update the details of a product by its ID.

    Returns a stub response with status, data, and message.
    """
    return {
        "status": "success",
        "data": None,  # Placeholder for the updated product
        "message": f"Product with ID {product_id} updated successfully (stub)"
    }


@router.delete("/{product_id}")
async def delete_product(product_id: int):
    """
    Delete a product by its ID.

    Returns a stub response with status, data, and message.
    """
    return {
        "status": "success",
        "data": None,  # Placeholder since product is deleted
        "message": f"Product with ID {product_id} deleted successfully (stub)"
    }
