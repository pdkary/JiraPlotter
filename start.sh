start_python () {
    cd python
    pip3 install virtualenv
    virtualenv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
    python setup.py bdist_wheel
    pip3 install flaskr-1.0.0-py3-none-any.whl
    export FLASK_APP=flaskr
    flask init-db
    waitress-serve --call 'flaskr:create_app'
}

start_ui () {
    cd web
    yarn install
    yarn start
}

start_python & start_ui