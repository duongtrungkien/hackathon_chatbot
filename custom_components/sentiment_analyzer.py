from rasa.nlu.components import Component
from typing import Any, Optional, Text, Dict
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.constants import INTENT, TEXT
import torch as pt
import logging
from transformers import BertForSequenceClassification, BertTokenizerFast

logger = logging.getLogger(__name__)


class SentimentPredictor:
    """Class for sentiment analysis prediction."""

    def __init__(self, model_save_dir, device="cuda"):
        """Init method for our SentimentPredictor.

        Args:
             model_save_dir: Directory where the pre-trained model is saved.
             device: Will the model be loaded on gpu ("cuda") or "cpu".
        """
        self.model_save_dir = model_save_dir
        self.device = device
        if device not in ("cuda", "cpu"):
            raise ValueError(
                'Devce value can either be "cuda" for gpu usage or "cpu"')
        self.tokenizer = None
        self.model = None

    def load_pretrained_sentiment_model(self):
        """Fucntion to load our pretrained sentiment analysis model. The pretrained model uses FinBERT."""

        self.tokenizer = BertTokenizerFast.from_pretrained(
            'TurkuNLP/bert-base-finnish-uncased-v1', do_lowercase=True)
        self.model = BertForSequenceClassification.from_pretrained(
            self.model_save_dir)
        self.model.to(self.device)

    def predict_sentiment(self, text_list):
        """Return the sentiment of list of text segments using the pre-loaded tokenizer and model. This will return a list of sentiments.

        Args:
             text_list: List of strings for which we want to get the sentiment.
        """

        label_map = {0: 'Negative', 1: 'Neutral', 2: 'Positive'}
        logger.debug(text_list)
        tokenized_data = self.tokenizer(
            text_list, truncation=True, padding=True, return_tensors='pt')
        tokenized_data.to(self.device)
        logits = self.model(**tokenized_data, return_dict=True).logits
        y = pt.argmax(logits, dim=1)
        return label_map[y.numpy().tolist()[0]]


class SentimentAnalyzer(Component):
    """A pre-trained sentiment component"""

    name = "sentiment"
    provides = ["entities"]
    requires = []
    defaults = {}
    language_list = ["fi"]

    def __init__(self, component_config=None):
        super(SentimentAnalyzer, self).__init__(component_config)

    def train(self, training_data, cfg, **kwargs):
        """Not needed, because the the model is pretrained"""
        pass

    def convert_to_rasa(self, value, confidence):
        """Convert model output into the Rasa NLU compatible output format."""

        entity = {"value": value,
                  "confidence": confidence,
                  "entity": "sentiment",
                  "extractor": "sentiment_extractor"}

        return entity

    def process(self, message: Message, **kwargs):
        """Retrieve the text message, pass it to the classifier
            and append the prediction results to the message class."""

        dt = message.as_dict()
        if TEXT in dt:
            sp = SentimentPredictor(
                '/Users/kien1/Documents/Projects/hackathon_demo/custom_components/pretrain_sent_model', device="cpu")
            sp.load_pretrained_sentiment_model()
            sentiment = sp.predict_sentiment([dt[TEXT]])

            entity = self.convert_to_rasa(sentiment, 1)

            message.set("entities", [entity], add_to_output=True)

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        pass
