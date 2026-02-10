import logging
import json
import base64
import os
import requests
import azure.functions as func


def get_dsm_token():
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
    resp = requests.post(url, data=payload, headers=headers)

    if resp.status_code != 200:
        logging.error(f"Erro ao obter token DSM: {resp.text}")
        raise Exception("Falha ao obter token DSM")

    return resp.json()["access_token"]


def create_or_update_dsm_secret(token, payload):
    url = f"{os.environ['DSM_BASE_URL']}/iso/sctm/secret"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    resp = requests.post(url, headers=headers, json=payload)

    if resp.status_code not in (200, 201):
        logging.error(f"Erro DSM ({resp.status_code}): {resp.text}")
        raise Exception("Falha ao criar secret no DSM")

    return resp.json()


def main(event: func.EventGridEvent):
    try:
        event_data = event.get_json()

        secret_name = event_data["data"]["ObjectName"]
        vault_name = event_data["data"]["VaultName"]

        logging.info("Evento recebido: %s", body)
        
        # ---------
        # 1) Monta o objeto da secret (IGUAL AO POSTMAN)
        # ---------
        secret_object = {
            "key_value": {
                "fields": body["fields"]
            }
        }

        # ---------
        # 2) JSON stringify + base64
        # ---------
        secret_json = json.dumps(secret_object)
        secret_b64 = base64.b64encode(secret_json.encode("utf-8")).decode("utf-8")

        logging.info(f"Tipo da secret enviada ao DSM: {type(secret_b64)}")
        logging.info(f"Secret (base64) enviada: {secret_b64}")

        # ---------
        # 3) Payload FINAL para o DSM
        # ---------
        dsm_payload = {
            "identity": body["identity"],
            "name": body["name"],
            "engine": "Generic",
            "expiration_date": "",
            "description": body.get("description", ""),
            "data": secret_b64
        }

        logging.info("Processamento concluído com sucesso")
        
        # ---------
        # 4) OAuth2 + POST
        # ---------
        token = get_dsm_token()
        result = create_or_update_dsm_secret(token, dsm_payload)

        logging.info("Processamento concluído com sucesso")
        # não retorna nada

    except Exception:
        logging.exception("Erro durante execução da Function")
        raise

