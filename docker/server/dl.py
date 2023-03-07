from transformers import AutoTokenizer, ViTImageProcessor, VisionEncoderDecoderModel


device = 'cpu'
model_name = 'nlpconnect/vit-gpt2-image-captioning'

feature_extractor = ViTImageProcessor.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = VisionEncoderDecoderModel.from_pretrained(model_name, low_cpu_mem_usage=True).to(device)


if __name__ == '__main__':
    model.eval()
