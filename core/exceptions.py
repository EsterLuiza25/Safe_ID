from rest_framework.exceptions import ErrorDetail
from rest_framework.views import exception_handler


def _normalize_details(data):
    if isinstance(data, list):
        return [_normalize_details(item) for item in data]

    if isinstance(data, dict):
        return {key: _normalize_details(value) for key, value in data.items()}

    if isinstance(data, ErrorDetail):
        return str(data)

    return data


def standard_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    original_data = response.data
    details = _normalize_details(original_data)

    if response.status_code == 400:
        code = "validation_error"
        message = "Erro de validacao."
    elif response.status_code == 401:
        code = "not_authenticated"
        message = "Credenciais de autenticacao nao foram informadas."
    elif response.status_code == 403:
        code = "permission_denied"
        message = "Acesso negado."
    elif response.status_code == 404:
        code = "not_found"
        message = "Recurso nao encontrado."
    elif response.status_code == 429:
        code = "rate_limited"
        message = "Limite de requisicoes excedido."
    else:
        code = "api_error"
        message = "Erro ao processar requisicao."

    if isinstance(details, dict) and "detail" in details and len(details) == 1:
        message = str(details["detail"])
        details = {}

    response.data = {
        "code": code,
        "message": message,
        "details": details,
    }
    return response
