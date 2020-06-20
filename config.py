import os

root_dir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # Database settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(root_dir, 'gateway_data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Services settings
    GUI_SERVICE_URL = 'https://places-info.herokuapp.com'
    AUTH_SERVICE_URL = 'https://places-info-auth.herokuapp.com'
    TAGS_SERVICE_URL = 'https://places-info-tags.herokuapp.com'
    PLACES_SERVICE_URL = 'https://places-info-places.herokuapp.com'

    REGISTER_URL = GUI_SERVICE_URL + '/register'

    # Other settings
    SOURCE_APP = 'gateway'
    PLACES_APP = 'places'
    TAGS_APP = 'tags'
    THIRD_PARTY_APP = 'Third party app example'
    THIRD_PARTY_APP_ID = '2236408341746309'
    JSON_AS_ASCII = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    SECRET_KEY = 'places-info-gateway-secret-key'
