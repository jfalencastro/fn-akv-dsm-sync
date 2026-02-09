import os
import json
import base64
import logging
import requests
import azure.functions as func


DSM_BASE_URL = os.getenv("DSM_BASE_URL")
DSM_CLIENT_ID = os.getenv("DSM_CLIENT_ID")
DSM_CLIENT_SECRET = os.getenv("DSM_CLIENT_SECRET")


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

    return response.json()["access_token"]


def encode_secret_data(secret_value: str) -> str:
    """
    DSM exige que o campo Data seja um JSON válido codificado em base64
    """
    data_json = {
        "value": secret_value
    }

    json_bytes = json.dumps(data_json).encode("utf-8")
    return base64.b64encode(json_bytes).decode("utf-8")


def post_secret_to_dsm(token: str, payload: dict):
    url = f"{DSM_BASE_URL}/iso/sctm/secret"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    dsm_payload = {
        "Name": payload["secret_name"],
        "Identity": payload["identity"],
        "Description": payload.get("description", ""),
        "Engine": payload["engine"],
        "Expiration_Date": payload.get("expiration_date"),
        "renew_cloud_time": payload.get("renew_cloud_time"),
        "renew_credential_time": payload.get("renew_credential_time"),
        "renew_ephemeral_credential_time": payload.get("renew_ephemeral_credential_time"),
        "Data": encode_secret_data(payload["secret_value"])
    }

    # Remove campos nulos (DSM é sensível a isso)
    dsm_payload = {k: v for k, v in dsm_payload.items() if v is not None}

    logging.info("Payload enviado ao DSM:")
    logging.info(json.dumps(dsm_payload, indent=2))

    response = requests.post(url, headers=headers, json=dsm_payload, timeout=10)
    response.raise_for_status()

    return response.json()


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("=== AKV → DSM FUNCTION STARTED ===")

    try:
        logging.info("Reading request body...")
        body = req.get_json()
        logging.info(f"Payload recebido: {json.dumps(body)}")

        logging.info("Getting DSM token...")
        token = get_dsm_token()
        logging.info("DSM token obtido com sucesso")

        logging.info("Posting secret to DSM...")
        result = post_secret_to_dsm(token, body)

        logging.info("Secret enviada com sucesso ao DSM")

        return func.HttpResponse(
            json.dumps({
                "status": "success",
                "dsm_response": result
            }),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.exception("ERRO FATAL NA FUNCTION")
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
