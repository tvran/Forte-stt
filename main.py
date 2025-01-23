import streamlit as st
import os
from dotenv import load_dotenv
from requests_aws4auth import AWS4Auth
import subprocess
from adjust_audio import convert_audio
from load_file import upload_to_yandex_storage
from recognize import get_request_id, fetch_recognition_results

from transformers.models.auto.modeling_auto import AutoModelForSequenceClassification
from transformers.models.auto.tokenization_auto import AutoTokenizer
from transformers.pipeline import pipeline as TextClassificationPipeline

# Загрузка переменных окружения
load_dotenv()
yandex_api_key = os.getenv("yandex_api_key")
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

REPO_URL = "https://github.com/yandex-cloud/cloudapi.git"
REPO_DIR = "cloudapi"

if not os.path.exists(REPO_DIR):
    subprocess.run(["git", "clone", REPO_URL], check=True)


# Функции для обработки шагов
def step_1_upload_file():
    """
    Шаг 1: Загрузка файла.
    """
    placeholder = st.empty()
    with placeholder.container():
        uploaded_file = st.file_uploader("Загрузите аудиофайл (mp3, wav, flac и т.д.)", type=["wav", "mp3", "flac", "aac", "ogg", "m4a"])
        if uploaded_file is not None:
            local_file = "uploadedaudio.wav"
            with open(local_file, "wb") as f:
                f.write(uploaded_file.read())
            st.success("Файл успешно загружен.")
            return local_file, placeholder
    return None, placeholder

def step_2_convert_audio(input_file):
    """
    Шаг 2: Конвертация аудио.
    """
    placeholder = st.empty()
    with placeholder.container():
        st.write("### Step 1: Обработка аудио...")
        try:
            converted_file = convert_audio(input_file)
            st.success("Аудио успешно обработано.")
            return converted_file, placeholder
        except Exception as e:
            st.error(f"Ошибка обработки аудио: {e}")
            st.stop()
    return None, placeholder

def step_3_upload_to_yandex(converted_file):
    """
    Шаг 3: Загрузка аудио в Yandex Object Storage.
    """
    placeholder = st.empty()
    with placeholder.container():
        st.write("### Step 2: Загрузка аудио на сервер...")
        success, endpoint = upload_to_yandex_storage(
            local_file=converted_file,
            bucket="tvrantest",
            access_key=ACCESS_KEY,
            secret_key=SECRET_KEY
        )
        if success:
            st.success("Аудио успешно загружено.")
            return endpoint, placeholder
        else:
            st.error("Ошибка загрузки аудио на сервер.")
            st.stop()
    return None, placeholder

def step_4_transcription(endpoint):
    """
    Шаг 4: Транскрипция аудио.
    """
    placeholder = st.empty()
    with placeholder.container():
        st.write("### Step 3: Транскрипция аудио...")
        try:
            stub, operation_id = get_request_id(endpoint, yandex_api_key)
            transcribed_text = fetch_recognition_results(stub, operation_id)
            st.success("Транскрипция завершена успешно.")
            st.text_area("Результат транскрипции", transcribed_text, height=300)
            return transcribed_text, placeholder
        except TimeoutError as e:
            st.error(f"Ошибка транскрипции: {e}")
            st.stop()
    return None, placeholder

def step_5_sentiment_analysis(transcribed_text):
    """
    Шаг 5: Анализ сентиментов.
    """
    placeholder = st.empty()
    with placeholder.container():
        st.write("### Step 4: Анализ сентиментов...")
        st.write("Анализируется сентимент каждой реплики...")
        model = AutoModelForSequenceClassification.from_pretrained(
            "issai/rembert-sentiment-analysis-polarity-classification-kazakh",
            token=HF_TOKEN
        )
        tokenizer = AutoTokenizer.from_pretrained(
            "issai/rembert-sentiment-analysis-polarity-classification-kazakh",
            token=HF_TOKEN
        )
        pipe = TextClassificationPipeline(model=model, tokenizer=tokenizer)
        
        # Prepare results for display and download
        results = []
        review_lines = transcribed_text.strip().split('\n')
        for i, line in enumerate(review_lines, 1):
            result = pipe(line)
            sentiment = result[0]['label']
            score = result[0]['score']
            
            # Format result string
            result_str = f"{line} | Сентимент: {sentiment} ({score:.2f})\n"
            results.append(result_str)
        st.empty()
        st.write("### Результат:")
        # Display results
        full_results = "\n".join(results)
        st.text_area("Результаты анализа сентиментов", full_results, height=300)
        
        # Download button
        st.download_button(
            label="Скачать результаты анализа",
            data=full_results,
            file_name="sentiment_analysis_results.txt",
            mime="text/plain"
        )
        
        return placeholder

# Streamlit App
st.title("Работа с аудиозаписями разговоров")
st.write("Загрузите аудиофайл с разговором и получите транскрипцию с анализом сентиментов.")
st.write("Автор: Туран Нургожин.")

# Шаг 1: Загрузка файла
input_file, step_1_placeholder = step_1_upload_file()
if input_file:
    step_1_placeholder.empty()  # Очистить элементы интерфейса для шага 1

    # Шаг 2: Конвертация аудио
    converted_file, step_2_placeholder = step_2_convert_audio(input_file)
    if converted_file:
        step_2_placeholder.empty()  # Очистить элементы интерфейса для шага 2

        # Шаг 3: Загрузка в Yandex Storage
        endpoint, step_3_placeholder = step_3_upload_to_yandex(converted_file)
        if endpoint:
            step_3_placeholder.empty()  # Очистить элементы интерфейса для шага 3

            # Шаг 4: Транскрипция
            transcribed_text, step_4_placeholder = step_4_transcription(endpoint)
            if transcribed_text:
                step_4_placeholder.empty()  # Очистить элементы интерфейса для шага 4
                # Шаг 5: Анализ сентиментов
                step_5_placeholder = step_5_sentiment_analysis(transcribed_text) 