import logging
import os
import json
import requests
import azure.functions as func

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


def get_secret_from_akv(vault_url: str, secret_name: str) -> str:
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)

    logging.info(f"Buscando secret '{secret_name}' no Azure Key Vault")
    secret = client.get_secret(secret_name)
    return secret.value


def get_dsm_token() -> str:
    url = f"{os.environ['DSM_BASE_URL']}/iso/oauth2/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": os.environ["DSM_CLIENT_ID"],
        "client_secret": os.environ["DSM_CLIENT_SECRET"]
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    logging.info("Solicitando token OAuth2 no DSM")

    response = requests.post(url, data=payload, headers=headers, timeout=10)

    if response.status_code != 200:
        logging.error("Erro ao obter token DSM: %s", response.text)
        raise Exception("Falha ao autenticar no DSM")

    token = response.json().get("access_token")
    if not token:
        raise Exception("Token DSM não retornado")

    return token


def create_or_update_dsm_secret(token: str, payload: dict):
    url = f"{os.environ['DSM_BASE_URL']}{os.environ['DSM_SECRET_PATH']}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    dsm_request = {
        "data": payload
    }

    logging.info("Enviando secret para o DSM")
    logging.debug("Payload DSM final: %s", json.dumps(dsm_request))

    response = requests.post(
        url,
        json=dsm_request,
        headers=headers,
        timeout=10
    )

    if response.status_code not in (200, 201):
        logging.error(
            "Erro DSM (%s): %s",
            response.status_code,
            response.text
        )
        raise Exception("Falha ao criar secret no DSM")

    return response.json()



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("AKV → DSM sync iniciado")

    try:
        body = req.get_json()

        akv_secret_name = body["akv_secret_name"]
        dsm_payload = body["dsm_payload"]

        # 1️⃣ Lê secret do Key Vault
        secret_value = get_secret_from_akv(
            os.environ["AKV_URI"],
            akv_secret_name
        )

        # injeta o valor da secret no payload DSM
        dsm_payload["secret"] = secret_value

        # 2️⃣ Token DSM
        token = get_dsm_token()

        # 3️⃣ Cria / atualiza secret no DSM
        result = create_or_update_dsm_secret(token, dsm_payload)

        return func.HttpResponse(
            json.dumps({
                "status": "success",
                "dsm_response": result
            }),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.exception("Erro durante execução da Function")
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
