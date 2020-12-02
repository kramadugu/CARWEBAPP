#======Importing libraries===================================#
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
#============================================================#


def generate_summary(txt,slen):
    parser = PlaintextParser.from_string(txt,Tokenizer("english"))
    summarizer = TextRankSummarizer()
    summary = summarizer(parser.document, slen)
    return '.'.join([str(k) for k in summary])



