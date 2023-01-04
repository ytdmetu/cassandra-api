from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

_sentiment_analysis_pipeline = None


def compute_sentiment_score(x):
    global _sentiment_analysis_pipeline
    if _sentiment_analysis_pipeline is None:
        tokenizer = AutoTokenizer.from_pretrained(
            "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
        )
        model = AutoModelForSequenceClassification.from_pretrained(
            "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
        )
        _sentiment_analysis_pipeline = pipeline(
            "sentiment-analysis", model=model, tokenizer=tokenizer
        )
    return _sentiment_analysis_pipeline(x)
