from quart import Blueprint, jsonify

module_api_bp = Blueprint('template', __name__)

@module_api_bp.route("/example", methods=["GET"])
async def example_endpoint():
    return jsonify({"status": 200, "message": "This is an example API route from the template module"})