from collections import Counter
import numpy as np
import pandas as pd

from janome.tokenizer import Tokenizer
from janome.tokenfilter import POSKeepFilter, TokenCountFilter

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

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


t = Tokenizer()

cv = CountVectorizer(token_pattern="(?u)\\b\\w+\\b")
tf_idf = TfidfVectorizer()


def tokenize_sentences(sentences: str) -> list[str]:
    result_array = []
    for token in t.tokenize(sentences):
        part_of_speech = token.part_of_speech.split(",")[0]
        # 動詞が必要な場面もあるとおもいますがノイズが結構多かったのでクレンジングと併せて要検討。一旦ハンドリングが容易な名詞のみ
        if part_of_speech in ["名詞"]:
            result_array.append(token.surface)

    return result_array


# Topic/ Sentiment Analysis
def ranking_words(sentences: list[str]) -> dict[str, int]:
    result_array = tokenize_sentences(sentences)
    noun_count = Counter(result_array)

    drop_list = part + connection + question
    filtered_dict = {key: value for key, value in dict(noun_count).items() if key not in drop_list}

    return filtered_dict


# All Sentences Trend Analysis
def create_term_document_matrix(sentences: list[str]) -> pd.DataFrame:
    """
    INPUT:
        [str, str, str, ...]
    OUTPUT:
        DataFrame
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
    df = pd.DataFrame(word_counts, index=feature_names, columns=["sumple_count"])
    df.sort_values(by="sumple_count", ascending=False)

    return df


def create_tfidf_matrix(sentences: list[str]) -> pd.DataFrame:
    """
    INPUT:
        [str, str, str, ...]
    OUTPUT:
        DataFrame
    """
    target_list = []
    for sentence in sentences:
        target_list.append(" ".join(tokenize_sentences(sentence)))

    # センテンス毎のscore
    X = tf_idf.fit_transform(target_list)
    feature_names = tf_idf.get_feature_names_out()

    # 1次元配列化
    word_counts = np.asarray(X.sum(axis=0)).reshape(-1)

    # 単語毎のスコア順
    df = pd.DataFrame(word_counts, index=feature_names, columns=["tfidf_score"])
    df = df.sort_values(by="tfidf_score", ascending=False)
    print(df)

    return df
