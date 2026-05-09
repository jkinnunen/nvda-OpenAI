"""
HTTP-based API client for OpenAI-compatible endpoints.
Replaces the openai Python package to avoid bundling dependencies in NVDA.
Uses only Python standard library (urllib, json).
"""
from __future__ import annotations

import json
import os
import uuid
import ssl
import base64
import mimetypes
import urllib.error
import urllib.parse
import urllib.request
from io import BytesIO
from typing import Any, BinaryIO, Generator, Optional

from . import apikeymanager
from .anthropicthinking import get_anthropic_thinking_profile, normalize_effort
from .consts import BASE_URLs


class APIError(Exception):
	"""Base exception for API errors."""
	message: str = ""

	def __init__(self, message: str, *args, **kwargs):
		self.message = message
		super().__init__(message, *args, **kwargs)


class APIConnectionError(APIError):
	"""Raised when the connection to the API fails."""
	pass


class APIStatusError(APIError):
	"""Raised when the API returns an error status code."""
	def __init__(self, message: str, status_code: int = 0, response_body: str = ""):
		self.status_code = status_code
		self.response_body = response_body
		super().__init__(message)


class ChoiceDelta:
	"""Mimics openai.types.chat.chat_completion.ChoiceDelta for streaming."""
	def __init__(self, content: Optional[str] = None, reasoning: Optional[str] = None):
		self.content = content or ""
		self.reasoning = reasoning or ""


class StreamChoice:
	"""Mimics stream response choice for compatibility."""
	def __init__(self, delta: ChoiceDelta, finish_reason: Optional[str] = None):
		self.delta = delta
		self.finish_reason = finish_reason


class ChoiceMessage:
	"""Mimics openai.types.chat.chat_completion.Choice.Message."""
	def __init__(self, content: str = "", audio: Optional[dict] = None, reasoning: str = ""):
		self.content = content or ""
		self.audio = audio  # {"data": base64_str, "format": "wav"} when model returns audio
		self.reasoning = reasoning or ""


class Choice:
	"""Mimics openai.types.chat.chat_completion.Choice for non-streaming."""
	def __init__(self, message: ChoiceMessage, index: int = 0):
		self.message = message
		self.index = index


class ChatCompletion:
	"""Mimics openai.types.chat.chat_completion.ChatCompletion."""
	def __init__(self, choices: list, usage: Optional[dict] = None):
		self.choices = choices
		self.usage = usage or {}


def _normalize_usage(usage: Any) -> dict:
	"""Normalize provider usage payloads into a common dict."""
	if not isinstance(usage, dict):
		return {}

	def _to_int(value: Any) -> int:
		try:
			return int(value or 0)
		except (TypeError, ValueError):
			return 0

	prompt_tokens_details = usage.get("prompt_tokens_details")
	if not isinstance(prompt_tokens_details, dict):
		prompt_tokens_details = {}
	completion_tokens_details = usage.get("completion_tokens_details")
	if not isinstance(completion_tokens_details, dict):
		completion_tokens_details = {}
	output_tokens_details = usage.get("output_tokens_details")
	if not isinstance(output_tokens_details, dict):
		output_tokens_details = {}

	prompt_tokens = _to_int(usage.get("prompt_tokens"))
	completion_tokens = _to_int(usage.get("completion_tokens"))
	input_tokens = _to_int(usage.get("input_tokens"))
	output_tokens = _to_int(usage.get("output_tokens"))
	if input_tokens == 0:
		input_tokens = prompt_tokens
	if output_tokens == 0:
		output_tokens = completion_tokens
	total_tokens = _to_int(usage.get("total_tokens"))
	if total_tokens == 0 and (input_tokens or output_tokens):
		total_tokens = input_tokens + output_tokens

	reasoning_tokens = _to_int(usage.get("reasoning_tokens"))
	if reasoning_tokens == 0:
		reasoning_tokens = _to_int(completion_tokens_details.get("reasoning_tokens"))
	if reasoning_tokens == 0:
		reasoning_tokens = _to_int(output_tokens_details.get("reasoning_tokens"))

	cached_input_tokens = _to_int(prompt_tokens_details.get("cached_tokens"))
	if cached_input_tokens == 0:
		cached_input_tokens = _to_int(usage.get("cached_input_tokens"))
	if cached_input_tokens == 0:
		cached_input_tokens = _to_int(usage.get("cache_read_input_tokens"))
	cache_creation_input_tokens = _to_int(usage.get("cache_creation_input_tokens"))

	input_audio_tokens = _to_int(prompt_tokens_details.get("audio_tokens"))
	if input_audio_tokens == 0:
		input_audio_tokens = _to_int(usage.get("prompt_audio_tokens"))
	output_audio_tokens = _to_int(completion_tokens_details.get("audio_tokens"))
	if output_audio_tokens == 0:
		output_audio_tokens = _to_int(usage.get("completion_audio_tokens"))

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
	"""Normalize usage from OpenAI-style usage or provider top-level counters."""
	if not isinstance(payload, dict):
		return {}
	usage = _normalize_usage(payload.get("usage"))
	if usage:
		return usage

	def _to_int(value: Any) -> int:
		try:
			return int(value or 0)
		except (TypeError, ValueError):
			return 0

	# Ollama native counters (also seen in some compatibility payloads).
	prompt_tokens = _to_int(payload.get("prompt_eval_count"))
	completion_tokens = _to_int(payload.get("eval_count"))
	if prompt_tokens == 0:
		prompt_tokens = _to_int(payload.get("prompt_tokens"))
	if completion_tokens == 0:
		completion_tokens = _to_int(payload.get("completion_tokens"))
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


def _create_opener():
	"""Create URL opener with timeout and SSL context."""
	ctx = ssl.create_default_context()
	return urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))


# User-Agent to avoid Cloudflare 1010 (browser signature) blocks on api.x.ai etc.
_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def _build_headers(api_key: str, organization: Optional[str] = None) -> dict:
	"""Build request headers for API calls."""
	headers = {
		"Content-Type": "application/json",
		"User-Agent": _USER_AGENT,
	}
	if api_key and str(api_key).strip():
		headers["Authorization"] = f"Bearer {api_key}"
	if organization and organization.strip():
		org_val = organization.strip()
		if ":= " in org_val:
			org_val = org_val.split(":= ", 1)[-1]
		if org_val and org_val != ":=":
			headers["OpenAI-Organization"] = org_val
	return headers


def _decode_audio_base64(value: Any) -> Optional[bytes]:
	"""Decode base64 audio payloads, including optional data URL prefix."""
	if not isinstance(value, str):
		return None
	data = value.strip()
	if not data:
		return None
	if data.startswith("data:") and "," in data:
		data = data.split(",", 1)[1].strip()
	try:
		return base64.b64decode(data, validate=False)
	except Exception:
		return None


