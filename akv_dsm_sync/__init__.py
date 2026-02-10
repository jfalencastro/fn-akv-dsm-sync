import logging
import azure.functions as func
from azure.identity import DefaultAzureCredential

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("INICIO - Teste Managed Identity")

    try:
        credential = DefaultAzureCredential()
        token = credential.get_token("https://management.azure.com/.default")
        logging.info("Managed Identity OK")
    except Exception as e:
        logging.error(f"Erro Managed Identity: {e}")
        return func.HttpResponse("MI falhou", status_code=500)

    return func.HttpResponse("Managed Identity funcionando", status_code=200)
