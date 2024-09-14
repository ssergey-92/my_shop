"""Handle business logic of app endpoints"""

from .catalog import CatalogHandler
from .category import (
    CategoryHandler,
    category_max_nesting_level,
)
from .product import (
    ProductHandler,
    max_sorting_index,
    min_sorting_index,
)
from .product_review import (
    ProductReviewHandler,
    max_review_rate,
    min_review_rate,
)
from .product_tag import ProductTagHandler
