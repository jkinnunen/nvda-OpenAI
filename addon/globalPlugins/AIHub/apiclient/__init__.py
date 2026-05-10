"""HTTP client for OpenAI-compatible endpoints (and Anthropic Messages).

This package replaces the openai-python SDK with a stdlib-only implementation
so the addon does not need to bundle external dependencies into NVDA.

Public API (used elsewhere in the addon):

* ``OpenAIClient`` — main client class.
* ``configure_client_for_provider`` — point a client at a given provider.
* ``ChatCompletion``, ``Choice``, ``ChoiceMessage``, ``ChoiceDelta``,
  ``StreamChoice`` — non-streaming and streaming response types.
* ``Transcription`` — return type of audio transcription/translation calls.
* ``APIError``, ``APIConnectionError``, ``APIStatusError`` — exception hierarchy.
* ``transcribe_audio_mistral`` — Mistral Voxtral transcription helper.
* ``truncate_error_for_user`` — convert an exception to a user-facing message.
* ``_resolve_error_message`` — extract the human-readable message from an API error body.
"""
from __future__ import annotations

from ._client import (
	OpenAIClient,
	configure_client_for_provider,
	transcribe_audio_mistral,
)
from ._errors import (
	APIConnectionError,
	APIError,
	APIStatusError,
	_resolve_error_message,
	truncate_error_for_user,
)
from ._types import (
	ChatCompletion,
	Choice,
	ChoiceDelta,
	ChoiceMessage,
	StreamChoice,
	StreamEvent,
	Transcription,
)

__all__ = [
	"APIConnectionError",
	"APIError",
	"APIStatusError",
	"ChatCompletion",
	"Choice",
	"ChoiceDelta",
	"ChoiceMessage",
	"OpenAIClient",
	"StreamChoice",
	"StreamEvent",
	"Transcription",
	"_resolve_error_message",
	"configure_client_for_provider",
	"transcribe_audio_mistral",
	"truncate_error_for_user",
]