def _extract_audio_bytes_from_json_payload(payload: Any) -> Optional[bytes]:
	"""Extract binary audio bytes from known JSON response shapes."""
	if not isinstance(payload, dict):
		return None
	for key in ("audio_data", "data"):
		audio = _decode_audio_base64(payload.get(key))
		if audio:
			return audio
	for container_key in ("audio", "output_audio"):
		container = payload.get(container_key)
		if not isinstance(container, dict):
			continue
		for key in ("audio_data", "data"):
			audio = _decode_audio_base64(container.get(key))
			if audio:
				return audio
	return None


def _build_anthropic_headers(api_key: str) -> dict:
	"""Build request headers for Anthropic API."""
	return {
		"x-api-key": api_key,
		"anthropic-version": "2023-06-01",
		"Content-Type": "application/json",
		"User-Agent": _USER_AGENT,
	}


def _convert_content_to_anthropic(content) -> str | list:
	"""Convert OpenAI-format content to Anthropic format."""
	def _is_text_media_type(media_type: str) -> bool:
		mt = (media_type or "").lower().strip()
		if not mt:
			return False
		if mt.startswith("text/"):
			return True
		return mt in {
			"application/json",
			"application/xml",
			"application/javascript",
			"application/x-javascript",
			"application/sql",
		}

	def _decode_text_payload(data: str, media_type: str) -> str:
		if not isinstance(data, str) or not data.strip():
			return ""
		raw_data = data.strip()
		mt = media_type
		if raw_data.startswith("data:") and "," in raw_data:
			header, b64_data = raw_data.split(",", 1)
			raw_data = b64_data
			if ";" in header:
				mt = header[5:].split(";")[0].strip() or media_type
		if not _is_text_media_type(mt):
			return ""
		try:
			decoded = base64.b64decode(raw_data, validate=False)
			return decoded.decode("utf-8", errors="replace")
		except Exception:
			return ""

	if isinstance(content, str):
		return content
	if not isinstance(content, list):
		return str(content) if content else ""
	blocks = []
	for part in content:
		if not isinstance(part, dict):
			continue
		typ = part.get("type", "")
		if typ == "text":
			text = part.get("text", "")
			if text:
				blocks.append({"type": "text", "text": text})
		elif typ == "image_url":
			img = part.get("image_url") or {}
			url = img.get("url", "")
			if url.startswith("data:"):
				# data:image/png;base64,XXXXX
				try:
					header, data = url.split(",", 1)
					mt = "image/png"
					if "image/" in header:
						mt = header.split("image/")[-1].split(";")[0].strip()
						mt = f"image/{mt}" if not mt.startswith("image/") else mt
					blocks.append({
						"type": "image",
						"source": {"type": "base64", "media_type": mt, "data": data}
					})
				except (ValueError, IndexError):
					pass
		elif typ == "input_file":
			source = None
			filename = part.get("filename", "")
			file_id = part.get("file_id")
			file_url = part.get("file_url")
			file_path = part.get("file_path")
			file_data = part.get("file_data")
			extracted_text = ""
			if isinstance(file_id, str) and file_id.strip():
				source = {"type": "file", "file_id": file_id.strip()}
			elif isinstance(file_url, str) and file_url.strip():
				source = {"type": "url", "url": file_url.strip()}
			elif isinstance(file_data, str) and file_data.strip():
				data = file_data.strip()
				media_type = "application/pdf"
				if data.startswith("data:") and "," in data:
					header, b64_data = data.split(",", 1)
					if ";" in header:
						media_type = header[5:].split(";")[0].strip() or media_type
					data = b64_data
				if _is_text_media_type(media_type):
					extracted_text = _decode_text_payload(data, media_type)
				else:
					source = {"type": "base64", "media_type": media_type, "data": data}
			elif isinstance(file_path, str) and os.path.exists(file_path):
				try:
					with open(file_path, "rb") as f:
						raw = f.read()
					media_type = mimetypes.guess_type(file_path)[0] or "application/pdf"
					if _is_text_media_type(media_type):
						extracted_text = raw.decode("utf-8", errors="replace")
					else:
						source = {
							"type": "base64",
							"media_type": media_type,
							"data": base64.b64encode(raw).decode("utf-8"),
						}
					if not filename:
						filename = os.path.basename(file_path)
				except OSError:
					source = None
			if extracted_text:
				title = filename or "Attached document"
				blocks.append({"type": "text", "text": f"[{title}]\n{extracted_text}"})
				continue
			if source:
				doc_block = {"type": "document", "source": source}
				if filename:
					doc_block["title"] = filename
				blocks.append(doc_block)
	return blocks if blocks else ""


def _has_input_file_parts(messages: Any) -> bool:
	"""Return True when at least one message contains input_file content."""
	if not isinstance(messages, list):
		return False
	for msg in messages:
		if not isinstance(msg, dict):
			continue
		content = msg.get("content")
		if not isinstance(content, list):
			continue
		for part in content:
			if isinstance(part, dict) and part.get("type") == "input_file":
				return True
	return False


def _file_path_to_data_url(path: str) -> Optional[str]:
	"""Read local file and return RFC2397 data URL."""
	if not isinstance(path, str) or not path or not os.path.exists(path):
		return None
	try:
		with open(path, "rb") as f:
			raw = f.read()
	except OSError:
		return None
	mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
	b64 = base64.b64encode(raw).decode("utf-8")
	return f"data:{mime};base64,{b64}"


def _inline_input_file_paths(messages: list) -> list:
	"""Convert input_file.file_path into input_file.file_data data URLs."""
	if not isinstance(messages, list):
		return messages
	converted = []
	for msg in messages:
		if not isinstance(msg, dict):
			converted.append(msg)
			continue
		content = msg.get("content")
		if not isinstance(content, list):
			converted.append(msg)
			continue
		new_parts = []
		for part in content:
			if not isinstance(part, dict) or part.get("type") != "input_file":
				new_parts.append(part)
				continue
			new_part = dict(part)
			file_path = new_part.get("file_path")
			if isinstance(file_path, str) and file_path:
				data_url = _file_path_to_data_url(file_path)
				if data_url:
					new_part["file_data"] = data_url
					new_part.pop("file_path", None)
					if not new_part.get("filename"):
						new_part["filename"] = os.path.basename(file_path)
			new_parts.append(new_part)
		new_msg = dict(msg)
		new_msg["content"] = new_parts
		converted.append(new_msg)
	return converted


def _extract_reasoning_text(value: Any) -> str:
	"""Best-effort extractor for reasoning/thinking payloads."""
	if isinstance(value, str):
		return value
	if isinstance(value, list):
		parts = []
		for item in value:
			txt = _extract_reasoning_text(item)
			if txt:
				parts.append(txt)
		return "\n".join(parts).strip()
	if isinstance(value, dict):
		for key in ("text", "content", "reasoning", "thinking", "thought", "summary"):
			txt = _extract_reasoning_text(value.get(key))
			if txt:
				return txt
	return ""


