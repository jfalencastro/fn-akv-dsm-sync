import logging
import azure.functions as func
from azure.identity import ManagedIdentityCredential

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Teste MI iniciado")

    credential = ManagedIdentityCredential()

    token = credential.get_token("https://management.azure.com/.default")

    logging.info("Token Azure obtido")

    return func.HttpResponse("MI OK", status_code=200)
