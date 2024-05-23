import torchaudio
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification
import librosa
import os
import uuid
import torch

import ffmpeg


model_path = "Konik-Y/wav2vec2-lg-960-ser-jp"
feature_extractor = AutoFeatureExtractor.from_pretrained(model_path)
audio_model = AutoModelForAudioClassification.from_pretrained(model_path)
audio_model.eval()

# ベースモデルの設定 / サンプル間の誤差修正
sampling_rate = 16000
max_duration = 5.0


# モデルと推論データの一時保存場所の一貫性保持 GPUモードで大体1秒かからず推論完了します
if torch.cuda.is_available():
    audio_model = audio_model.to("cuda")
    MODE_DEVICE = "cuda"
    print("GPU is available.")
else:
    audio_model = audio_model.to("cpu")
    MODE_DEVICE = "cpu"
    print("GPU is not available.")


def _convert_to_wav(file_path, output_path):
    try:
        # ファイルを読み込んで変換(ブラウザからの形式はwebmの可能性があるため追加)
        ffmpeg.input(file_path).output(output_path, format="wav").run()

    except ffmpeg.Error as e:
        print(f"An error occurred: {e.stderr}")


def _save_audio(audio_data):
    save_directory = os.path.join(".", "temp")
    os.makedirs(save_directory, exist_ok=True)

    saved_audio_path = os.path.join(save_directory, str(uuid.uuid4()) + ".wav")
    temp_path = os.path.join(save_directory, str(uuid.uuid4()) + ".wav")

    with open(saved_audio_path, "wb") as f:
        f.write(audio_data)

    _convert_to_wav(saved_audio_path, temp_path)

    return temp_path


def _remove_audio_file(audio_path):
    os.remove(audio_path)


# インプットデータの前処理
def _preprocess_audio(sample):
    wv, sr = torchaudio.load(sample)
    rms = torch.sqrt((wv**2).mean()).item()
    wv = wv.squeeze().numpy()  # Convert to 1D array

    # サンプリングレート変換
    if sr != sampling_rate:
        wv = librosa.resample(wv, orig_sr=sr, target_sr=sampling_rate)
        sr = sampling_rate

    # トリミング
    num_samples = int(max_duration * sr)
    if wv.shape[0] > num_samples:
        wv = wv[:num_samples]

    # 特徴量抽出
    inputs = feature_extractor(wv, sampling_rate=sr, return_tensors="pt", padding=True)
    return inputs, rms


def _predict_labels(file):
    inputs, rms = _preprocess_audio(file)
    if MODE_DEVICE == "cuda":
        inputs = {key: value.to("cuda") for key, value in inputs.items()}
    elif MODE_DEVICE == "cpu":
        inputs = {key: value.to("cpu") for key, value in inputs.items()}

    # 推論
    with torch.no_grad():
        print(
            inputs
        )  # OUTPUT: {'input_values': tensor([[ 0.0043,  0.0080,  0.0074,  ..., -0.1806,  0.1078, -0.0112]],device='cuda:0')}
        logits = audio_model(input_values=inputs["input_values"]).logits
    # 結果
    predictions = torch.argmax(logits, dim=-1)
    return [audio_model.config.id2label[pred.item()] for pred in predictions], rms


def predict(audio: bytes):
    try:
        if audio_model is None:
            raise Exception("Model is not loaded.")
        audio = _save_audio(audio)
        emotions, pressure = _predict_labels(audio)
        _remove_audio_file(audio)
        return emotions, pressure

    except Exception as e:
        raise Exception(str(e))
