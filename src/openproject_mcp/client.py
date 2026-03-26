from typing import Any

import httpx

from openproject_mcp.config import Settings


class OpenProjectError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"OpenProject API error {status_code}: {message}")


class OpenProjectClient:
    def __init__(self, settings: Settings):
        base_url = str(settings.url).rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=base_url,
            auth=("apikey", settings.api_token.get_secret_value()),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=settings.timeout,
            verify=settings.verify_ssl,
        )

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.is_success:
            return
        try:
            body = response.json()
            message = body.get("message") or body.get("errorMessages") or response.text
        except Exception:
            message = response.text
        raise OpenProjectError(response.status_code, str(message))

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        response = await self._client.get(path, params=params)
        self._raise_for_status(response)
        return response.json()

    async def post(self, path: str, json: dict[str, Any]) -> dict:
        response = await self._client.post(path, json=json)
        self._raise_for_status(response)
        return response.json()

    async def patch(self, path: str, json: dict[str, Any]) -> dict:
        response = await self._client.patch(path, json=json)
        self._raise_for_status(response)
        return response.json()

    async def delete(self, path: str) -> None:
        response = await self._client.delete(path)
        self._raise_for_status(response)

    async def aclose(self) -> None:
        await self._client.aclose()
