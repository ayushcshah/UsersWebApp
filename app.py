from flask import Flask, jsonify, request, abort
import json
from models.models import User, Support, UserResponse, Users

app = Flask(__name__)

# Load DB
with open("db.json", "r") as f:
    db = json.load(f)


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    users_data = db.get("users", [])
    support_data = db.get("support", {})

    user_dict = next((u for u in users_data if u["id"] == user_id), None)
    if not user_dict:
        abort(404, description="User not found")

    user = User(**user_dict)
    support = Support(**support_data)
    response = UserResponse(data=user, support=support)

    return jsonify(response.to_dict())


@app.route("/users/", methods=["GET"])
def get_users():
    users_data = db.get("users", [])
    users = [User(**u) for u in users_data]

    # Query params (default page=1, per_page=6)
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 6))

    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_users = users[start:end]

    total = len(users)
    total_pages = (total + per_page - 1) // per_page

    response = Users(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        data=paginated_users
    )

    return jsonify(response.to_dict())


# Error handlers to always return JSON
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal Server Error"}), 500


if __name__ == "__main__":
    app.run(debug=True)
