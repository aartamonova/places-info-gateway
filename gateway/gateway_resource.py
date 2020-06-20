import functools
import json
import logging

import requests
from flask import make_response, jsonify, request
from flask_api.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_504_GATEWAY_TIMEOUT, \
    HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from flask_restful import Resource
from requests.exceptions import ConnectTimeout, ReadTimeout, Timeout

from config import Config
from gateway.gateway_model import TokenData

logging.basicConfig(filename="log_data.log", level=logging.WARNING, filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')


def request_error_handler(foo):
    @functools.wraps(foo)
    def wrapper(*args):
        try:
            response = foo(*args)
        except (Timeout, ConnectTimeout, ReadTimeout):
            return make_response(jsonify('Истекло время ожидания запроса от сервера'), HTTP_504_GATEWAY_TIMEOUT)
        except:
            return make_response(jsonify('В настоящий момент сервис недоступен'), HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return response

    return wrapper


def response_500_error():
    return make_response(jsonify('В настоящий момент сервис недоступен'), HTTP_500_INTERNAL_SERVER_ERROR)


def return_response(service_response, code=None):
    if code:
        service_response.status_code = code
    try:
        response = make_response(service_response.json, service_response.status_code,
                                 service_response.headers.items())
    except:
        try:
            response = make_response(service_response.content, service_response.status_code,
                                     service_response.headers.items())
        except:
            return response_500_error()
    return response


def get_access_header(request_app):
    '''Сформировать хедер с access-токеном'''
    # Сначала попробовать прочитать из БД, нет/истек - запросить у сервиса авторизации
    token = TokenData.get_by_apps(Config.SOURCE_APP, request_app)
    if token and TokenData.check_token(token):
        return {'Gateway-Token': token.access_token}

    try:
        response = requests.get(Config.AUTH_SERVICE_URL + '/token/get',
                                'source_app=' + Config.SOURCE_APP + '&request_app=' + str(request_app))
        if response.status_code == HTTP_200_OK:
            access_token = json.loads(response.content)['access_token']
            TokenData.save(Config.SOURCE_APP, request_app, access_token)
            return {'Gateway-Token': access_token}
    except:
        return None
    return None


def oauth_token_required(foo):
    @functools.wraps(foo)
    def wrapper(*args, **kwargs):
        '''Access токен из стороннего приложения'''
        if 'App-Token' in request.headers:
            access_token = request.headers['App-Token']
            # Проверить токен
            try:
                response = requests.get(Config.AUTH_SERVICE_URL + '/oauth/token/validate', 'access_token=' +
                                        str(access_token))
            except:
                return make_response(jsonify({'error': 'Invalid authorization data'}), HTTP_403_FORBIDDEN)

            if response.status_code != HTTP_200_OK:
                return make_response(jsonify({'error': 'Invalid authorization data'}), HTTP_403_FORBIDDEN)

            return foo(*args, **kwargs)
        else:
            return make_response(jsonify({'error': 'Invalid authorization data'}), HTTP_403_FORBIDDEN)

    return wrapper


class GatewayTagListResource(Resource):
    @staticmethod
    @request_error_handler
    @oauth_token_required
    def get():
        '''Получить список всех тегов'''
        headers = get_access_header(Config.TAGS_APP)
        logging.warning('Получение списка всех тегов')
        if headers:
            response = requests.get(Config.TAGS_SERVICE_URL + '/tags', headers=headers)
            return return_response(response)
        return response_500_error()


class GatewayOauthTokenResource(Resource):
    @staticmethod
    def post():
        '''Получить токен по коду у сервиса авторизации'''
        try:
            data = json.loads(request.data.decode("utf-8"))
        except:
            return make_response(jsonify({'error': 'Invalid authorization data'}), HTTP_400_BAD_REQUEST)

        response = requests.post(Config.AUTH_SERVICE_URL + '/oauth/token', json.dumps(data))
        logging.warning('Получение токена по коду у сервиса авторизации')
        if response.status_code == HTTP_200_OK:
            return make_response(response.content, HTTP_200_OK)

        return make_response(jsonify({'error': 'Corrupted database data'}), HTTP_500_INTERNAL_SERVER_ERROR)
