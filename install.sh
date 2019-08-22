install_python () {
    cd python
    pip3 install virtualenv
    virtualenv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
}

install_web () {
    cd web
    npm install yarn
    yarn install
}

install_python & install_web