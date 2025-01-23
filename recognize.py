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
    speaker_labeling=stt_pb2.SpeakerLabelingOptions(
        speaker_labeling=stt_pb2.SpeakerLabelingOptions.SPEAKER_LABELING_ENABLED
    )
    )
    response = stub.RecognizeFile(operation_request, metadata=[('authorization', f'Api-Key {Apikey}')])
    operation_id = response.id
    return stub, operation_id

def fetch_recognition_results(stub, operation_id, timeout=60, interval=2):    
    start_time = time.time()
    full_text = ""

    # Build the request for fetching recognition results
    request = stt_service_pb2.GetRecognitionRequest(operation_id=operation_id)
    while time.time() - start_time < timeout:
        try:
            # Stream responses
            whole_recognition = stub.GetRecognition(request, metadata=[('authorization', 'Api-Key AQVN2yNJ6b2rUQp6U5smoMiBgKZeuYD8mqaKQgsj')])
            speaker = "1"
            for response in whole_recognition:
    # Check where channel_tag exists
                if response.HasField("final_refinement"):
                    new_speaker = response.final_refinement.normalized_text.channel_tag  # Adjust this based on the structure
                    if speaker == new_speaker:
                        full_text += "\n" + "Оператор: "
                        for alternative in response.final_refinement.normalized_text.alternatives:
                            full_text += alternative.text + " "
                    else:
                        full_text += "\n" + "Клиент: "
                        for alternative in response.final_refinement.normalized_text.alternatives:
                            full_text += alternative.text + " "
                else:
                    print("No final_refinement in this response")
            return full_text.strip()
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                print(f"Operation {operation_id} is not yet ready.")
            else:
                print(f"An error occurred: {e.code()} - {e.details()}")
            time.sleep(interval)
    raise TimeoutError(f"Operation {operation_id} did not complete within {timeout} seconds.")