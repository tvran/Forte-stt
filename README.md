# 🎙 STTSSTTSSTTSSTTS: Speech-to-Text & Sentiment Analysis

🚀 **STTSSTTSSTTSSTTSS** is a tool for transcribing audio files and analyzing sentiment using **Yandex SpeechKit**, **RemBERT** trained on KazSAnDRA dataset created by ISSAI, and **Streamlit**.

## 📌 Features
- ✅ **Transcribe audio files** (WAV, MP3, FLAC, etc.)
- ✅ **Sentiment analysis** (positive, neutral, negative)
- ✅ **Supports Kazakh and Russian languages**
- ✅ **User-friendly UI with Streamlit**
- ✅ **Leverages Yandex Cloud API as a submodule**

---

## 📥 Installation & Setup

### 🔧 Prerequisites
- **Python 3.12** (Ensure Python 3.12 is installed)
- **FFmpeg** (Required for audio processing)
  ```bash
  sudo apt install ffmpeg  # Linux
  brew install ffmpeg      # macOS
  ```
- **Git** (For cloning the repository and initializing submodules)

---

### 🚀 Clone the Repository
Since this project uses Yandex Cloud API as a **submodule**, use:
```bash
git clone --recurse-submodules https://github.com/tvran/Forte-stt.git
cd Forte-stt
```
If you have already cloned the repo without submodules, initialize it manually:
```bash
git submodule update --init --recursive
```

---

### 🛠 Generate gRPC Client Interface
To use **Yandex SpeechKit**, you need to generate the **gRPC client interface**.

#### 1️⃣ Install `grpcio-tools`
```bash
pip install grpcio-tools
```

#### 2️⃣ Run the following command inside the **Forte-STT** directory:
```bash
python3 -m grpc_tools.protoc -I cloudapi -I cloudapi/third_party/googleapis \
  --python_out=output \
  --grpc_python_out=output \
  cloudapi/google/api/http.proto \
  cloudapi/google/api/annotations.proto \
  cloudapi/yandex/cloud/api/operation.proto \
  cloudapi/google/rpc/status.proto \
  cloudapi/yandex/cloud/operation/operation.proto \
  cloudapi/yandex/cloud/validation.proto \
  cloudapi/yandex/cloud/ai/stt/v3/stt_service.proto \
  cloudapi/yandex/cloud/ai/stt/v3/stt.proto
```
This will generate necessary Python files in `output/`:
- `stt_pb2.py`
- `stt_pb2_grpc.py`
- `stt_service_pb2.py`
- `stt_service_pb2_grpc.py`

---

### 📦 Install Dependencies
Activate a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Then, install the required dependencies:
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Project
### **Start the Streamlit UI**
```bash
streamlit run main.py
```
If deploying on a server, use:
```bash
streamlit run main.py --server.port 8501
```

---

## 🚀 Setting up API Keys
### **To use Yandex SpeechKit and Hugging Face Transformers, you need to store API keys securely.**

1️⃣ Create a .env file in the root of the project

2️⃣ Add your API keys inside .env:
```
# Yandex SpeechKit API Key
YANDEX_API_KEY=your_yandex_api_key_here

# Yandex Object Storage Keys
ACCESS_KEY=your_access_key_here
SECRET_KEY=your_secret_key_here

# Hugging Face Token (for sentiment analysis)
HF_TOKEN=your_huggingface_token_here
```

---

## 📂 Project Structure
```
Forte-stt/
│── output/                  # Audio processing & recognition logic
│   ├── adjust_audio.py       # Converts audio to 16kHz PCM
│   ├── load_file.py          # Uploads to Yandex Cloud Storage
│   ├── recognize.py          # Handles Yandex SpeechKit transcription
│   ├── stt_pb2.py            # gRPC-generated file
│   ├── stt_service_pb2.py    # gRPC-generated file
│── cloudapi/                 # Yandex Cloud API (submodule)
│── main.py                   # Streamlit UI
│── requirements.txt          # Python dependencies
│── README.md                 # Documentation
```

---

## 🛠 Technologies Used
- **Python 3.12**
- **Streamlit** – UI for audio processing
- **Yandex SpeechKit** – Speech-to-Text processing
- **Hugging Face Transformers** – Sentiment analysis
- **FFmpeg** – Audio conversion
- **gRPC** – Communication with Yandex API

---

## 📞 Contact
👤 **Turan Nurgozhin**  
📧 Email: **turannurgozhin@gmail.com**  
🔗 LinkedIn: [https://www.linkedin.com/in/turan-nurgozhin-81931428b/](https://linkedin.com)  
🚀 GitHub: [github.com/tvran](https://github.com/tvran/)
