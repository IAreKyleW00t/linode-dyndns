import json
import requests

LINODE_API_URL = "https://api.linode.com/v4"


class LinodeClient:
    _token = None

    def __init__(self, token: str) -> None:
        self._token = token

    def request(self, method: str, path: str, **kwargs) -> tuple:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self._token}",
        }

        if "headers" in kwargs:
            headers = headers | kwargs.pop("headers")

        req = requests.request(
            method,
            f"{LINODE_API_URL}{path}",
            headers=headers,
            **kwargs,
        )

        return req.status_code, req.json()

    def get_domains(self) -> tuple:
        return self.request("GET", "/domains")

    def get_domain_records(self, domain_id: str) -> tuple:
        return self.request("GET", f"/domains/{domain_id}/records")

    def create_domain_record(
        self,
        domain_id: str,
        name: str,
        type: str,
        target: str,
        port: int = None,
        priority: int = None,
        protocol: str = None,
        service: str = None,
        tag: str = None,
        ttl_sec: int = None,
        weight: int = None,
    ) -> tuple:
        data = {"type": type, "name": name, "target": target}
        if port:
            data["port"] = port
        if priority:
            data["priority"] = priority
        if protocol:
            data["protocol"] = protocol
        if service:
            data["service"] = service
        if tag:
            data["tag"] = tag
        if ttl_sec:
            data["ttl_sec"] = ttl_sec
        if weight:
            data["weight"] = weight

        return self.request("POST", f"/domains/{domain_id}/records", json=data)

    def update_domain_record(
        self,
        domain_id: str,
        record_id: str,
        target: str,
        name: str = None,
        type: str = None,
        port: int = None,
        priority: int = None,
        protocol: str = None,
        service: str = None,
        tag: str = None,
        ttl_sec: int = None,
        weight: int = None,
    ) -> tuple:
        data = {"target": target}
        if name:
            data["name"] = name
        if type:
            data["type"] = type
        if port:
            data["port"] = port
        if priority:
            data["priority"] = priority
        if protocol:
            data["protocol"] = protocol
        if service:
            data["service"] = service
        if tag:
            data["tag"] = tag
        if ttl_sec:
            data["ttl_sec"] = ttl_sec
        if weight:
            data["weight"] = weight

        return self.request(
            "PUT", f"/domains/{domain_id}/records/{record_id}", json=data
        )
