# from flask import Flask, request, jsonify

# app = Flask(__name__)

# @app.route("/", methods=["GET"])
# def home():
#     return {"message": "Cloud Automation Backend is running"}

# @app.route("/provision", methods=["POST"])
# def provision():
#     data = request.json
#     print("Provision request received:", data)

#     return jsonify({
#         "status": "success",
#         "message": "Provision request received",
#         "data": data
#     })

# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, request, jsonify
import mysql.connector
import subprocess
import os


app = Flask(__name__)

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Sadv@2803",
    database="cloud_automation"
)

cursor = db.cursor()

@app.route("/", methods=["GET"])
def home():
    return {"message": "Cloud Automation Backend is running"}

@app.route("/provision", methods=["POST"])
def provision():
    data = request.json

    resource = data.get("resource")
    instance_type = data.get("instance_type")
    region = data.get("region")
    status = "PENDING"

    sql = """
        INSERT INTO provision_requests (resource, instance_type, region, status)
        VALUES (%s, %s, %s, %s)
    """
    values = (resource, instance_type, region, status)

    cursor.execute(sql, values)
    db.commit()

    return jsonify({
        "status": "success",
        "message": "Provision request stored in database",
        "data": data
    })


@app.route("/requests", methods=["GET"])
def get_requests():
    cursor.execute("SELECT * FROM provision_requests")
    rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "resource": row[1],
            "instance_type": row[2],
            "region": row[3],
            "status": row[4],
            "created_at": str(row[5])
        })

    return jsonify(result)


@app.route("/trigger/<int:request_id>", methods=["POST"])
def trigger_provision(request_id):
    try:
        # 1. Fetch request
        cursor.execute(
            "SELECT status FROM provision_requests WHERE id=%s",
            (request_id,)
        )
        result = cursor.fetchone()

        if not result:
            return {"error": "Request not found"}, 404

        if result[0] != "PENDING":
            return {"error": "Request already processed"}, 400

        # 2. Update status to IN_PROGRESS
        cursor.execute(
            "UPDATE provision_requests SET status='IN_PROGRESS' WHERE id=%s",
            (request_id,)
        )
        db.commit()

        # 3. Run Terraform
        terraform_dir = os.path.abspath("../terraform")

        init_cmd = ["terraform", "init"]
        apply_cmd = ["terraform", "apply", "-auto-approve"]

        subprocess.run(init_cmd, cwd=terraform_dir, check=True)
        subprocess.run(apply_cmd, cwd=terraform_dir, check=True)

        # 4. Update status to COMPLETED
        cursor.execute(
            "UPDATE provision_requests SET status='COMPLETED' WHERE id=%s",
            (request_id,)
        )
        db.commit()

        return {
            "message": "Infrastructure provisioned successfully",
            "request_id": request_id
        }

    except Exception as e:
        # Failure case
        cursor.execute(
            "UPDATE provision_requests SET status='FAILED' WHERE id=%s",
            (request_id,)
        )
        db.commit()

        return {
            "error": "Provisioning failed",
            "details": str(e)
        }, 500

if __name__ == "__main__":
    app.run(debug=True)

