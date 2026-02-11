import logging
import azure.functions as func

def main(event: func.EventGridEvent):
    logging.info("### EVENT GRID DISPAROU ###")
