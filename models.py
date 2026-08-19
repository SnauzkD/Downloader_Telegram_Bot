from dataclasses import dataclass

@dataclass
class DownloadRequest:
    url:str
    info: dict
    platform:str