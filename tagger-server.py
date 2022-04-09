import os

# Disable internet access below if needed
offline_mode = True  # set to True for offline deployment
if offline_mode:
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    os.environ['HF_DATASETS_OFFLINE'] = 'TRUE'
    os.environ['HF_UPDATE_DOWNLOAD_COUNTS'] = 'FALSE'

import sys
import json
import logging
import time
import scipy.special
import numpy as np
from transformers import BertTokenizerFast
from flask import Flask, request, jsonify
from onnxruntime import InferenceSession

cache_dir = 'cache/'
threshold = 0.25  # default for CNNDM is 0.25

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S", level=logging.DEBUG)

start = time.time()
logger.info('Loading model...')
session = InferenceSession("onnx_model/model.onnx", providers=['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider'])  # ranked in priority
logger.info('Loading tokenizer...')
tokenizer = BertTokenizerFast.from_pretrained('bert-large-cased', cache_dir=cache_dir, use_fast=True, local_files_only=offline_mode)
logger.info(f'Model and tokenizer loaded in {time.time() - start} sec')

app = Flask(__name__)


def preprocess(source: str) -> dict:
    """
    Tokenize the source text and cast tokenized numpy array to int64

    Args:
        source (str): input contents for summarization

    Returns:
        (dict): tokenized input contents, attention mask and token type ids in a dict
    """
    inputs = tokenizer(source, return_tensors="np", max_length=512, truncation=True)
    inputs = {k: v.astype(np.int64) for k, v in inputs.items()}
    return inputs


def gen_tags(inputs) -> list:
    """
    Perform inference on the input tokenized text and generate the tags

    Args:
        inputs (dict): tokenized input contents, attention mask and token type ids in a dict (generated by preprocess())

    Returns:
        (list): list of tags
    """
    logits = session.run(output_names=["logits"], input_feed={'input_ids': inputs['input_ids'], 'attention_mask': inputs['attention_mask'], 'token_type_ids': inputs['token_type_ids']})
    logits = np.squeeze(logits, axis=0)  # remove batch dimension which is 1 in this case
    preds = np.argmax(logits, axis=2)
    logits = scipy.special.softmax(logits, axis=2)
    batch_size, seq_len = preds.shape
    preds_prob_list = [logits[0][j][1] for j in range(seq_len)]
    tags = [inputs['input_ids'][0][i] for i in range(len(preds_prob_list)) if preds_prob_list[i] > threshold]
    tags = [tokenizer.decode(tag, skip_special_tokens=True) for tag in tags]
    tags = [tag for tag in tags if len(tag) > 1 and tag.isalpha()]  # filter out non-alphabet and 1-alphabet tags
    return tags


logger.info('Warming up...')  # call the model once first to warm up and load lazy-loaded data into memory
try:
    inputs = preprocess('Hello World')
    tags = gen_tags(inputs)
except:
    pass
logger.info('Warm up done.')


@app.route('/tagger', methods=['POST'])
def tagger():
    try:
        source = request.json
        source = source['source'].replace('\n', ' ').strip()
    except Exception as e:
        return jsonify({'success': 'false', 'error': f'Malformed input: {e}'})
    try:
        inputs = preprocess(source)
    except Exception as e:
        return jsonify({'success': 'false', 'error': f'Failed to preprocess: {e}'})
    try:
        tags = gen_tags(inputs)
    except Exception as e:
        return jsonify({'success': 'false', 'error': f'Failed to predict: {e}'})

    return jsonify({'success': 'true', 'tags': ';'.join(tags)})


@app.route('/health', methods=['GET'])
def health():
    """Sanity check"""
    try:
        inputs = preprocess('Hello World')
        tags = gen_tags(inputs)
        if tags == ['Hello', 'World']:
            return jsonify({'health': 'true'})
    except Exception as e:
        logger.error(f'Health check failed with error {e}')
    return jsonify({'health': 'false'})


if __name__ == '__main__':
    from waitress import serve
    import logging
    server_logger = logging.getLogger('waitress')
    server_logger.setLevel(logging.DEBUG)
    serve(app, host='0.0.0.0', port=8080, expose_tracebacks=False, threads=8)