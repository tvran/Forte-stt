import grpc
from yandex.cloud.ai.stt.v3 import stt_pb2, stt_service_pb2_grpc, stt_service_pb2 
from google.protobuf.json_format import MessageToJson
import json

request = stt_service_pb2.GetRecognitionRequest(
    operation_id="f8dp0tq036pt6b7lcm9c"
)

cred = grpc.ssl_channel_credentials()
chan = grpc.secure_channel('stt.api.cloud.yandex.net:443', cred)
stub = stt_service_pb2_grpc.AsyncRecognizerStub(chan)

# Аутентификация с API-ключом
response = stub.GetRecognition(request, metadata=[('authorization', 'Api-Key AQVN2yNJ6b2rUQp6U5smoMiBgKZeuYD8mqaKQgsj')])

def save_streaming_response_to_json(stream, filename="streaming_response.json"):
    """
    Processes a stream of StreamingResponse messages, converts them to JSON,
    and saves them to a file.

    Args:
        stream: The stream of StreamingResponse objects (e.g., from gRPC stub).
        filename: The name of the JSON file to save the responses.

    Returns:
        None
    """
    responses = []

    try:
        # Iterate over the stream
        for response in stream:
            # Convert each response to JSON
            response_json = MessageToJson(response)
            responses.append(json.loads(response_json))  # Append as a Python dict

        # Write all responses to a JSON file
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(responses, file, ensure_ascii=False, indent=4) 

        print(f"StreamingResponse data saved to {filename}")
    
    except Exception as e:
        print(f"Error processing stream: {e}")


# Example usage
save_streaming_response_to_json(response)