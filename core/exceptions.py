from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return Response(
            {
                "error": {
                    "code": "internal_error",
                    "message": "Erro interno do servidor.",
                    "details": [],
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    details = response.data
    message = "Falha na requisicao."

    if isinstance(details, dict):
        if "detail" in details:
            message = str(details["detail"])
        else:
            first_key = next(iter(details), None)
            if first_key is not None:
                message = f"Erro no campo {first_key}."

    response.data = {
        "error": {
            "code": f"http_{response.status_code}",
            "message": message,
            "details": details,
        }
    }
    return response
