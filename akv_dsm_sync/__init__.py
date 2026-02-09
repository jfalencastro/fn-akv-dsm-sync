import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        "AKV → DSM sync function is alive 🚀",
        status_code=200
    )
