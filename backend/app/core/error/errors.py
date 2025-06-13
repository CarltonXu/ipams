from typing import Any, Dict, Optional

class AppError(Exception):
    """应用基础异常类"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class DatabaseError(AppError):
    """数据库错误"""
    def __init__(
        self,
        message: str = "数据库连接错误",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=503,
            error_code="DATABASE_ERROR",
            details=details
        )

class DatabaseConnectionError(DatabaseError):
    """数据库连接错误"""
    def __init__(
        self,
        message: str = "无法连接到数据库服务器",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            details=details
        )

class ValidationError(AppError):
    """数据验证错误"""
    def __init__(
        self,
        message: str = "数据验证失败",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )

class AuthenticationError(AppError):
    """认证错误"""
    def __init__(
        self,
        message: str = "认证失败",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )

class AuthorizationError(AppError):
    """授权错误"""
    def __init__(
        self,
        message: str = "没有权限执行此操作",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )

class ResourceNotFoundError(AppError):
    """资源不存在错误"""
    def __init__(
        self,
        message: str = "请求的资源不存在",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=404,
            error_code="RESOURCE_NOT_FOUND",
            details=details
        )

class BusinessError(AppError):
    """业务逻辑错误"""
    def __init__(
        self,
        message: str = "业务处理失败",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=400,
            error_code="BUSINESS_ERROR",
            details=details
        ) 