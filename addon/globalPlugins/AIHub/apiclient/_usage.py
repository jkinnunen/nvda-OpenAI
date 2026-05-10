"""Provider-agnostic normalization of usage/billing payloads.

Each provider exposes token counts under different keys. We normalize them
to a single shape so the rest of the addon (history/cost display) does not
have to know which provider produced the data.
"""
from __future__ import annotations

from typing import Any


def _to_int(value: Any) -> int:
	try:
		return int(value or 0)
	except (TypeError, ValueError):
		return 0


def _normalize_usage(usage: Any) -> dict:
	"""Normalize a single ``usage`` dict (OpenAI, Anthropic, etc.) into the addon's shape."""
	if not isinstance(usage, dict):
		return {}

	prompt_tokens_details = usage.get("prompt_tokens_details") if isinstance(usage.get("prompt_tokens_details"), dict) else {}
	completion_tokens_details = usage.get("completion_tokens_details") if isinstance(usage.get("completion_tokens_details"), dict) else {}
	output_tokens_details = usage.get("output_tokens_details") if isinstance(usage.get("output_tokens_details"), dict) else {}
	input_tokens_details = usage.get("input_tokens_details") if isinstance(usage.get("input_tokens_details"), dict) else {}

	prompt_tokens = _to_int(usage.get("prompt_tokens"))
	completion_tokens = _to_int(usage.get("completion_tokens"))
	input_tokens = _to_int(usage.get("input_tokens")) or prompt_tokens
	output_tokens = _to_int(usage.get("output_tokens")) or completion_tokens
	total_tokens = _to_int(usage.get("total_tokens"))
	if total_tokens == 0 and (input_tokens or output_tokens):
		total_tokens = input_tokens + output_tokens

	reasoning_tokens = (
		_to_int(usage.get("reasoning_tokens"))
		or _to_int(completion_tokens_details.get("reasoning_tokens"))
		or _to_int(output_tokens_details.get("reasoning_tokens"))
	)

	cached_input_tokens = (
		_to_int(prompt_tokens_details.get("cached_tokens"))
		or _to_int(input_tokens_details.get("cached_tokens"))
		or _to_int(usage.get("cached_input_tokens"))
		or _to_int(usage.get("cache_read_input_tokens"))
		or _to_int(usage.get("prompt_cache_hit_tokens"))  # DeepSeek
	)
	cache_creation_input_tokens = _to_int(usage.get("cache_creation_input_tokens"))

	input_audio_tokens = (
		_to_int(prompt_tokens_details.get("audio_tokens"))
		or _to_int(input_tokens_details.get("audio_tokens"))
		or _to_int(usage.get("prompt_audio_tokens"))
	)
	output_audio_tokens = (
		_to_int(completion_tokens_details.get("audio_tokens"))
		or _to_int(output_tokens_details.get("audio_tokens"))
		or _to_int(usage.get("completion_audio_tokens"))
	)

	normalized = {
		"input_tokens": input_tokens,
		"output_tokens": output_tokens,
		"total_tokens": total_tokens,
		"prompt_tokens": prompt_tokens,
		"completion_tokens": completion_tokens,
		"reasoning_tokens": reasoning_tokens,
		"cached_input_tokens": cached_input_tokens,
		"cache_creation_input_tokens": cache_creation_input_tokens,
		"input_audio_tokens": input_audio_tokens,
		"output_audio_tokens": output_audio_tokens,
	}
	cost = usage.get("cost")
	if isinstance(cost, (int, float)):
		normalized["cost"] = float(cost)
	return normalized


def _normalize_usage_from_payload(payload: Any) -> dict:
	"""Try the standard ``usage`` field first, then fall back to provider-specific shapes."""
	if not isinstance(payload, dict):
		return {}
	usage = _normalize_usage(payload.get("usage"))
	if usage:
		return usage

	# Ollama native counters (also seen in some compatibility payloads).
	prompt_tokens = _to_int(payload.get("prompt_eval_count")) or _to_int(payload.get("prompt_tokens"))
	completion_tokens = _to_int(payload.get("eval_count")) or _to_int(payload.get("completion_tokens"))
	if prompt_tokens == 0 and completion_tokens == 0:
		return {}
	return {
		"input_tokens": prompt_tokens,
		"output_tokens": completion_tokens,
		"total_tokens": prompt_tokens + completion_tokens,
		"prompt_tokens": prompt_tokens,
		"completion_tokens": completion_tokens,
		"reasoning_tokens": 0,
		"cached_input_tokens": 0,
		"cache_creation_input_tokens": 0,
		"input_audio_tokens": 0,
		"output_audio_tokens": 0,
	}


def _merge_usage(base: dict, update: dict) -> dict:
	"""Merge two normalized usage dicts, preferring non-zero values from ``update``.

	Used by Anthropic streaming where ``message_start.usage`` provides input_tokens
	and ``message_delta.usage`` provides cumulative output_tokens — neither chunk
	alone has the full picture.
	"""
	if not base:
		return dict(update or {})
	if not update:
		return dict(base)
	merged = dict(base)
	for key, value in update.items():
		if key == "cost":
			if isinstance(value, (int, float)):
				merged["cost"] = float(value)
			continue
		try:
			ivalue = int(value or 0)
		except (TypeError, ValueError):
			continue
		if ivalue:
			merged[key] = ivalue
	# Recompute total_tokens if components changed but the field is missing/stale.
	in_tok = _to_int(merged.get("input_tokens")) or _to_int(merged.get("prompt_tokens"))
	out_tok = _to_int(merged.get("output_tokens")) or _to_int(merged.get("completion_tokens"))
	if in_tok or out_tok:
		merged["total_tokens"] = max(_to_int(merged.get("total_tokens")), in_tok + out_tok)
	return merged
