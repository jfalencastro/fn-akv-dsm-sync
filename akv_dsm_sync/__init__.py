import logging
import azure.functions as func

def main(event: func.EventGridEvent):
    logging.info("### EVENT GRID DISPAROU ###")

    event_data = event.get_json()

    logging.info("Payload bruto recebido do Event Grid:")
    logging.info(event_data)

    # Extração segura
    try:
        secret_name = event_data["data"]["ObjectName"]
        vault_name = event_data["data"]["VaultName"]

        logging.info(f"Secret detectada: {secret_name}")
        logging.info(f"Key Vault: {vault_name}")

    except Exception as e:
        logging.error("Falha ao interpretar payload do Event Grid")
        logging.exception(e)
        raise

    logging.info("### TESTE CONTROLADO FINALIZADO COM SUCESSO ###")
