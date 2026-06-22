from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Backend API (KEEP THIS)
BACKEND_API = "http://backend-alb-965546045.eu-north-1.elb.amazonaws.com"


# =========================
# HEALTH CHECK (ADDED - IMPORTANT)
# =========================
@app.route("/health", methods=["GET"])
def health():
    return "OK", 200


@app.route("/", methods=["GET"])
def index():
    try:
        response = requests.get(f"{BACKEND_API}/users", timeout=5)
        users = response.json()
    except Exception as e:
        users = []
        print(f"Error fetching users: {str(e)}")
    return render_template("index.html", users=users)


@app.route("/add-user", methods=["POST"])
def add_user():
    name = request.form.get("name")
    email = request.form.get("email")

    if not name or not email:
        return jsonify(status="error", message="Name and Email are required")

    try:
        response = requests.post(
            f"{BACKEND_API}/users/add",
            json={"name": name, "email": email},
            timeout=5
        )

        if response.status_code == 201:
            return jsonify(status="success", message="User added successfully!")
        elif response.status_code == 409:
            return jsonify(status="duplicate", message="User already exists!")
        else:
            return jsonify(status="error", message="Unknown error")

    except Exception as e:
        return jsonify(status="error", message=str(e))


@app.route("/delete-user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    try:
        response = requests.delete(
            f"{BACKEND_API}/users/delete/{user_id}",
            timeout=5
        )

        if response.status_code == 200:
            return jsonify(status="success", message="User deleted successfully!")
        else:
            return jsonify(status="error", message="Delete failed")

    except Exception as e:
        return jsonify(status="error", message=str(e))


@app.route("/update-user/<int:user_id>", methods=["POST"])
def update_user(user_id):
    name = request.form.get("name")
    email = request.form.get("email")

    if not name or not email:
        return jsonify(status="error", message="Name and Email are required")

    try:
        response = requests.put(
            f"{BACKEND_API}/users/update/{user_id}",
            json={"name": name, "email": email},
            timeout=5
        )

        if response.status_code == 200:
            return jsonify(status="success", message="User updated successfully!")
        else:
            return jsonify(status="error", message="Update failed")

    except Exception as e:
        return jsonify(status="error", message=str(e))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
