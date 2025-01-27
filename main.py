import streamlit as st
import os
from dotenv import load_dotenv
from requests_aws4auth import AWS4Auth
import subprocess
import torch

from adjust_audio import convert_audio
from load_file import upload_to_yandex_storage
from recognize import get_request_id, fetch_recognition_results

from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer
from transformers import TextClassificationPipeline

# Загрузка переменных окружения
load_dotenv()
yandex_api_key = os.getenv("yandex_api_key")
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

REPO_URL = "https://github.com/yandex-cloud/cloudapi.git"
REPO_DIR = "cloudapi"

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

model = None
tokenizer = None
pipe = None

if not os.path.exists(REPO_DIR):
    subprocess.run(["git", "clone", REPO_URL], check=True)

def delete_temp_files():
    temp_files = ["uploadedaudio.wav", "converted_audio.wav"]
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def initialize_sentiment_model():
    """
    Initialize the sentiment analysis model and tokenizer once.
    """
    global model, tokenizer, pipe
    
    if model is None or tokenizer is None or pipe is None:
        model = AutoModelForSequenceClassification.from_pretrained(
            "issai/rembert-sentiment-analysis-polarity-classification-kazakh",
            token=HF_TOKEN,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
            device_map="cpu"
        )
        tokenizer = AutoTokenizer.from_pretrained(
            "issai/rembert-sentiment-analysis-polarity-classification-kazakh",
            token=HF_TOKEN
        )
        pipe = TextClassificationPipeline(model=model, tokenizer=tokenizer)


def step_1_upload_file():
    """
    Шаг 1: Загрузка файла.
    """
    uploaded_file = st.file_uploader(
        "Загрузите аудиофайл (mp3, wav, flac и т.д.)", 
        type=["wav", "mp3", "flac", "aac", "ogg", "m4a"],
        key="file_uploader"  # Add a unique key
    )
    
    if uploaded_file is not None:
        local_file = "uploadedaudio.wav"
        with open(local_file, "wb") as f:
            f.write(uploaded_file.read())
        st.success("Файл успешно загружен.")
        return local_file
    return None
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
            transcribed_text = fetch_recognition_results(stub, operation_id, yandex_api_key)
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
        
        # Initialize model if not already loaded
        initialize_sentiment_model()

        table_data = []  
        review_lines = transcribed_text.strip().split('\n')
        
        # Add a progress bar
        progress_bar = st.progress(0)
        
        for i, line in enumerate(review_lines, 1):
            # Split the line into speaker and text
            if ': ' in line:
                speaker, text = line.split(': ', 1)
            else:
                speaker, text = 'Unknown', line

            result = pipe(text)
            label = result[0]['label']
            score = result[0]['score']

            # Determine sentiment based on score
            # Determine sentiment based on score
            if label == 'POSITIVE' and score > 0.66:
                sentiment = 'POSITIVE'
            elif label == 'POSITIVE' and score <= 0.66:
                sentiment = 'NEUTRAL'
            elif label == 'NEGATIVE' and score > 0.66:
                sentiment = 'NEGATIVE'
            else:
                sentiment = 'NEUTRAL'
            
            # Store structured data
            table_data.append({
                "Говорящий": speaker,
                "Текст": text,
                "Сентимент": sentiment,
                "Оценка": f"{score:.2f}"
            })
            
            # Update progress bar
            progress_bar.progress((i / len(review_lines)))
        
        # Clear progress bar
        progress_bar.empty()
        
        st.write("### Результат:")
        # Display results as a table
        st.dataframe(
            table_data,
            column_config={
                "Говорящий": st.column_config.TextColumn("Говорящий", width="medium"),
                "Текст": st.column_config.TextColumn("Текст", width="large"),
                "Сентимент": st.column_config.TextColumn("Сентимент", width="medium"),
                "Оценка": st.column_config.TextColumn("Оценка", width="small")
            },
            hide_index=True
        )
        
        # Create two columns for the download buttons
        col1, col2 = st.columns(2)
        
        # Text file download button in first column
        with col1:
            # Convert table data to text format for .txt download
            text_results = "\n".join([
                f"{row['Говорящий']}: {row['Текст']} | Сентимент: {row['Сентимент']} ({row['Оценка']})"
                for row in table_data
            ])
            st.download_button(
                label="Скачать как текст",
                data=text_results,
                file_name="sentiment_analysis_results.txt",
                mime="text/plain"
            )
        
        # CSV download button in second column
        with col2:
            # Prepare CSV data
            import io
            import csv
            
            csv_output = io.StringIO()
            writer = csv.writer(csv_output)
            writer.writerow(['Говорящий', 'Текст', 'Сентимент', 'Оценка'])  # Header row
            for row in table_data:
                writer.writerow([row['Говорящий'], row['Текст'], row['Сентимент'], row['Оценка']])
            
            st.download_button(
                label="Скачать как CSV",
                data=csv_output.getvalue(),
                file_name="sentiment_analysis_results.csv",
                mime="text/csv"
            )

        return placeholder

def main():
    st.title("Работа с аудиозаписями разговоров")
    st.write("Загрузите аудиофайл с разговором и получите транскрипцию с анализом сентиментов.")
    st.write("Автор: Туран Нургожин.")

    # Reset button at the top
    if st.button("Начать новый анализ", key="reset_button"):  # Add a unique key
        # Clear temporary files
        delete_temp_files()
        # Clear session state
        st.session_state.clear()
        # Clear query params
        st.query_params.clear()
        # Force rerun
        st.rerun()

    # Main workflow
    if 'input_file' not in st.session_state:
        input_file = step_1_upload_file()  # Remove placeholder
        if input_file:
            st.session_state['input_file'] = input_file

    if 'input_file' in st.session_state and 'converted_file' not in st.session_state:
        converted_file, step_2_placeholder = step_2_convert_audio(st.session_state['input_file'])
        if converted_file:
            st.session_state['converted_file'] = converted_file
            step_2_placeholder.empty()

    if 'converted_file' in st.session_state and 'endpoint' not in st.session_state:
        endpoint, step_3_placeholder = step_3_upload_to_yandex(st.session_state['converted_file'])
        if endpoint:
            st.session_state['endpoint'] = endpoint
            step_3_placeholder.empty()

    if 'endpoint' in st.session_state and 'transcribed_text' not in st.session_state:
        transcribed_text, step_4_placeholder = step_4_transcription(st.session_state['endpoint'])
        if transcribed_text:
            st.session_state['transcribed_text'] = transcribed_text
            step_4_placeholder.empty()

    if 'transcribed_text' in st.session_state:
        step_5_sentiment_analysis(st.session_state['transcribed_text'])

# In your main.py
if __name__ == "__main__":
    # Initialize the model when the app starts
    initialize_sentiment_model()
    main()