from flask import Flask, request, jsonify, render_template
import speech_recognition as sr
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    recognizer = sr.Recognizer()
    
    # Save the uploaded audio file temporarily
    temp_audio_path = 'temp_audio.wav'
    with open(temp_audio_path, 'wb') as temp_audio:
        temp_audio.write(audio_file.read())

    try:
        # Process the audio file in chunks
        with sr.AudioFile(temp_audio_path) as source:
            duration = source.DURATION
            text = ""
            offset = 0
            chunk_size = 30  # seconds

            while offset < duration:
                audio_data = recognizer.record(source, duration=chunk_size, offset=offset)
                try:
                    chunk_text = recognizer.recognize_google(audio_data)
                    text += chunk_text + " "
                except sr.UnknownValueError:
                    text += "[unintelligible] "
                except sr.RequestError:
                    return jsonify({"error": "Speech recognition service unavailable"}), 500
                offset += chunk_size

        os.remove(temp_audio_path)
        return jsonify({"transcription": text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
