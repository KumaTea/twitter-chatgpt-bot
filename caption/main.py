from session import *
from capsrv import get_caption
from flask import Flask, request, jsonify


app = Flask(__name__)


@app.route('/caption', methods=['POST'])
def respond():
    if request.method == 'POST':
        logger.info('Caption: received request...')
        if request.files:
            image = request.files['image'].read()
            caption = get_caption(image)
            logger.info('Caption: responding...')
            return jsonify({'caption': caption})
        else:
            return jsonify({'error': 'No image received.'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=14500, debug=False)
