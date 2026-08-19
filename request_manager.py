import uuid
from models import DownloadRequest


class RequestManager:
    def create(self, requests: dict, request: DownloadRequest) -> str:
        request_id = str(uuid.uuid4())

        requests[request_id] = request

        return request_id

    def get(self, requests: dict, request_id: str) -> DownloadRequest | None:
        return requests.get(request_id)

    def delete(self, requests: dict, request_id: str) -> None:
        requests.pop(request_id, None)
