Склонируйте репозиторий Yandex Cloud API:

git clone https://github.com/yandex-cloud/cloudapi

Перейдите в папку output и сгенерируйте в ней код интерфейса клиента:

cd <путь_к_папке_cloudapi>
python3 -m grpc_tools.protoc -I . -I third_party/googleapis \
  --python_out=output \
  --grpc_python_out=output \
  google/api/http.proto \
  google/api/annotations.proto \
  yandex/cloud/api/operation.proto \
  google/rpc/status.proto \
  yandex/cloud/operation/operation.proto \
  yandex/cloud/validation.proto \
  yandex/cloud/ai/stt/v3/stt_service.proto \
  yandex/cloud/ai/stt/v3/stt.proto

В папке output будут созданы файлы с интерфейсом клиента: stt_pb2.py, stt_pb2_grpc.py, stt_service_pb2.py, stt_service_pb2_grpc.py и файлы зависимостей.