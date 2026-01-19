from fastapi import APIRouter

# Create a router with a prefix and a tag
router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get("/")
async def get_all_categories():
    """
    Retrieve a complete list of all product categories.

    Returns a stub response with status, data, and message.
    """
    return {
        "status": "success",
        "data": None,  # Placeholder for actual category list
        "message": "Retrieved all categories successfully (stub)"
    }


@router.post("/")
async def create_category():
    """
    Create a new product category.

    Returns a stub response with status, data, and message.
    """
    return {
        "status": "success",
        "data": None,  # Placeholder for the created category
        "message": "Category created successfully (stub)"
    }


@router.put("/{category_id}")
async def update_category(category_id: int):
    """
    Update the details of a category by its ID.

    Returns a stub response with status, data, and message.
    """
    return {
        "status": "success",
        "data": None,  # Placeholder for the updated category
        "message": f"Category with ID {category_id} updated successfully (stub)"
    }


@router.delete("/{category_id}")
async def delete_category(category_id: int):
    """
    Delete a category by its ID.

    Returns a stub response with status, data, and message.
    """
    return {
        "status": "success",
        "data": None,  # Placeholder since category is deleted
        "message": f"Category with ID {category_id} deleted successfully (stub)"
    }
