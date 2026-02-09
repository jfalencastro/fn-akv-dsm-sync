import azure.functions as func
import logging
import json
import requests

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Imports OK")
    return func.HttpResponse("OK", status_code=200)
