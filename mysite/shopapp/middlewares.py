from django.core.exceptions import RequestAborted
from django.http import HttpRequest
from datetime import datetime, timedelta

last_request = {}


def throttling_middleware(get_response):
    """
    Ограничение обработки запросов пользователя, если он делает обращения слишком часто.
    :param get_response:
    :return:
    """
    def middleware(request: HttpRequest):
        if request.method == "GET":
            client_ip = request.META["REMOTE_ADDR"]
            if client_ip in last_request and datetime.now() - last_request[client_ip] < timedelta(seconds=0.01):
                last_request[client_ip] = datetime.now()
                raise RequestAborted
            request.user_ip = client_ip
            last_request[client_ip] = datetime.now()
        response = get_response(request)
        return response

    return middleware
