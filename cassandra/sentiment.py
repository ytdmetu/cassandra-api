from functools import lru_cache

from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline


@lru_cache(maxsize=1)
def make_sentiment_analysis_pipeline():
    print("Creating sentiment analysis pipeline")
    tokenizer = AutoTokenizer.from_pretrained(
        "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
    )
    return pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)


def compute_sentiment_score(x):
    return make_sentiment_analysis_pipeline()(x)


# warmup
make_sentiment_analysis_pipeline()
