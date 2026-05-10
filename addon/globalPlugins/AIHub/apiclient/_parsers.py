"""Non-streaming response parsers (Chat Completions, Responses, Anthropic).

Each parser turns the provider's JSON response shape into a uniform
``ChatCompletion`` containing a single ``Choice`` (we never request ``n>1``).
"""
from __future__ import annotations

from typing import Any

from ..consts import Provider
from ._think_tags import (
	_extract_reasoning_text,
	_split_ollama_think_inline,
	_split_text_and_reasoning_from_parts,
)
from ._types import ChatCompletion, Choice, ChoiceMessage
from ._usage import _normalize_usage, _normalize_usage_from_payload


_REASONING_KEYS = (
	"reasoning",
	"reasoning_content",
	"thinking",
	"thinking_content",
	"reasoning_details",
	"thought",
)


def parse_chat_completion(data: dict, provider: str = "") -> ChatCompletion:
	"""Parse an OpenAI Chat Completions / OpenAI-compatible JSON response."""
	choices = []
	for i, choice in enumerate(data.get("choices", []) if isinstance(data, dict) else []):
		choices.append(_parse_chat_choice(choice, i, provider))
	return ChatCompletion(choices, usage=_normalize_usage_from_payload(data))


def _parse_chat_choice(choice: Any, index: int, provider: str) -> Choice:
	if not isinstance(choice, dict):
		choice = {}
	msg = choice.get("message") if isinstance(choice.get("message"), dict) else choice
	if not isinstance(msg, dict):
		msg = {}

	content_val = msg.get("content")
	if isinstance(content_val, list):
		content, reasoning = _split_text_and_reasoning_from_parts(content_val)
	else:
		content = content_val or choice.get("text") or ""
		reasoning = ""

	if not reasoning:
		reasoning = _first_reasoning(msg) or _first_reasoning(choice)

	if content is not None and not isinstance(content, str):
		content = str(content)
	content = content or ""

	# Always strip inline ``<think>`` / ``<thought>`` tags (except for Anthropic,
	# which uses structured content blocks and never embeds these wrappers in
	# text). Skipping the strip when structured reasoning is also present would
	# let Gemini/Gemma's inline wrapper leak into the visible answer.
	if content and provider != Provider.Anthropic:
		visible, think_inline, _ = _split_ollama_think_inline(content, in_think=False)
		content = visible
		if think_inline:
			reasoning = _merge_reasoning(reasoning, think_inline)

	audio = msg.get("audio") if isinstance(msg.get("audio"), dict) else None
	if audio and audio.get("data"):
		message = ChoiceMessage(content, audio=audio, reasoning=reasoning)
	else:
		message = ChoiceMessage(content, reasoning=reasoning)
	return Choice(message, index=index)


def _first_reasoning(container: Any) -> str:
	if not isinstance(container, dict):
		return ""
	for key in _REASONING_KEYS:
		text = _extract_reasoning_text(container.get(key))
		if text:
			return text
	return ""


def parse_responses(data: dict, provider: str = "") -> ChatCompletion:
	"""Parse an OpenAI Responses API non-streaming JSON response."""
	if not isinstance(data, dict):
		data = {}
	text_parts: list[str] = []
	reasoning_parts: list[str] = []

	output_text = data.get("output_text")
	if isinstance(output_text, str) and output_text:
		text_parts.append(output_text)

	for item in data.get("output", []) or []:
		if not isinstance(item, dict):
			continue
		item_type = str(item.get("type", "")).lower()
		content = item.get("content")
		if isinstance(content, list):
			for part in content:
				if not isinstance(part, dict):
					continue
				part_type = str(part.get("type", "")).lower()
				if part_type in ("output_text", "text", "message_output_text"):
					value = part.get("text") or part.get("output_text") or ""
					if isinstance(value, str) and value:
						text_parts.append(value)
				elif "reasoning" in part_type or "thinking" in part_type:
					r = _extract_reasoning_text(part)
					if r:
						reasoning_parts.append(r)
		elif "reasoning" in item_type or "thinking" in item_type:
			r = _extract_reasoning_text(item)
			if r:
				reasoning_parts.append(r)

	text = "".join(text_parts).strip()
	reasoning = "\n".join(reasoning_parts).strip()
	if text and provider != Provider.Anthropic:
		visible, think_inline, _ = _split_ollama_think_inline(text, in_think=False)
		text = visible.strip()
		if think_inline:
			reasoning = _merge_reasoning(reasoning, think_inline, separator="\n").strip()

	return ChatCompletion(
		[Choice(ChoiceMessage(content=text, reasoning=reasoning))],
		usage=_normalize_usage_from_payload(data),
	)


def _merge_reasoning(base: str, addition: str, separator: str = "") -> str:
	"""Append ``addition`` to ``base`` while avoiding obvious duplication.

	The structured reasoning channel and the inline-tag stripper can both
	contribute reasoning text. Empty fragments are skipped, and an addition
	already present verbatim in ``base`` is dropped so the user does not see
	the same paragraph twice.
	"""
	if not addition:
		return base or ""
	if not base:
		return addition
	if addition in base:
		return base
	return f"{base}{separator}{addition}"


def parse_anthropic(data: dict) -> ChatCompletion:
	"""Parse an Anthropic Messages API non-streaming JSON response."""
	if not isinstance(data, dict):
		data = {}
	text = ""
	reasoning = ""
	for blk in data.get("content", []) or []:
		if not isinstance(blk, dict):
			continue
		blk_type = str(blk.get("type", "")).lower()
		if blk_type == "text":
			text += blk.get("text", "") or ""
		elif "thinking" in blk_type or "reasoning" in blk_type:
			part = _extract_reasoning_text(blk)
			if part:
				reasoning = f"{reasoning}\n{part}".strip() if reasoning else part
	return ChatCompletion(
		[Choice(ChoiceMessage(text, reasoning=reasoning))],
		usage=_normalize_usage(data.get("usage")),
	)
