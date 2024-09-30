from django.db.models import QuerySet

from products.constants import DEFAULT_PAGINATION_LIMIT

def apply_pagination_to_qs(
        query_set: QuerySet,
        current_page: int,
        limit: int = DEFAULT_PAGINATION_LIMIT,
) -> QuerySet:
    """Apply pagination to queryset as per current page and limit."""

    offset = (current_page - 1) * limit
    last_item = offset + limit
    query_set = query_set[offset:last_item]
    return query_set

def get_pagination_last_page(
        total_records: int,
        page_limit: int = DEFAULT_PAGINATION_LIMIT
) -> int:
    """Get last page for paginated response."""

    if (total_records % page_limit) == 0:
        return int(total_records / page_limit)

    return int(total_records // page_limit + 1)