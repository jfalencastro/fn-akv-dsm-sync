import azure.functions as func
import logging
import sys

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(str(sys.path))
    return func.HttpResponse("OK")
