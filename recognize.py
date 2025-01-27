import grpc
import time
from yandex.cloud.ai.stt.v3 import stt_pb2, stt_service_pb2_grpc, stt_service_pb2

def get_request_id(uri, Apikey):
    cred = grpc.ssl_channel_credentials()
    chan = grpc.secure_channel('stt.api.cloud.yandex.net:443', cred)
    stub = stt_service_pb2_grpc.AsyncRecognizerStub(chan)

    operation_request = stt_pb2.RecognizeFileRequest(
    uri=uri,
    recognition_model=stt_pb2.RecognitionModelOptions(
        model='general:rc',
        audio_format=stt_pb2.AudioFormatOptions(
        container_audio=stt_pb2.ContainerAudio(
            container_audio_type=stt_pb2.ContainerAudio.WAV
        )
        ),
    language_restriction=stt_pb2.LanguageRestrictionOptions(
        restriction_type=stt_pb2.LanguageRestrictionOptions.WHITELIST,
        language_code=['kk-KZ', 'ru-RU']
    ),
    text_normalization=stt_pb2.TextNormalizationOptions(
        text_normalization=stt_pb2.TextNormalizationOptions.TEXT_NORMALIZATION_ENABLED,
        literature_text=True
    ),
    ),
    )
    response = stub.RecognizeFile(operation_request, metadata=[('authorization', f'Api-Key {Apikey}')])
    operation_id = response.id
    return stub, operation_id

def fetch_recognition_results(stub, operation_id, Apikey, timeout=60, interval=2):    
    start_time = time.time()
    replicas = []

    # Build the request for fetching recognition results
    request = stt_service_pb2.GetRecognitionRequest(operation_id=operation_id)
    while time.time() - start_time < timeout:
        try:
            # Stream responses
            whole_recognition = stub.GetRecognition(request, metadata=[('authorization', f'Api-Key {Apikey}')])
            
            for response in whole_recognition:
                if response.HasField("final_refinement"):
                    # Extract text and channel information
                    text = " ".join([alt.text for alt in response.final_refinement.normalized_text.alternatives])
                    channel = response.final_refinement.normalized_text.channel_tag
                    
                    # Create replica object with details
                    replica = {
                        'text': text,
                        'channel': channel
                    }
                    replicas.append(replica)
            
            # Construct final transcript
            full_text = ""
            for replica in replicas:
                speaker = "Клиент" if replica['channel'] == "0" else "Оператор"
                full_text += f"\n{speaker}: {replica['text']}"
            
            return full_text.strip()
        
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                print(f"Operation {operation_id} is not yet ready.")
            else:
                print(f"An error occurred: {e.code()} - {e.details()}")
            time.sleep(interval)
    
    raise TimeoutError(f"Operation {operation_id} did not complete within {timeout} seconds.")