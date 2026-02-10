import logging
import azure.functions as func
from azure.identity import ManagedIdentityCredential

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Início da function – teste Managed Identity")

    try:
        credential = ManagedIdentityCredential()

        logging.info("ManagedIdentityCredential criado")

        token = credential.get_token("https://vault.azure.net/.default")

        logging.info("Token obtido com sucesso")

        return func.HttpResponse(
            body="Managed Identity OK",
            status_code=200
        )

    except Exception as e:
        logging.error("Erro ao usar Managed Identity", exc_info=True)

        return func.HttpResponse(
            body=f"Erro MI: {str(e)}",
            status_code=500
        )
