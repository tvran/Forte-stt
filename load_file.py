import requests
from requests_aws4auth import AWS4Auth
import datetime

def upload_to_yandex_storage(
    local_file: str,
    bucket: str,
    access_key: str,
    secret_key: str
) -> bool:
    """
    Upload a file to Yandex Object Storage using AWS4 authentication.
    Mirrors the functionality of the working curl command.
    """
    # Endpoint and region
    endpoint = f"https://storage.yandexcloud.net/{bucket}/audio-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
    region = "ru-central1"
    service = "s3"

    # Create AWS4 auth object
    auth = AWS4Auth(
        access_key,
        secret_key,
        region,
        service
    )

    # Read file content
    with open(local_file, 'rb') as file:
        file_data = file.read()

    # Make the PUT request
    try:
        response = requests.put(
            endpoint,
            auth=auth,
            data=file_data,
            headers={
                'Content-Type': 'audio/wav'
            }
        )
        
        if response.status_code in [200, 201]:
            print(f"Successfully uploaded {local_file}")
            print(f"File URL: {endpoint}")
            return True, endpoint
        else:
            print(f"Upload failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False, endpoint
            
    except Exception as e:
        print(f"Upload failed: {str(e)}")
        return False, endpoint