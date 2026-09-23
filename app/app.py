import json
import os

import boto3
import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template

from app.storage import list_bucket_objects

load_dotenv()

app = Flask(__name__)


def get_database_credentials():
    secret_name = os.getenv(
        "AWS_DB_SECRET_NAME",
        "cloud-app/rdscloud-app/rds"
    )

    region_name = os.getenv("AWS_REGION", "us-east-1")

    client = boto3.client(
        "secretsmanager",
        region_name=region_name
    )

    response = client.get_secret_value(
        SecretId=secret_name
    )

    return json.loads(response["SecretString"])


def get_database_connection():
    credentials = get_database_credentials()

    return psycopg2.connect(
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT", "5432"),
        database=os.getenv("DATABASE_NAME"),
        user=credentials["username"],
        password=credentials["password"],
        sslmode="require"
    )


@app.route("/")
def home():
    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                resource_type,
                environment,
                status,
                created_at
            FROM resources
            ORDER BY id;
        """)

        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        resources_data = []

        for row in rows:
            resources_data.append({
                "id": row[0],
                "name": row[1],
                "resource_type": row[2],
                "environment": row[3],
                "status": row[4],
                "created_at": row[5].strftime("%Y-%m-%d %H:%M:%S")
            })

        return render_template(
            "index.html",
            resources=resources_data,
            database_error=None
        )

    except Exception as error:
        return render_template(
            "index.html",
            resources=[],
            database_error=str(error)
        ), 500


@app.route("/health")
def health():
    return {
        "status": "healthy"
    }


@app.route("/database-test")
def database_test():
    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT version();")

        database_version = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return {
            "status": "connected",
            "database": "PostgreSQL",
            "version": database_version
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }, 500


@app.route("/resources")
def resources():
    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                resource_type,
                environment,
                status,
                created_at
            FROM resources
            ORDER BY id;
        """)

        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        resources_data = []

        for row in rows:
            resources_data.append({
                "id": row[0],
                "name": row[1],
                "resource_type": row[2],
                "environment": row[3],
                "status": row[4],
                "created_at": row[5].isoformat()
            })

        return {
            "status": "success",
            "resources": resources_data
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }, 500

    
@app.route("/storage-test")
def storage_test():
    return list_bucket_objects()


if __name__ == "__main__":
    app.run(
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 5000)),
        debug=True
    )