def _split_text_and_reasoning_from_parts(parts: Any) -> tuple[str, str]:
	"""Split mixed content parts into (text, reasoning) strings."""
	text_chunks = []
	reasoning_chunks = []
	if not isinstance(parts, list):
		return "", ""
	for part in parts:
		if not isinstance(part, dict):
			continue
		part_type = str(part.get("type", "")).lower()
		part_text = _extract_reasoning_text(part)
		if not part_text:
			continue
		if (
			"reasoning" in part_type
			or "thinking" in part_type
			or part_type in ("thought", "thought_summary")
		):
			reasoning_chunks.append(part_text)
		else:
			text_chunks.append(part_text)
	return "\n".join(text_chunks).strip(), "\n".join(reasoning_chunks).strip()


# Inline thinking blocks emitted by some reasoning models (OpenRouter, Ollama, DeepSeek R1, etc.).
# Order: strip redacted_thinking-style wrappers first, then plain think tags (some distillations / R1-style).
_THINK_TAG_PAIRS = (
	("<think>", "</think>"),
	("", ""),
)

# Worst-case suffix kept between SSE chunks so a tag is never split across chunk boundaries incorrectly.
_THINK_STREAM_CARRY_KEEP = max((max(len(o), len(c)) for o, c in _THINK_TAG_PAIRS), default=1) - 1
if _THINK_STREAM_CARRY_KEEP < 1:
	_THINK_STREAM_CARRY_KEEP = 1


def _split_think_pair_inline(text: str, in_think: bool, open_tag: str, close_tag: str) -> tuple[str, str, bool]:
	"""Split one tag pair from content (case-insensitive tag names)."""
	if not text:
		return "", "", in_think
	resp_parts = []
	reasoning_parts = []
	lower = text.lower()
	ot_l = open_tag.lower()
	ct_l = close_tag.lower()
	i = 0
	while i < len(text):
		if in_think:
			j = lower.find(ct_l, i)
			if j < 0:
				reasoning_parts.append(text[i:])
				i = len(text)
				break
			reasoning_parts.append(text[i:j])
			i = j + len(close_tag)
			in_think = False
		else:
			j = lower.find(ot_l, i)
			if j < 0:
				resp_parts.append(text[i:])
				i = len(text)
				break
			resp_parts.append(text[i:j])
			i = j + len(open_tag)
			in_think = True
	return "".join(resp_parts), "".join(reasoning_parts), in_think


def _split_ollama_think_inline(text: str, in_think: bool = False) -> tuple[str, str, bool]:
	"""Split all known inline thinking tag pairs from assistant content (non-streaming)."""
	visible = text or ""
	reasoning_all = []
	final_in_think = in_think
	for open_tag, close_tag in _THINK_TAG_PAIRS:
		visible, chunk, final_in_think = _split_think_pair_inline(visible, False, open_tag, close_tag)
		if chunk:
			reasoning_all.append(chunk)
	return visible, "".join(reasoning_all), final_in_think


def _should_apply_inline_think_strip(provider: str, has_separate_reasoning: bool) -> bool:
	"""Parse think-tags from assistant text only when the API did not return structured reasoning."""
	if provider == "Anthropic":
		return False
	return not has_separate_reasoning


def _split_think_pair_stream(text: str, state: dict, open_tag: str, close_tag: str) -> tuple[str, str]:
	"""Incremental parser for one tag pair across chunked SSE text."""
	if not isinstance(state, dict):
		state = {}
	carry = state.get("carry", "") or ""
	in_think = bool(state.get("in_think", False))
	buf = carry + (text or "")
	if not buf:
		return "", ""
	keep = _THINK_STREAM_CARRY_KEEP
	if len(buf) <= keep:
		state["carry"] = buf
		state["in_think"] = in_think
		return "", ""
	process = buf[:-keep]
	state["carry"] = buf[-keep:]
	resp, reasoning, in_think = _split_think_pair_inline(process, in_think=in_think, open_tag=open_tag, close_tag=close_tag)
	state["in_think"] = in_think
	return resp, reasoning


def _flush_think_pair_stream(state: dict, open_tag: str, close_tag: str) -> tuple[str, str]:
	"""Flush carry for one tag pair at end of stream."""
	if not isinstance(state, dict):
		return "", ""
	carry = state.get("carry", "") or ""
	in_think = bool(state.get("in_think", False))
	state["carry"] = ""
	resp, reasoning, in_think = _split_think_pair_inline(carry, in_think=in_think, open_tag=open_tag, close_tag=close_tag)
	state["in_think"] = in_think
	return resp, reasoning


def _flush_think_chain(states: list) -> tuple[str, str]:
	"""Flush all tag-pair stream parsers in order (see _apply_think_chain_to_chunk)."""
	if not states:
		return "", ""
	reasoning_parts = []
	visible_acc = ""
	for idx, (open_tag, close_tag) in enumerate(_THINK_TAG_PAIRS):
		if idx >= len(states):
			break
		s = states[idx]
		buf = (s.get("carry") or "") + visible_acc
		s["carry"] = ""
		v, r, in_t = _split_think_pair_inline(buf, s.get("in_think", False), open_tag, close_tag)
		s["in_think"] = in_t
		visible_acc = v
		if r:
			reasoning_parts.append(r)
	return visible_acc, "".join(reasoning_parts)


def _apply_think_chain_to_chunk(content: str, states: list) -> tuple[str, str]:
	"""Run streamed content through each tag pair parser in sequence."""
	if not content or not states:
		return content or "", ""
	out = content
	reasoning_frags = []
	for idx, (open_tag, close_tag) in enumerate(_THINK_TAG_PAIRS):
		if idx >= len(states):
			break
		out, frag = _split_think_pair_stream(out, states[idx], open_tag, close_tag)
		if frag:
			reasoning_frags.append(frag)
	return out, "".join(reasoning_frags)


def _convert_messages_to_anthropic(messages: list) -> tuple[str | None, list]:
	"""Convert OpenAI messages to Anthropic format. Returns (system, messages)."""
	system = None
	anthropic_msgs = []
	for m in messages:
		if not isinstance(m, dict):
			continue
		role = (m.get("role") or "").lower()
		content = m.get("content", "")
		if role == "system":
			if isinstance(content, str):
				system = content
			elif isinstance(content, list):
				text_parts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
				system = "\n".join(text_parts) if text_parts else None
			else:
				system = str(content) if content else None
			continue
		if role not in ("user", "assistant"):
			continue
		conv = _convert_content_to_anthropic(content)
		if conv or (isinstance(conv, str) and conv):
			anthropic_msgs.append({"role": role, "content": conv})
	return (system, anthropic_msgs)


