from django.db.models import QuerySet


def apply_pagination_to_qs(
        query_set: QuerySet, current_page: int, limit: int,
) -> QuerySet:
    """Apply pagination to queryset as per current page and limit."""

    offset = (current_page - 1) * limit
    last_item = offset + limit
    query_set = query_set[offset:last_item]
    return query_set

def get_pagination_last_page(total_records: int, page_limit: int) -> int:
    if (total_records % page_limit) == 0:
        return int(total_records / page_limit)

    return int(total_records // page_limit + 1)