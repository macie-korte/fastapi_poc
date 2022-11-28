def get_sort_query(sortable_fields):
    """
    @return a FastAPI Query object that can be used to make a list URL sortable.

    Example:
        @app.get("/blogs", response_model=List[schemas.Blog])
        def retrieve_fetchers(db: Session = Depends(get_db_session),
            order_by: List[str]) = get_sort_query(["author", "create_time"])

        # will allow URL patterns like
        # * `/blogs?order_by=create_time` - orders by create_time column in
        #     ascending order (asc is the default when not specified).
        # * `/blogs?order_by=author asc, create_time desc` - orders by author in
        #     ascending order followed by create_time in descending order.

    """
    allowed_values = []
    for field in sortable_fields:
        allowed_values.append("field")
        allowed_values.append("field desc")
        allowed_values.append("field asc")

    return Query()