class OpenAIClient:
	"""
	HTTP-based client for OpenAI-compatible APIs.
	Replaces openai.OpenAI without external dependencies.
	"""

	def __init__(
		self,
		api_key: str,
		base_url: str = "https://api.openai.com/v1",
		organization: Optional[str] = None,
	):
		self.api_key = api_key
		self.base_url = base_url.rstrip("/")
		self.organization = organization
		self.provider = "OpenAI"
		self._opener = _create_opener()
		self.chat = _ChatCompletions(self)
		self.audio = _Audio(self)

	def clone(self) -> "OpenAIClient":
		"""Return a detached client copy for thread-safe per-request mutations."""
		other = OpenAIClient(
			api_key=self.api_key,
			base_url=self.base_url,
			organization=self.organization,
		)
		other.provider = getattr(self, "provider", "OpenAI")
		other.account_id = getattr(self, "account_id", None)
		return other

	def _request(
		self,
		method: str,
		path: str,
		body: Optional[dict] = None,
		headers: Optional[dict] = None,
	) -> urllib.request.Request:
		"""Build request with auth."""
		url = f"{self.base_url}{path}"
		req_headers = _build_headers(self.api_key, self.organization)
		if headers:
			req_headers.update(headers)
		data = json.dumps(body).encode("utf-8") if body else None
		return urllib.request.Request(url, data=data, headers=req_headers, method=method)

	def chat_completions_create(
		self,
		*,
		model: str,
		messages: list,
		stream: bool = False,
		**kwargs,
	) -> ChatCompletion | Generator:
		"""Create chat completion. Returns ChatCompletion or generator for streaming."""
		provider = getattr(self, "provider", "OpenAI")
		has_input_files = _has_input_file_parts(messages)
		if provider == "Anthropic":
			return self._anthropic_chat_completions_create(
				model=model, messages=messages, stream=stream, **kwargs
			)
		if provider == "OpenAI" and has_input_files:
			return self._openai_responses_create(
				model=model, messages=messages, stream=stream, **kwargs
			)
		if has_input_files:
			# Best-effort for non-OpenAI providers: inline local files as data URLs.
			messages = _inline_input_file_paths(messages)
		body = {"model": model, "messages": messages, "stream": stream}
		# Build body with provider-appropriate params
		excluded = {"reasoning_enabled", "adaptive_thinking", "reasoning_effort"}
		for k, v in kwargs.items():
			if k in excluded or v is None:
				continue
			body[k] = v
		# Reasoning: provider-specific param shape (avoids thinking.adaptive.effort errors)
		reasoning_effort = kwargs.get("reasoning_effort")
		if reasoning_effort is not None:
			if provider == "OpenRouter":
				body["reasoning"] = {"effort": reasoning_effort}
			else:
				body["reasoning_effort"] = reasoning_effort

		req = self._request("POST", "/chat/completions", body=body)
		try:
			if stream:
				resp = self._opener.open(req, timeout=120)
				if resp.status != 200:
					text = resp.read().decode("utf-8", errors="replace")
					resp.close()
					raise APIStatusError(
						_resolve_error_message(text, resp.status),
						status_code=resp.status,
						response_body=text,
					)
				return self._stream_chat(resp)
			with self._opener.open(req, timeout=120) as resp:
				if resp.status != 200:
					text = resp.read().decode("utf-8", errors="replace")
					raise APIStatusError(
						_resolve_error_message(text, resp.status),
						status_code=resp.status,
						response_body=text,
					)
				data = json.loads(resp.read().decode("utf-8"))
				return self._parse_chat_completion(data)
		except urllib.error.HTTPError as e:
			text = e.read().decode("utf-8", errors="replace") if e.fp else ""
			raise APIStatusError(
				_resolve_error_message(text, e.code),
				status_code=e.code,
				response_body=text,
			)
		except (urllib.error.URLError, OSError, ConnectionError) as e:
			raise APIConnectionError(str(e)) from e

	def _stream_chat(self, resp) -> Generator:
		"""Parse SSE stream and yield stream events."""
		try:
			provider = getattr(self, "provider", "")
			# Once any chunk carries structured reasoning, stop stripping inline think-tags from content (avoids mangling DeepSeek/OpenAI deltas).
			structured_reasoning_seen = False
			# OpenAI-compatible SSE: merge gateway reasoning_* delta keys, strip embedded think tags from content when needed.
			think_chain_states = [{"carry": "", "in_think": False} for _ in _THINK_TAG_PAIRS]
			buf = b""
			for chunk in resp:
				buf += chunk
				while b"\n" in buf or b"\r\n" in buf:
					line, buf = buf.split(b"\n", 1) if b"\n" in buf else (buf, b"")
					line = line.strip()
					if not line or not line.startswith(b"data: "):
						continue
					payload = line[6:].strip()
					if payload == b"[DONE]":
						if think_chain_states:
							content, reasoning = _flush_think_chain(think_chain_states)
							if content or reasoning:
								yield type("StreamEvent", (), {
									"choices": [StreamChoice(ChoiceDelta(content, reasoning=reasoning), None)],
									"usage": {},
								})()
						return
					try:
						data = json.loads(payload.decode("utf-8"))
						if not isinstance(data, dict):
							continue
						usage = _normalize_usage_from_payload(data)
						if not usage and isinstance(data.get("response"), dict):
							usage = _normalize_usage_from_payload(data.get("response"))
						choices = data.get("choices", [])
						content = ""
						finish = None
						reasoning = ""
						if choices:
							c = choices[0]
							if isinstance(c, dict):
								delta = c.get("delta") or {}
								if isinstance(delta, str):
									content = delta
								elif isinstance(delta, dict):
									content_val = delta.get("content")
									if isinstance(content_val, list):
										content, reasoning = _split_text_and_reasoning_from_parts(content_val)
									else:
										content = content_val
									for key in (
										"reasoning",
										"reasoning_content",
										"thinking",
										"thinking_content",
										"thought",
									):
										text = _extract_reasoning_text(delta.get(key))
										if text:
											reasoning = text
											break
									if not reasoning and isinstance(delta.get("reasoning_details"), list):
										reasoning = _extract_reasoning_text(delta.get("reasoning_details"))
									# OpenAI streaming: refusal may stream in delta.refusal while content is empty.
									refusal_txt = delta.get("refusal")
									if isinstance(refusal_txt, str) and refusal_txt:
										content = (content or "") + refusal_txt
								else:
									content = None
								finish = c.get("finish_reason")
								if finish is None and isinstance(delta, dict):
									finish = delta.get("finish_reason")
						if finish is None:
							finish = data.get("finish_reason") if isinstance(data, dict) else None
						# OpenAI Responses API and other choice-less SSE shapes.
						if not choices:
							evt_type = str(data.get("type", "")).lower()
							if "reasoning" in evt_type or "thinking" in evt_type:
								reasoning = _extract_reasoning_text(data.get("delta")) or _extract_reasoning_text(data)
							elif "text.delta" in evt_type or "output_text.delta" in evt_type:
								raw_d = data.get("delta")
								if isinstance(raw_d, str):
									content = raw_d
								else:
									content = _extract_reasoning_text(raw_d) or _extract_reasoning_text(
										data.get("text") or ""
									)
							elif "response.output_item.added" in evt_type:
								item = data.get("item") or {}
								item_content = item.get("content")
								text_from_parts, reasoning_from_parts = _split_text_and_reasoning_from_parts(item_content)
								content = text_from_parts
								reasoning = reasoning_from_parts
						if content is not None and not isinstance(content, str):
							content = str(content)
						content = content or ""
						if think_chain_states and content and not structured_reasoning_seen:
							content, think_from_tags = _apply_think_chain_to_chunk(content, think_chain_states)
							if think_from_tags:
								reasoning = f"{reasoning}{think_from_tags}" if reasoning else think_from_tags
						if (reasoning or "").strip():
							structured_reasoning_seen = True
						yield type("StreamEvent", (), {
							"choices": [StreamChoice(ChoiceDelta(content, reasoning=reasoning), finish)],
							"usage": usage,
						})()
					except (json.JSONDecodeError, KeyError, TypeError, AttributeError):
						pass
		finally:
			try:
				resp.close()
			except Exception:
				pass

	def _parse_chat_completion(self, data: dict) -> ChatCompletion:
		"""Parse JSON response into ChatCompletion."""
		choices = []
		for i, c in enumerate(data.get("choices", [])):
			msg = c.get("message") or c
			if not isinstance(msg, dict):
				msg = {}
			reasoning_text = ""
			content_val = msg.get("content")
			if isinstance(content_val, list):
				content, reasoning_text = _split_text_and_reasoning_from_parts(content_val)
			else:
				content = content_val or c.get("text") or ""
			if not reasoning_text:
				for key in ("reasoning", "reasoning_content", "thinking", "thinking_content", "reasoning_details", "thought"):
					candidate = _extract_reasoning_text(msg.get(key))
					if candidate:
						reasoning_text = candidate
						break
			if not reasoning_text:
				for key in ("reasoning", "reasoning_content", "thinking", "thinking_content", "reasoning_details", "thought"):
					candidate = _extract_reasoning_text(c.get(key))
					if candidate:
						reasoning_text = candidate
						break
			if content is not None and not isinstance(content, str):
				content = str(content)
			content = content or ""
			provider = getattr(self, "provider", "")
			if content and _should_apply_inline_think_strip(provider, bool((reasoning_text or "").strip())):
				visible, think_inline, _ = _split_ollama_think_inline(content, in_think=False)
				content = visible
				if think_inline:
					reasoning_text = f"{reasoning_text}{think_inline}" if reasoning_text else think_inline
			audio = msg.get("audio")
			if isinstance(audio, dict) and audio.get("data"):
				choices.append(Choice(ChoiceMessage(content, audio=audio, reasoning=reasoning_text), index=i))
			else:
				choices.append(Choice(ChoiceMessage(content, reasoning=reasoning_text), index=i))
		return ChatCompletion(choices, usage=_normalize_usage_from_payload(data))

	def _upload_openai_user_file(self, file_path: str, purpose: str = "user_data") -> str:
		"""Upload local file to OpenAI /files and return file id."""
		if not isinstance(file_path, str) or not file_path or not os.path.exists(file_path):
			raise APIError(f"Invalid file path: {file_path}")
		boundary = uuid.uuid4().hex
		filename = os.path.basename(file_path)
		for ch in '\r\n"\\':
			filename = filename.replace(ch, "_")
		file_mime = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
		with open(file_path, "rb") as f:
			file_data = f.read()
		body = (
			f'--{boundary}\r\n'
			f'Content-Disposition: form-data; name="purpose"\r\n\r\n'
			f'{purpose}\r\n'
			f'--{boundary}\r\n'
			f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
			f"Content-Type: {file_mime}\r\n\r\n"
		).encode("utf-8") + file_data + (
			f"\r\n--{boundary}--\r\n"
		).encode("utf-8")
		url = f"{self.base_url}/files"
		headers = _build_headers(self.api_key, self.organization)
		headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
		req = urllib.request.Request(url, data=body, headers=headers, method="POST")
		try:
			with self._opener.open(req, timeout=180) as resp:
				raw = resp.read().decode("utf-8", errors="replace")
				if resp.status != 200:
					raise APIStatusError(
						_resolve_error_message(raw, resp.status),
						status_code=resp.status,
						response_body=raw,
					)
				payload = json.loads(raw) if raw else {}
				file_id = payload.get("id") if isinstance(payload, dict) else ""
				if not isinstance(file_id, str) or not file_id.strip():
					raise APIError("File upload succeeded but no file id was returned.")
				return file_id.strip()
		except urllib.error.HTTPError as e:
			text = e.read().decode("utf-8", errors="replace") if e.fp else ""
			raise APIStatusError(
				_resolve_error_message(text, e.code),
				status_code=e.code,
				response_body=text,
			)
		except (urllib.error.URLError, OSError, ConnectionError) as e:
			raise APIConnectionError(str(e)) from e

	def _messages_to_responses_input(self, messages: list) -> list:
		"""Convert chat-completions messages to OpenAI Responses input format."""
		if not isinstance(messages, list):
			return []
		output = []
		for msg in messages:
			if not isinstance(msg, dict):
				continue
			role = (msg.get("role") or "user").lower()
			content = msg.get("content", "")
			if isinstance(content, str):
				text = content.strip()
				if not text:
					continue
				output.append({"role": role, "content": [{"type": "input_text", "text": text}]})
				continue
			if not isinstance(content, list):
				continue
			parts = []
			for part in content:
				if not isinstance(part, dict):
					continue
				part_type = part.get("type")
				if part_type == "text":
					text = part.get("text", "")
					if text:
						parts.append({"type": "input_text", "text": text})
				elif part_type == "image_url":
					image = part.get("image_url") or {}
					url = image.get("url")
					if isinstance(url, str) and url:
						parts.append({"type": "input_image", "image_url": url})
				elif part_type == "input_audio":
					audio = part.get("input_audio") or {}
					data = audio.get("data")
					fmt = audio.get("format")
					if data:
						parts.append({"type": "input_audio", "input_audio": {"data": data, "format": fmt or "wav"}})
				elif part_type == "input_file":
					if isinstance(part.get("file_id"), str) and part["file_id"].strip():
						parts.append({"type": "input_file", "file_id": part["file_id"].strip()})
						continue
					if isinstance(part.get("file_url"), str) and part["file_url"].strip():
						parts.append({"type": "input_file", "file_url": part["file_url"].strip()})
						continue
					if isinstance(part.get("file_data"), str) and part["file_data"].strip():
						file_part = {
							"type": "input_file",
							"file_data": part["file_data"].strip(),
						}
						if part.get("filename"):
							file_part["filename"] = part.get("filename")
						parts.append(file_part)
						continue
					file_path = part.get("file_path")
					if isinstance(file_path, str) and file_path:
						file_id = self._upload_openai_user_file(file_path, purpose="user_data")
						parts.append({"type": "input_file", "file_id": file_id})
			if parts:
				output.append({"role": role, "content": parts})
		return output

	def _parse_responses_completion(self, data: dict) -> ChatCompletion:
		"""Parse /responses JSON into ChatCompletion-like object."""
		text_parts = []
		reasoning_parts = []
		output_text = data.get("output_text")
		if isinstance(output_text, str) and output_text:
			text_parts.append(output_text)
		for item in data.get("output", []) if isinstance(data, dict) else []:
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
		provider = getattr(self, "provider", "")
		if text and _should_apply_inline_think_strip(provider, bool(reasoning.strip())):
			visible, think_inline, _ = _split_ollama_think_inline(text, in_think=False)
			text = visible.strip()
			if think_inline:
				reasoning = f"{reasoning}\n{think_inline}".strip() if reasoning else think_inline
		return ChatCompletion(
			[Choice(ChoiceMessage(content=text, reasoning=reasoning))],
			usage=_normalize_usage_from_payload(data),
		)

	def _openai_responses_create(
		self,
		*,
		model: str,
		messages: list,
		stream: bool = False,
		**kwargs,
	) -> ChatCompletion | Generator:
		"""OpenAI Responses API path for richer document input support."""
		input_payload = self._messages_to_responses_input(messages)
		if not input_payload:
			raise APIError("No valid messages for OpenAI Responses API request.")
		body = {"model": model, "input": input_payload, "stream": stream}
		for key, value in kwargs.items():
			if value is None:
				continue
			if key in ("messages", "stream", "stream_options"):
				continue
			if key in ("max_tokens", "max_completion_tokens"):
				body["max_output_tokens"] = value
				continue
			if key == "reasoning_effort":
				body["reasoning"] = {"effort": value}
				continue
			body[key] = value
		req = self._request("POST", "/responses", body=body)
		try:
			if stream:
				resp = self._opener.open(req, timeout=180)
				if resp.status != 200:
					text = resp.read().decode("utf-8", errors="replace")
					resp.close()
					raise APIStatusError(
						_resolve_error_message(text, resp.status),
						status_code=resp.status,
						response_body=text,
					)
				return self._stream_chat(resp)
			with self._opener.open(req, timeout=180) as resp:
				raw = resp.read().decode("utf-8", errors="replace")
				if resp.status != 200:
					raise APIStatusError(
						_resolve_error_message(raw, resp.status),
						status_code=resp.status,
						response_body=raw,
					)
				data = json.loads(raw) if raw else {}
				return self._parse_responses_completion(data if isinstance(data, dict) else {})
		except urllib.error.HTTPError as e:
			text = e.read().decode("utf-8", errors="replace") if e.fp else ""
			raise APIStatusError(
				_resolve_error_message(text, e.code),
				status_code=e.code,
				response_body=text,
			)
		except (urllib.error.URLError, OSError, ConnectionError) as e:
			raise APIConnectionError(str(e)) from e

	def _anthropic_chat_completions_create(
		self,
		*,
		model: str,
		messages: list,
		stream: bool = False,
		**kwargs,
	) -> ChatCompletion | Generator:
		"""Create chat completion via Anthropic Messages API."""
		system, anthropic_msgs = _convert_messages_to_anthropic(messages)
		if not anthropic_msgs:
			raise APIError("No valid messages for Anthropic")
		max_tokens = kwargs.get("max_tokens") or kwargs.get("max_completion_tokens") or 4096
		body = {
			"model": model,
			"max_tokens": max_tokens,
			"messages": anthropic_msgs,
			"stream": stream,
		}
		if system:
			body["system"] = system
		# Anthropic API: temperature and top_p cannot both be specified
		temp, top_p = kwargs.get("temperature"), kwargs.get("top_p")
		if temp is not None:
			body["temperature"] = temp
		elif top_p is not None:
			body["top_p"] = top_p
		if kwargs.get("top_k") is not None:
			body["top_k"] = kwargs["top_k"]
		stop_kw = kwargs.get("stop")
		if stop_kw is not None:
			seq = []
			if isinstance(stop_kw, str) and stop_kw.strip():
				seq = [stop_kw.strip()]
			elif isinstance(stop_kw, list):
				seq = [s.strip() for s in stop_kw if isinstance(s, str) and s.strip()]
			if seq:
				body["stop_sequences"] = seq[:16]
		# Extended thinking (reasoning) - Anthropic API spec.
		# effort belongs in output_config and must be model-compatible.
		caps = get_anthropic_thinking_profile(model)
		if kwargs.get("reasoning_enabled"):
			if caps["adaptive_only"]:
				body["thinking"] = {"type": "adaptive"}
			elif caps["adaptive_supported"] and kwargs.get("adaptive_thinking", True):
				body["thinking"] = {"type": "adaptive"}
			else:
				body["thinking"] = {"type": "enabled", "budget_tokens": 10000}
			# Claude 4.7/Mythos default to omitted thinking output;
			# request summarized output so history can display <think>...</think>.
			body["thinking"]["display"] = "summarized"
		if kwargs.get("reasoning_enabled") and caps["effort_supported"]:
			effort = normalize_effort(
				kwargs.get("reasoning_effort", "high"),
				tuple(caps.get("effort_levels") or ()),
				default="high",
			)
			body["output_config"] = {"effort": effort}
		# Web search tool - Anthropic API spec (web_search_20250305 is GA, works on all supported models)
		if kwargs.get("web_search_options") is not None:
			body["tools"] = [{"type": "web_search_20250305", "name": "web_search"}]
		url = f"{self.base_url}/messages"
		headers = _build_anthropic_headers(self.api_key)
		data = json.dumps(body).encode("utf-8")
		req = urllib.request.Request(url, data=data, headers=headers, method="POST")
		try:
			if stream:
				resp = self._opener.open(req, timeout=120)
				if resp.status != 200:
					text = resp.read().decode("utf-8", errors="replace")
					resp.close()
					raise APIStatusError(
						_resolve_error_message(text, resp.status),
						status_code=resp.status,
						response_body=text,
					)
				return self._stream_anthropic(resp)
			with self._opener.open(req, timeout=120) as resp:
				if resp.status != 200:
					text = resp.read().decode("utf-8", errors="replace")
					raise APIStatusError(
						_resolve_error_message(text, resp.status),
						status_code=resp.status,
						response_body=text,
					)
				data = json.loads(resp.read().decode("utf-8"))
				return self._parse_anthropic_response(data)
		except urllib.error.HTTPError as e:
			text = e.read().decode("utf-8", errors="replace") if e.fp else ""
			raise APIStatusError(
				_resolve_error_message(text, e.code),
				status_code=e.code,
				response_body=text,
			)
		except (urllib.error.URLError, OSError, ConnectionError) as e:
			raise APIConnectionError(str(e)) from e

	def _parse_anthropic_response(self, data: dict) -> ChatCompletion:
		"""Parse Anthropic message response into ChatCompletion."""
		content_blocks = data.get("content", [])
		text = ""
		reasoning = ""
		for blk in content_blocks:
			if not isinstance(blk, dict):
				continue
			blk_type = str(blk.get("type", "")).lower()
			if blk_type == "text":
				text += blk.get("text", "")
			elif "thinking" in blk_type or "reasoning" in blk_type:
				part = _extract_reasoning_text(blk)
				if part:
					reasoning = f"{reasoning}\n{part}".strip() if reasoning else part
		choices = [Choice(ChoiceMessage(text, reasoning=reasoning))]
		return ChatCompletion(choices, usage=_normalize_usage(data.get("usage")))

	def _stream_anthropic(self, resp) -> Generator:
		"""Parse Anthropic SSE stream and yield OpenAI-compatible events."""
		try:
			buf = b""
			for chunk in resp:
				buf += chunk
				while b"\n" in buf or b"\r\n" in buf:
					line, buf = buf.split(b"\n", 1) if b"\n" in buf else (buf, b"")
					line = line.strip()
					if not line.startswith(b"data: "):
						continue
					payload = line[6:].strip()
					if payload == b"[DONE]" or not payload:
						continue
					try:
						data = json.loads(payload.decode("utf-8"))
						usage = {}
						if data.get("type") == "message_delta":
							usage = _normalize_usage(data.get("usage"))
						if data.get("type") == "content_block_delta":
							delta = data.get("delta") or {}
							if delta.get("type") == "text_delta":
								content = delta.get("text", "") or ""
								yield type("StreamEvent", (), {
									"choices": [StreamChoice(ChoiceDelta(content), None)],
									"usage": usage,
								})()
							elif delta.get("type") in ("thinking_delta", "reasoning_delta"):
								th = delta.get("thinking")
								reasoning = th if isinstance(th, str) else _extract_reasoning_text(delta)
								yield type("StreamEvent", (), {
									"choices": [StreamChoice(ChoiceDelta("", reasoning=reasoning), None)],
									"usage": usage,
								})()
						elif usage:
							yield type("StreamEvent", (), {
								"choices": [StreamChoice(ChoiceDelta(""), None)],
								"usage": usage,
							})()
					except (json.JSONDecodeError, KeyError):
						pass
		finally:
			try:
				resp.close()
			except Exception:
				pass

	def audio_transcriptions_create(
		self,
		*,
		model: str = "whisper-1",
		file: BinaryIO,
		response_format: str = "json",
		**kwargs,
	) -> "Transcription":
		"""Transcribe audio file via OpenAI-compatible transcription API."""
		return self._audio_text_create(
			endpoint="/audio/transcriptions",
			model=model,
			file=file,
			response_format=response_format,
			**kwargs,
		)

	def audio_translations_create(
		self,
		*,
		model: str = "whisper-1",
		file: BinaryIO,
		response_format: str = "json",
		**kwargs,
	) -> "Transcription":
		"""Translate audio file via OpenAI-compatible translation API."""
		return self._audio_text_create(
			endpoint="/audio/translations",
			model=model,
			file=file,
			response_format=response_format,
			**kwargs,
		)

	def _audio_text_create(
		self,
		*,
		endpoint: str,
		model: str,
		file: BinaryIO,
		response_format: str,
		**kwargs,
	) -> "Transcription":
		"""Shared multipart handler for /audio/transcriptions and /audio/translations."""
		boundary = uuid.uuid4().hex
		file_data = file.read()
		file_name = os.path.basename(getattr(file, "name", "") or "audio.wav")
		ext = os.path.splitext(file_name)[1].lower() or ".wav"
		file_mime = _AUDIO_MIME.get(ext, "audio/wav")
		parts = []

		def _add_field(name: str, value: Any):
			if value is None:
				return
			if isinstance(value, (list, tuple)):
				for item in value:
					_add_field(name, item)
				return
			if isinstance(value, dict):
				value = json.dumps(value, ensure_ascii=False)
			parts.append(
				(
					f'--{boundary}\r\n'
					f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
					f'{value}\r\n'
				).encode("utf-8")
			)

		_add_field("model", model)
		_add_field("response_format", response_format)
		for k, v in kwargs.items():
			_add_field(k, v)

		file_part = (
			f'--{boundary}\r\n'
			f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'
			f'Content-Type: {file_mime}\r\n\r\n'
		).encode("utf-8") + file_data + b"\r\n"
		body = b"".join(parts) + file_part + (f'--{boundary}--\r\n').encode("utf-8")
		url = f"{self.base_url}{endpoint}"
		headers = _build_headers(self.api_key, self.organization)
		headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
		req = urllib.request.Request(url, data=body, headers=headers, method="POST")

		try:
			with self._opener.open(req, timeout=120) as resp:
				if resp.status != 200:
					text = resp.read().decode("utf-8", errors="replace")
					raise APIStatusError(
						_resolve_error_message(text, resp.status),
						status_code=resp.status,
						response_body=text,
					)
				raw = resp.read().decode("utf-8", errors="replace")
				if response_format in ("json", "verbose_json", "diarized_json"):
					result = json.loads(raw) if raw else {}
					if isinstance(result, dict):
						text = result.get("text", "")
					else:
						text = str(result)
					return Transcription(text, payload=result, response_format=response_format)
				# text-like formats: text/srt/vtt
				return Transcription(raw, payload=raw, response_format=response_format)
		except urllib.error.HTTPError as e:
			text = e.read().decode("utf-8", errors="replace") if e.fp else ""
			raise APIStatusError(
				_resolve_error_message(text, e.code),
				status_code=e.code,
				response_body=text,
			)
		except (urllib.error.URLError, OSError, ConnectionError) as e:
			raise APIConnectionError(str(e)) from e

	def audio_speech_create(
		self,
		*,
		model: str,
		voice: str = "",
		input: str,
		response_format: str = "mp3",
		**kwargs,
	) -> bytes:
		"""Create speech from text. Returns raw bytes."""
		body = {
			"model": model,
			"input": input,
			"response_format": response_format,
		}
		if voice:
			body["voice"] = voice
		for k, v in kwargs.items():
			if v is None:
				continue
			body[k] = v
		req = self._request("POST", "/audio/speech", body=body)
		try:
			with self._opener.open(req, timeout=60) as resp:
				if resp.status != 200:
					text = resp.read().decode("utf-8", errors="replace")
					raise APIStatusError(
						_resolve_error_message(text, resp.status),
						status_code=resp.status,
						response_body=text,
					)
				raw = resp.read()
				content_type = (resp.headers.get("Content-Type") or "").lower()
				# Some providers (e.g. Voxtral endpoints) return JSON with base64 audio_data.
				is_json = "application/json" in content_type or "text/json" in content_type
				if is_json:
					try:
						payload = json.loads(raw.decode("utf-8", errors="replace"))
						audio = _extract_audio_bytes_from_json_payload(payload)
						if audio:
							return audio
						raise APIStatusError(
							"No audio payload found in JSON TTS response.",
							status_code=resp.status,
							response_body=str(payload),
						)
					except json.JSONDecodeError:
						pass
				return raw
		except urllib.error.HTTPError as e:
			text = e.read().decode("utf-8", errors="replace") if e.fp else ""
			raise APIStatusError(
				_resolve_error_message(text, e.code),
				status_code=e.code,
				response_body=text,
			)
		except (urllib.error.URLError, OSError, ConnectionError) as e:
			raise APIConnectionError(str(e)) from e


