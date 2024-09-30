import os
import wave
import json
from flask import Flask, request, jsonify
from vosk import Model, KaldiRecognizer

# Tạo ứng dụng Flask
app = Flask(__name__)

# Đường dẫn đến mô hình tiếng Việt đã giải nén
MODEL_PATH = "vosk-model-small-vn-0.4"

# Kiểm tra xem mô hình có tồn tại hay không
if not os.path.exists(MODEL_PATH):
    print("Tải mô hình tiếng Việt từ: https://alphacephei.com/vosk/models và giải nén.")
    exit(1)

model = Model(MODEL_PATH)

# Hàm chuyển đổi âm thanh thành văn bản
def transcribe_audio(audio_file):
    wf = wave.open(audio_file, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        return "File âm thanh không hợp lệ. Vui lòng sử dụng tệp mono với tần số mẫu 16000Hz."

    rec = KaldiRecognizer(model, wf.getframerate())
    
    result = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            text = json.loads(rec.Result())['text']
            result.append(text)
    
    final_result = rec.FinalResult()
    result.append(json.loads(final_result)['text'])
    
    return ' '.join(result)

# Tạo route API cho phép POST file âm thanh
@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = "temp.wav"
    file.save(file_path)

    try:
        text_result = transcribe_audio(file_path)
        return jsonify({"text": text_result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app.run()
