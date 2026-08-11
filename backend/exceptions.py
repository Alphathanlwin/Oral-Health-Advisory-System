from fastapi import HTTPException


class EmailAlreadyExistsException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=409,
            detail={
                "code": "EMAIL_ALREADY_EXISTS",
                "message": "An account with this email already exists.",
            },
        )


class InvalidCredentialsException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=401,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Incorrect email or password.",
            },
        )


class UnauthorizedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=401,
            detail={
                "code": "UNAUTHORIZED",
                "message": "Missing or invalid authentication token.",
            },
        )


class InvalidImageFormatException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=400,
            detail={
                "code": "INVALID_IMAGE_FORMAT",
                "message": "Unsupported image. Use a JPEG, PNG, or WEBP photo of at least 100x100px.",
            },
        )


class ImageTooLargeException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=400,
            detail={
                "code": "IMAGE_TOO_LARGE",
                "message": "Image exceeds the 5 MB size limit.",
            },
        )
