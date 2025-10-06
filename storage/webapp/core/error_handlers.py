from flask import Flask, jsonify
from flask.typing import ResponseReturnValue


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def handle_not_found_error(error: Exception) -> ResponseReturnValue:
        app.logger.exception(f'Handled error: {str(error)}')
        return jsonify({'message': 'Not found'}), 404

    @app.errorhandler(Exception)
    def handle_error(error: Exception) -> ResponseReturnValue:
        app.logger.exception(f'Handled error: {str(error)}')
        return jsonify({'message': str(error)}), 500
