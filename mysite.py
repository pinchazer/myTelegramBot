from flask import Flask
from flask_sslify import SSLify

app = Flask(__name__)
sslify = SSLify(app)

@app.route('/')
def hello_world():
    return '<p style="text-align: center;"><strong>КУКУ ЕПТА)</strong></p>'

if __name__ == '__main__':
    app.run()