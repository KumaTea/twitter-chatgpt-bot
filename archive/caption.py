# Credit: https://huggingface.co/spaces/SRDdev/Image-Caption

import io
from PIL import Image
from session import logger
from transformers import AutoTokenizer, ViTImageProcessor, VisionEncoderDecoderModel

device = 'cpu'
model_name = 'nlpconnect/vit-gpt2-image-captioning'

# Initialize the feature extractor, tokenizer, and model
feature_extractor = ViTImageProcessor.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = VisionEncoderDecoderModel.from_pretrained(model_name).to(device)


def get_caption(im, max_length=64, num_beams=4):
    """
    Generates a caption for an input image using a pre-trained vision encoder-decoder model.

    Args:
        im: Either a file path or a PIL.Image object.
        max_length: The maximum length of the generated caption.
        num_beams: The number of beams to use for beam search.

    Returns:
        A string containing the generated caption.
    """
    logger.info('Caption: loading image...')
    if isinstance(im, str) or isinstance(im, io.BytesIO):
        # If the input is a file path, open the image using a context manager
        with Image.open(im) as image_file:
            image = image_file.convert('RGB')
            image = feature_extractor(image, return_tensors="pt").pixel_values.to(device)
    elif isinstance(im, Image.Image):
        # If the input is a PIL.Image object, convert it to a tensor and move it to the specified device
        image = feature_extractor(im, return_tensors="pt").pixel_values.to(device)
    else:
        raise ValueError('Invalid input type. Expected file path or PIL.Image object.')

    # Generate the caption using the pre-trained model
    # caption_ids = model.generate(image, max_length=max_length, num_beams=num_beams)[0]
    logger.info('Caption: predicting...')
    caption_ids = model.generate(image, max_length=max_length)[0]
    caption_text = tokenizer.decode(caption_ids)
    caption_text = caption_text.replace('<|endoftext|>', '').split('\n')[0].strip()
    return caption_text
