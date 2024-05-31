from janome.tokenizer import Tokenizer
from janome.analyzer import Analyzer
from janome.tokenfilter import POSKeepFilter, TokenCountFilter


# 除外ワード
part = ["が", "を", "に", "へ", "と", "より", "から", "で", "や", "の", "みたい", "ん"]
connection = [
    "ば",
    "ながら",
    "ても",
    "けれど",
    "のに",
    "ものの",
    "もの",
    "ところで",
    "ところ",
    "ので",
    "から",
    "し",
    "たり",
    "て",
]
question = ["か", "何", "なん", "どこ", "どう", "なぜ", "どれ", "いつ", "誰", "なに", "どうして", "どのように"]

tokenizer = Tokenizer()
token_filters = [POSKeepFilter(["名詞"]), TokenCountFilter()]


def ranking_words(sentenses):
    result_array = []
    for token in sentenses:
        for result in Analyzer(token_filters=token_filters).analyze(token["message"]):
            result_array.append(result)

    noun_count = {}
    for noun, count in result_array:
        if noun in noun_count:
            noun_count[noun] += count
        else:
            noun_count[noun] = count

    drop_list = part + connection + question

    ordering_dict = sorted(noun_count.items(), key=lambda x: x[1], reverse=True)
    filtered_dict = {key: value for key, value in dict(ordering_dict).items() if key not in drop_list}

    return filtered_dict
