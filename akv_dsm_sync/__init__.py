import os
import json
import logging
import requests
import azure.functions as func


DSM_BASE_URL = os.getenv("DSM_BASE_URL")
DSM_CLIENT_ID = os.getenv("DSM_CLIENT_ID")
DSM_CLIENT_SECRET = os.getenv("DSM_CLIENT_SECRET")
DSM_ORG_ID = os.getenv("DSM_ORG_ID")
DSM_SYSTEM_ID = os.getenv("DSM_SYSTEM_ID")


def get_dsm_token():
    url = f"{DSM_BASE_URL}/iso/oauth2/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": DSM_CLIENT_ID,
        "client_secret": DSM_CLIENT_SECRET
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=payload, headers=headers, timeout=10)
    response.raise_for_status()

    token = response.json().get("access_token")
    return token


def post_secret_to_dsm(token, secret_data):
    url = f"{DSM_BASE_URL}/secret"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "name": secret_data["secret_name"],
        "secret": secret_data["secret_value"],
        "description": secret_data.get("description", ""),
        "tags": secret_data.get("tags", []),
        "organization_id": int(DSM_ORG_ID),
        "system_id": int(DSM_SYSTEM_ID)
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()

    return response.json()


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("AKV → DSM sync triggered")

    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON body",
            status_code=400
        )

    required_fields = ["secret_name", "secret_value"]
    for field in required_fields:
        if field not in body:
            return func.HttpResponse(
                f"Missing required field: {field}",
                status_code=400
            )

    try:
        token = get_dsm_token()
        result = post_secret_to_dsm(token, body)

        return func.HttpResponse(
            json.dumps({
                "status": "success",
                "dsm_response": result
            }),
            status_code=200,
            mimetype="application/json"
        )

    except requests.exceptions.RequestException as e:
        logging.error(f"DSM request failed: {str(e)}")
        return func.HttpResponse(
            f"DSM request failed: {str(e)}",
            status_code=500
        )

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return func.HttpResponse(
            f"Unexpected error: {str(e)}",
            status_code=500
        )