class Transcription:
	"""Mimics openai.types.audio.transcription.Transcription."""
	def __init__(self, text: str, payload: Any = None, response_format: str = "json"):
		self.text = text or ""
		self.payload = payload
		self.response_format = response_format


_AUDIO_MIME = {
	".wav": "audio/wav",
	".mp3": "audio/mpeg",
	".m4a": "audio/mp4",
	".webm": "audio/webm",
	".mp4": "audio/mp4",
	".flac": "audio/flac",
	".ogg": "audio/ogg",
	".mpga": "audio/mpeg",
	".mpeg": "audio/mpeg",
}


def transcribe_audio_mistral(
	api_key: str,
	file_path: str,
	model: str = "voxtral-mini-latest",
	language: Optional[str] = None,
) -> "Transcription":
	"""
	Transcribe audio via Mistral Voxtral API.
	POST https://api.mistral.ai/v1/audio/transcriptions
	Uses x-api-key auth and multipart form-data per official docs.
	"""
	if not api_key or not api_key.strip():
		raise ValueError("Mistral API key is required for transcription")
	url = "https://api.mistral.ai/v1/audio/transcriptions"
	boundary = uuid.uuid4().hex
	with open(file_path, "rb") as f:
		file_data = f.read()

	ext = "." + file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ".wav"
	filename = os.path.basename(file_path) or "audio.wav"
	mime = _AUDIO_MIME.get(ext, "audio/wav")

	body = (
		f'--{boundary}\r\n'
		f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
		f'Content-Type: {mime}\r\n\r\n'
	).encode() + file_data

	body += (
		f'\r\n--{boundary}\r\n'
		f'Content-Disposition: form-data; name="model"\r\n\r\n'
		f'{model}\r\n'
	).encode()

	if language:
		body += (
			f'\r\n--{boundary}\r\n'
			f'Content-Disposition: form-data; name="language"\r\n\r\n'
			f'{language}\r\n'
		).encode()

	body += (f'\r\n--{boundary}--\r\n').encode()

	headers = {
		"x-api-key": api_key.strip(),
		"Content-Type": f"multipart/form-data; boundary={boundary}",
	}
	req = urllib.request.Request(url, data=body, headers=headers, method="POST")
	opener = _create_opener()

	try:
		with opener.open(req, timeout=300) as resp:
			if resp.status != 200:
				text = resp.read().decode("utf-8", errors="replace")
				raise APIStatusError(
					_resolve_error_message(text, resp.status),
					status_code=resp.status,
					response_body=text,
				)
			result = json.loads(resp.read().decode("utf-8"))
			return Transcription(result.get("text", ""))
	except urllib.error.HTTPError as e:
		text = e.read().decode("utf-8", errors="replace") if e.fp else ""
		raise APIStatusError(
			_resolve_error_message(text, e.code),
			status_code=e.code,
			response_body=text,
		)
	except (urllib.error.URLError, OSError, ConnectionError) as e:
		raise APIConnectionError(str(e)) from e


