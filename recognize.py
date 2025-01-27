import grpc
import time
from yandex.cloud.ai.stt.v3 import stt_pb2, stt_service_pb2_grpc, stt_service_pb2
from dataclasses import dataclass
from typing import List, Optional
import bisect

@dataclass
class Utterance:
    text: str
    channel: str
    start_time: float
    end_time: float
    speaker: str

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
            audio_processing_type=stt_pb2.RecognitionModelOptions.FULL_DATA,  # Process full audio before results
        ),
    )
    
    response = stub.RecognizeFile(operation_request, metadata=[('authorization', f'Api-Key {Apikey}')])
    return stub, response.id

def merge_utterances(utterances: List[Utterance], time_threshold: float = 0.3) -> List[Utterance]:
    """
    Merge utterances from both channels based on timing overlap.
    """
    if not utterances:
        return []
    
    # Sort utterances by start time
    sorted_utterances = sorted(utterances, key=lambda x: x.start_time)
    merged = []
    current = sorted_utterances[0]
    
    for next_utterance in sorted_utterances[1:]:
        # Check if utterances overlap or are very close in time
        if (next_utterance.start_time - current.end_time) <= time_threshold:
            # Merge overlapping utterances
            current.end_time = max(current.end_time, next_utterance.end_time)
            current.text += f" {next_utterance.text}"
        else:
            merged.append(current)
            current = next_utterance
    
    merged.append(current)
    return merged

def fetch_recognition_results(stub, operation_id, Apikey, timeout=60, interval=2):
    start_time = time.time()
    utterances = []

    request = stt_service_pb2.GetRecognitionRequest(operation_id=operation_id)
    
    while time.time() - start_time < timeout:
        try:
            whole_recognition = stub.GetRecognition(request, metadata=[('authorization', f'Api-Key {Apikey}')])
            
            for response in whole_recognition:
                if response.HasField("final_refinement"):
                    refinement = response.final_refinement
                    text = " ".join([alt.text for alt in refinement.normalized_text.alternatives])
                    channel = refinement.normalized_text.channel_tag
                    
                    # Extract timing information if available
                    start_time = getattr(refinement, 'start_time', 0.0)
                    end_time = getattr(refinement, 'end_time', 0.0)
                    
                    speaker = "Клиент" if channel == "1" else "Оператор"
                    
                    utterance = Utterance(
                        text=text,
                        channel=channel,
                        start_time=start_time,
                        end_time=end_time,
                        speaker=speaker
                    )
                    utterances.append(utterance)
            
            # Merge and sort utterances
            merged_utterances = merge_utterances(utterances)
            
            # Construct final transcript
            full_text = ""
            for utterance in merged_utterances:
                full_text += f"\n{utterance.speaker}: {utterance.text}"
            
            return full_text.strip()
            
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                print(f"Operation {operation_id} is not yet ready.")
            else:
                print(f"An error occurred: {e.code()} - {e.details()}")
            time.sleep(interval)
    
    raise TimeoutError(f"Operation {operation_id} did not complete within {timeout} seconds.")