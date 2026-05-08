from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer


def summarize_policy(text, sentence_count=6):
    """
    Generate an extractive summary of the privacy policy
    using TextRank algorithm.
    """

    if not text or len(text.split()) < 100:
        return {
            "summary_text": "Policy text too short to generate a meaningful summary."
        }

    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = TextRankSummarizer()

    summary_sentences = summarizer(parser.document, sentence_count)

    summary_text = " ".join(str(sentence) for sentence in summary_sentences)

    return {
        "summary_text": summary_text
    }