class _ChatCompletions:
	"""Mimics client.chat.completions."""
	def __init__(self, client: OpenAIClient):
		self._client = client
		self.completions = self  # client.chat.completions.create() compatibility

	def create(self, **kwargs):
		return self._client.chat_completions_create(**kwargs)


class _AudioTranscriptions:
	"""Mimics client.audio.transcriptions."""
	def __init__(self, client: OpenAIClient):
		self._client = client

	def create(self, **kwargs):
		return self._client.audio_transcriptions_create(**kwargs)


class _AudioSpeech:
	"""Mimics client.audio.speech."""
	def __init__(self, client: OpenAIClient):
		self._client = client

	def create(self, **kwargs) -> "_TTSResponse":
		"""Create speech and return wrapper with stream_to_file."""
		data = self._client.audio_speech_create(**kwargs)
		return _TTSResponse(data)


class _Audio:
	"""Mimics client.audio."""
	def __init__(self, client: OpenAIClient):
		self.transcriptions = _AudioTranscriptions(client)
		self.translations = _AudioTranslations(client)
		self.speech = _AudioSpeech(client)
		self._client = client


class _AudioTranslations:
	"""Mimics client.audio.translations."""
	def __init__(self, client: OpenAIClient):
		self._client = client

	def create(self, **kwargs):
		return self._client.audio_translations_create(**kwargs)


