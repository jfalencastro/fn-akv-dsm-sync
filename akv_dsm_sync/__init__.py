import logging
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(">>> INICIO DA FUNCAO <<<")

    return func.HttpResponse(
        "Function V1 funcionando",
        status_code=200
    )
