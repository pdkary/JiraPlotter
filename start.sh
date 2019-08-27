start_python () {
    cd python
    source venv/bin/activate
    python start.py
}
start_ui () {
    cd web
    yarn start
}
kill $(lsof -t -i:5000)
kill $(lsof -t -i:4200)
start_python & start_ui