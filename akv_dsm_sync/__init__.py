import logging
import requests

def main(req):
    logging.info("Function started")

    try:
        logging.info("Requests version: %s", requests.__version__)
    except Exception as e:
        logging.error("Failed importing requests: %s", str(e))
        raise

    return "OK"
