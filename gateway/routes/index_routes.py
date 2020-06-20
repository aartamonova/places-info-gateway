import hashlib
import json

from flask import Blueprint, render_template, request, make_response, flash
from flask_api.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_403_FORBIDDEN
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired

from config import Config
from gateway.gateway_utils import generate_code_helper

bp = Blueprint('index', __name__)


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired("Пожалуйста, введите логин")])
    password = PasswordField('Пароль', validators=[DataRequired("Пожалуйста, введите пароль")])
    submit = SubmitField('   Войти   ')


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/login/oauth', methods=['GET', 'POST'])
def index():
    login_form = LoginForm()
    try:
        app_id = request.args.get('app_id', type=int)
        redirect_uri = request.args.get('redirect_uri', type=str)
    except:
        return make_response({'error': 'Invalid request data'}, HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        if str(app_id) == str(Config.THIRD_PARTY_APP_ID):
            app_name = Config.THIRD_PARTY_APP
        else:
            app_name = 'Неизвестное приложение'

        request_permission_str = 'Приложение "' + app_name + \
                                 '" запрашивает доступ к вашей учетной записи. Войдите, чтобы продолжить'
        flash(request_permission_str, 'info')

        return render_template('index.html', form=login_form, register_url=Config.REGISTER_URL)
    else:
        login = request.form["login"]
        password = request.form["password"]
        password_hash = hashlib.md5(password.encode()).hexdigest()

        response = generate_code_helper(login, password_hash)
        if response.status_code == HTTP_200_OK:
            code = json.loads(response.content)['code']
            if code:
                return redirect(redirect_uri + '?code=' + code)

        elif response.status_code == HTTP_403_FORBIDDEN:
            flash('Неверный логин или пароль', 'danger')
        else:
            flash('Неуспешная попытка авторизации', 'danger')

        return render_template('index.html', form=login_form, register_url=Config.REGISTER_URL)
