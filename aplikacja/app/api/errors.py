from flask import jsonify


class NotFoundError(Exception):
    def __init__(self, resource, resource_id):
        self.message = f"{resource} o id={resource_id} nie istnieje."
        super().__init__(self.message)


class ValidationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Nieprawidłowe żądanie.", "details": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Wymagane uwierzytelnienie."}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Brak uprawnień."}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Zasób nie został znaleziony."}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Wewnętrzny błąd serwera."}), 500

    @app.errorhandler(NotFoundError)
    def handle_not_found(e):
        return jsonify({"error": e.message}), 404

    @app.errorhandler(ValidationError)
    def handle_validation(e):
        return jsonify({"error": e.message}), 400
