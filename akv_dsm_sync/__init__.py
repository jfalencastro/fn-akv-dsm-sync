import azure.functions as func
import logging
import requests

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("requests OK")
    return func.HttpResponse("OK")
