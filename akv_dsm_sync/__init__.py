import logging
import json
import azure.functions as func
import requests
import os
import base64
from datetime import datetime, timezone

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("=== Function akv_dsm_sync STARTED ===")

    try:
        logging.info("Headers: %s", dict(req.headers))
        body = req.get_json()
        logging.info("Body recebido: %s", body)

        # Apenas para confirmar requests funcionando
        logging.info("requests version: %s", requests.__version__)

        return func.HttpResponse(
            json.dumps({"status": "OK", "message": "Function executou até o fim"}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.exception("ERRO NA FUNCTION")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
