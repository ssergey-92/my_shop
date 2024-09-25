
class OrderException(Exception):
    """Custom exception related to model Order."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
