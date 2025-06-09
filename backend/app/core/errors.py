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