import logging
import azure.functions as func
import requests

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Requests version loaded")
    return func.HttpResponse("OK", status_code=200)
