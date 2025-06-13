from flask import jsonify
from sqlalchemy.exc import OperationalError, IntegrityError
from werkzeug.exceptions import HTTPException
from .error.errors import (
    AppError, DatabaseConnectionError, ValidationError,
    AuthenticationError, AuthorizationError, ResourceNotFoundError,
    BusinessError
)

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        response = {
            'error': {
                'code': error.error_code,
                'message': error.message,
                'details': error.details
            }
        }
        return jsonify(response), error.status_code

    @app.errorhandler(OperationalError)
    def handle_database_error(error):
        db_error = DatabaseConnectionError(
            details={'original_error': str(error)}
        )
        return handle_app_error(db_error)

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        app_error = BusinessError(
            message="数据完整性错误",
            details={'original_error': str(error)}
        )
        return handle_app_error(app_error)

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        app_error = AppError(
            message=error.description,
            status_code=error.code,
            error_code=f"HTTP_{error.code}",
            details={'original_error': str(error)}
        )
        return handle_app_error(app_error)

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        app_error = AppError(
            message="服务器内部错误",
            details={'original_error': str(error)}
        )
        return handle_app_error(app_error) 