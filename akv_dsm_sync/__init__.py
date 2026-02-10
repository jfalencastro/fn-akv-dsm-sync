import logging
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Sem libs externas")
    return func.HttpResponse("OK", status_code=200)

