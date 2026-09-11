from application.common.constants import HttpErrorCodeEnum


class HttpBusinessException(Exception):
    def __init__(
        self,
        error_code: HttpErrorCodeEnum = HttpErrorCodeEnum.ERROR,
        message: str = "",
    ) -> None:
        self.code = error_code.code
        self.message = message or error_code.message
        super().__init__(self.message)
