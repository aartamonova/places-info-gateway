import functools

import requests
from flask import abort, jsonify, make_response
from flask_api.status import (HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN,
                              HTTP_500_INTERNAL_SERVER_ERROR, HTTP_504_GATEWAY_TIMEOUT)
from requests.exceptions import ConnectTimeout, ConnectionError, ReadTimeout, Timeout

from config import Config


def request_error_handler(foo):
    @functools.wraps(foo)
    def wrapper(*args):
        response = None
        try:
            response = foo(*args)
        except ConnectionError:
            response = make_response(jsonify('В настоящий момент сервис недоступен'), HTTP_500_INTERNAL_SERVER_ERROR)
        except (Timeout, ConnectTimeout, ReadTimeout):
            return make_response(jsonify('Истекло время ожидания запроса от сервера'), HTTP_504_GATEWAY_TIMEOUT)
        except:
            abort(404)

        if response.status_code == HTTP_401_UNAUTHORIZED:
            abort(403)
        if response.status_code == HTTP_403_FORBIDDEN:
            return make_response(jsonify('Доступ запрещен'), HTTP_403_FORBIDDEN)
        if response.status_code == HTTP_500_INTERNAL_SERVER_ERROR:
            return make_response(jsonify('В настоящий момент сервис недоступен'), HTTP_500_INTERNAL_SERVER_ERROR)
        if response.status_code == HTTP_400_BAD_REQUEST:
            return make_response(jsonify('Неверные данные. Пожалуйста, '
                                         'проверьте введенные данные '
                                         'и попробуйте еще раз'), HTTP_400_BAD_REQUEST)
        else:
            return response

    return wrapper


@request_error_handler
def generate_code_helper(login, password_hash):
    '''Получить код по логину и хешу пароля'''
    response = requests.get(Config.AUTH_SERVICE_URL + '/auth/code' + '?login=' +
                            login + '&password_hash=' + password_hash)
    return response
