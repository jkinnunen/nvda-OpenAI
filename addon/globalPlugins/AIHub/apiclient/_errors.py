"""Exception hierarchy and helpers for parsing/formatting API error payloads."""
from __future__ import annotations

import json


class APIError(Exception):
	"""Base exception for API errors."""

	message: str = ""

	def __init__(self, message: str, *args, **kwargs):
		self.message = message
		super().__init__(message, *args, **kwargs)


class APIConnectionError(APIError):
	"""Raised when the connection to the API fails (DNS, TLS, socket, OS errors)."""

	pass


class APIStatusError(APIError):
	"""Raised when the API returns a non-2xx HTTP status."""

	def __init__(self, message: str, status_code: int = 0, response_body: str = ""):
		self.status_code = status_code
		self.response_body = response_body
		super().__init__(message)


def _resolve_error_message(body: str, status: int) -> str:
	"""Extract a human-readable error message from an API response body."""
	if not body:
		return f"HTTP {status}"
	try:
		data = json.loads(body)
	except json.JSONDecodeError:
		return body or f"HTTP {status}"
	if not isinstance(data, dict):
		return str(data) if data else (body or f"HTTP {status}")
	err = data.get("error", {})
	if isinstance(err, dict):
		return err.get("message", err.get("code", body)) or body
	return str(err)


def truncate_error_for_user(err, max_len: int = 300) -> str:
	"""Return a user-facing error string, truncated if needed."""
	msg = str(err) if err else ""
	if len(msg) < max_len:
		return msg
	return msg[:max_len] + "..."
