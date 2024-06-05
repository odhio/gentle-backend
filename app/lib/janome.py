from collections import Counter
import itertools
from typing import Optional
import numpy as np
import pandas as pd

from janome.tokenizer import Tokenizer
from janome.tokenfilter import POSKeepFilter, TokenCountFilter

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

# 除外ワード
# 英数字1文字とかもノイズになりがちなので除外した方が良いかもしれませんが要件次第なので一応一般的なものを列挙しました
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
question = [
    "か",
    "何",
    "なん",
    "どこ",
    "どちら",
    "どう",
    "なぜ",
    "どの",
    "どれ",
    "いつ",
    "誰",
    "だれ",
    "だれか",
    "誰か",
    "なに",
    "なにか",
    "何か",
    "どうして",
    "どのように",
    "どのくらい",
    "どのぐらい",
    "どうして",
    "どうやって",
    "どのように",
]

other = [
    "あー",
    "ああ",
    "そう",
    "うん",
    "ええ",
    "これ",
    "それ",
    "あれ",
    "ここ",
    "そこ",
    "よう",
    "あそこ",
    "こちら",
    "みんな",
    "何も",
    "なにも",
    "どうか",
    "どうも",
]

t = Tokenizer()

cv = CountVectorizer(token_pattern="(?u)\\b\\w+\\b")
tv = TfidfVectorizer()


def tokenize_sentences(sentences: str) -> list[str]:
    result_array = []
    for token in t.tokenize(sentences):
        part_of_speech = token.part_of_speech.split(",")[0]
        # 動詞が必要な場面もあるとおもいますがノイズが結構多かったのでクレンジングと併せて要検討。一旦ハンドリングが容易な名詞のみ
        if part_of_speech in ["名詞"]:
            result_array.append(token.surface)

    drop_list = part + connection + question + other
    result_array = [x for x in result_array if x not in drop_list]

    return result_array


# Topic/ Sentiment Analysis
def ranking_words(sentences: list[str]) -> dict[str, int]:
    result_array = []
    for sentence in sentences:
        if sentence != "":
            result_array.extend(tokenize_sentences(sentence))
        else:
            continue

    noun_count = Counter(result_array)

    return noun_count


# All Sentences Trend Analysis
def create_term_document_matrix(sentences: list[str]) -> dict[str, int]:
    """
    INPUT:
        [str, str, str, ...]
    OUTPUT:
        {'単語１': 5, '単語２': 4, '単語３': 3, ...
    """
    target_list = []
    for sentence in sentences:
        target_list.append(" ".join(tokenize_sentences(sentence)))

    # センテンス毎の単純集計
    X = cv.fit_transform(target_list)
    feature_names = cv.get_feature_names_out()

    # 1次元配列化
    word_counts = np.asarray(X.sum(axis=0)).reshape(-1)

    # 出現順
    df = pd.DataFrame(word_counts, index=feature_names, columns=["simple_count"])
    df = df.sort_values(by="simple_count", ascending=False)

    return df.head(20).to_dict().get("simple_count")


def create_tfidf_matrix(sentences: list[str]) -> dict[str, float]:
    """
    INPUT:
        [str, str, str, ...]
    OUTPUT:
        {'単語１': 2.4321004085182274, '単語２': 1.661562462753031, ...
    """
    print(sentences)
    target_list = []
    for sentence in sentences:
        target_list.append(" ".join(tokenize_sentences(sentence)))

    # センテンス毎のscore
    X = tv.fit_transform(target_list)
    feature_names = tv.get_feature_names_out()

    # 1次元配列化
    word_counts = np.asarray(X.sum(axis=0)).reshape(-1)

    # 単語毎のスコア順
    df = pd.DataFrame(word_counts, index=feature_names, columns=["tfidf_score"])
    df = df.sort_values(by="tfidf_score", ascending=False)

    return df.head(20).to_dict().get("tfidf_score")


def create_term_combination(sentences: list[str]) -> dict[str, dict[int, str | int]]:
    sentences = [tokenize_sentences(text) for text in sentences]
    print(sentences)
    sentences_combs = [list(itertools.combinations(sentence, 2)) for sentence in sentences]
    words_combs = [[tuple(sorted(words)) for words in sentence] for sentence in sentences_combs]
    target_combs = []
    for words_comb in words_combs:
        target_combs.extend(words_comb)

    ct = Counter(target_combs)

    df = pd.DataFrame([{"col_1": i[0][0], "col_2": i[0][1], "count": i[1]} for i in ct.most_common()])
    df.head(20)
    return df.head(20).to_dict()
