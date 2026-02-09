import logging
import os
import requests
import azure.functions as func

app = func.FunctionApp()

@app.event_grid_trigger(arg_name="event")
def akv_secret_sync(event: func.EventGridEvent):
    logging.info("Event received from Azure Key Vault")

    data = event.get_json()

    secret_name = data.get("objectName")
    vault_name = data.get("vaultName")

    dsm_base_url = os.environ["DSM_BASE_URL"]
    client_id = os.environ["DSM_CLIENT_ID"]
    client_secret = os.environ["DSM_CLIENT_SECRET"]

    # OAuth2 Client Credentials
    token_resp = requests.post(
        f"{dsm_base_url}/iso/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        },
        timeout=10
    )
    token_resp.raise_for_status()

    access_token = token_resp.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "name": secret_name,
        "engine": "azure-key-vault",
        "description": f"Synced from AKV {vault_name}"
    }

    dsm_resp = requests.post(
        f"{dsm_base_url}/iso/secret",
        json=payload,
        headers=headers,
        timeout=10
    )

    dsm_resp.raise_for_status()
    logging.info(f"Secret {secret_name} synced to DSM")
