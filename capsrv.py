# caption server

import io
import logging
from PIL import Image
# from session import logger
from flask import Flask, request, jsonify
from transformers import AutoTokenizer, ViTImageProcessor, VisionEncoderDecoderModel


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

app = Flask(__name__)

device = 'cpu'
model_name = 'nlpconnect/vit-gpt2-image-captioning'

# Initialize the feature extractor, tokenizer, and model
feature_extractor = ViTImageProcessor.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = VisionEncoderDecoderModel.from_pretrained(model_name, low_cpu_mem_usage=True).to(device)
# https://huggingface.co/docs/transformers/main_classes/model#large-model-loading


def get_caption(im, max_length=64, num_beams=4):
    logger.info('Caption: loading image...')
    if isinstance(im, bytes):
        logger.info('  Convert bytes to BytesIO')
        im = io.BytesIO(im)
    if isinstance(im, str) or isinstance(im, io.BytesIO):
        # If the input is a file path, open the image using a context manager
        logger.info('  Convert to PIL.Image')
        with Image.open(im) as image_file:
            image = image_file.convert('RGB')
            image = feature_extractor(image, return_tensors="pt").pixel_values.to(device)
    elif isinstance(im, Image.Image):
        # If the input is a PIL.Image object, convert it to a tensor and move it to the specified device
        image = feature_extractor(im, return_tensors="pt").pixel_values.to(device)
    else:
        raise ValueError(f'Invalid input type: {type(im)}. Expected file path or PIL.Image object.')

    # Generate the caption using the pre-trained model
    # caption_ids = model.generate(image, max_length=max_length, num_beams=num_beams)[0]
    logger.info('Caption: predicting...')
    caption_ids = model.generate(image, max_length=max_length)[0]
    caption_text = tokenizer.decode(caption_ids)
    caption_text = caption_text.replace('<|endoftext|>', '').split('\n')[0].strip()
    return caption_text


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
