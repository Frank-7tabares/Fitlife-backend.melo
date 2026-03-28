class DomainException(Exception):

    def __init__(self, message: str, code: str='DOMAIN_ERROR'):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return self.message