class _TTSResponse:
	"""Wrapper for TTS binary response to support stream_to_file."""
	def __init__(self, data: bytes):
		self._data = data

	def stream_to_file(self, path: str):
		with open(path, "wb") as f:
			f.write(self._data)


def _resolve_error_message(body: str, status: int) -> str:
	"""Extract error message from API response body."""
	if not body:
		return f"HTTP {status}"
	try:
		data = json.loads(body)
		if not isinstance(data, dict):
			return str(data) if data else body or f"HTTP {status}"
		err = data.get("error", {})
		if isinstance(err, dict):
			return err.get("message", err.get("code", body)) or body
		return str(err)
	except json.JSONDecodeError:
		return body or f"HTTP {status}"


def truncate_error_for_user(err, max_len: int = 300) -> str:
	"""Return user-facing error string, truncated if needed."""
	msg = str(err) if err else ""
	if len(msg) < max_len:
		return msg
	return msg[:max_len] + "..."


def configure_client_for_provider(client, provider: str, account_id: str = None, clone: bool = False):
	"""Set client base_url, api_key, organization for provider/account and return configured client."""
	if clone and hasattr(client, "clone"):
		client = client.clone()
	manager = apikeymanager.get(provider)
	client.base_url = manager.get_base_url(account_id=account_id) or BASE_URLs[provider]
	api_key = manager.get_api_key(account_id=account_id)
	if provider == "Ollama" and not (api_key and str(api_key).strip()):
		api_key = "ollama"
	client.api_key = api_key
	client.organization = manager.get_organization_key(account_id=account_id)
	client.provider = provider
	client.account_id = account_id
	return client
