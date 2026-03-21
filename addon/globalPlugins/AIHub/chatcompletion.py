# coding: UTF-8
"""Chat completion thread implementation."""
import base64
import json
import os
import threading
import time
import uuid
import winsound
import wx

import addonHandler
import gui
from logHandler import log

from .apiclient import Choice, ChatCompletion, configure_client_for_provider
from .consts import TEMP_DIR, TOP_P_MIN, TOP_P_MAX, TTS_DEFAULT_VOICE, stop_progress_sound
from .consts import SND_PROGRESS, SND_CHAT_RESPONSE_PENDING, SND_CHAT_RESPONSE_SENT
from .history import HistoryBlock
from .mediastore import persist_local_file
from .recordthread import transcribe_audio_file
from .resultevent import ResultEvent

addonHandler.initTranslation()


class CompletionThread(threading.Thread):
	def __init__(self, notifyWindow):
		threading.Thread.__init__(self, daemon=True)
		self._notifyWindow = notifyWindow
		self._wantAbort = False
		self.lastTime = int(time.time())

	def _log_timing(self, debug, label, elapsed):
		if debug and elapsed is not None:
			log.info("OpenAI [timing] %s: %.2fs", label, elapsed)

	def _set_block_usage_from_response(self, block, response):
		"""Copy normalized usage fields from response to HistoryBlock."""
		usage = getattr(response, "usage", None)
		if not isinstance(usage, dict) or not usage:
			return
		def _to_int(value):
			try:
				return int(value or 0)
			except (TypeError, ValueError):
				return 0
		block.usage = {
			"input_tokens": _to_int(usage.get("input_tokens")),
			"output_tokens": _to_int(usage.get("output_tokens")),
			"total_tokens": _to_int(usage.get("total_tokens")),
			"prompt_tokens": _to_int(usage.get("prompt_tokens")),
			"completion_tokens": _to_int(usage.get("completion_tokens")),
			"reasoning_tokens": _to_int(usage.get("reasoning_tokens")),
			"cached_input_tokens": _to_int(usage.get("cached_input_tokens")),
			"cache_creation_input_tokens": _to_int(usage.get("cache_creation_input_tokens")),
			"input_audio_tokens": _to_int(usage.get("input_audio_tokens")),
			"output_audio_tokens": _to_int(usage.get("output_audio_tokens")),
		}
		if "cost" in usage:
			try:
				block.usage["cost"] = float(usage.get("cost"))
			except (TypeError, ValueError):
				pass

	def _apply_pricing_if_missing(self, block, model):
		usage = getattr(block, "usage", None)
		if not isinstance(usage, dict):
			return
		if isinstance(usage.get("cost"), (int, float)):
			return
		pricing = {}
		if getattr(model, "extraInfo", None) and isinstance(model.extraInfo, dict):
			pricing = model.extraInfo.get("pricing", {})
		if not isinstance(pricing, dict) or not pricing:
			return
		def _to_float(value):
			try:
				return float(value or 0.0)
			except (TypeError, ValueError):
				return 0.0
		def _to_int(value):
			try:
				return int(value or 0)
			except (TypeError, ValueError):
				return 0
		input_tokens = _to_int(usage.get("input_tokens"))
		output_tokens = _to_int(usage.get("output_tokens"))
		cached_read_tokens = _to_int(usage.get("cached_input_tokens"))
		cache_write_tokens = _to_int(usage.get("cache_creation_input_tokens"))
		audio_tokens = _to_int(usage.get("input_audio_tokens")) + _to_int(usage.get("output_audio_tokens"))
		regular_input_tokens = max(0, input_tokens - cached_read_tokens - cache_write_tokens)
		prompt_rate = _to_float(pricing.get("prompt"))
		completion_rate = _to_float(pricing.get("completion"))
		cache_read_rate = _to_float(pricing.get("input_cache_read"))
		cache_write_rate = _to_float(pricing.get("input_cache_write"))
		audio_rate = _to_float(pricing.get("audio"))
		request_rate = _to_float(pricing.get("request"))
		cost = (
			(regular_input_tokens * prompt_rate)
			+ (output_tokens * completion_rate)
			+ (cached_read_tokens * cache_read_rate)
			+ (cache_write_tokens * cache_write_rate)
			+ (audio_tokens * audio_rate)
			+ request_rate
		)
		if cost > 0:
			usage["cost"] = float(cost)

	def _maybe_build_document_support_error(self, err, provider, document_count):
		"""Return a clearer provider-specific document failure message when possible."""
		if document_count <= 0:
			return None
		base_message = str(getattr(err, "message", "") or err or "")
		if not base_message:
			return None
		lower = base_message.lower()
		indicators = (
			"input_file",
			"document",
			"pdf",
			"unsupported",
			"not support",
			"invalid type",
			"invalid_request_error",
			"media_type",
			"file_id",
			"file_data",
		)
		if not any(flag in lower for flag in indicators):
			return None
		if provider == "Anthropic":
			hint = _(
				"Anthropic document support is best-effort here (PDF as document blocks, text files inlined). "
				"If this file is rejected, try OpenAI provider for native Responses file-input support."
			)
		elif provider == "Google":
			hint = _(
				"Google document support is best-effort through compatibility endpoints. "
				"Try OpenAI provider for native Responses file-input support, or convert the file to PDF/text."
			)
		elif provider != "OpenAI":
			hint = _(
				"This provider uses a best-effort document compatibility path and may reject some file types. "
				"Try OpenAI provider for native Responses file-input support."
			)
		else:
			hint = _(
				"The selected model/provider rejected this document. "
				"Try another OpenAI model with document support or use a supported document format."
			)
		return f"{base_message}\n\n{hint}"

	def run(self):
		wnd = self._notifyWindow
		client = wnd.client
		conf = wnd.conf
		data = wnd.data
		block = HistoryBlock()
		system = wnd.systemTextCtrl.GetValue().strip()
		block.system = system
		prompt = getattr(wnd, "_askPromptOverride", None)
		if prompt is not None:
			delattr(wnd, "_askPromptOverride")
		else:
			prompt = wnd.promptTextCtrl.GetValue().strip()
		block.prompt = prompt
		model = wnd.getCurrentModel()
		block.model = model.id
		stream = conf["stream"]
		debug = conf["debug"]
		t0 = time.perf_counter()
		maxTokens = wnd.maxTokensSpinCtrl.GetValue()
		block.maxTokens = maxTokens
		data["maxTokens_%s" % model.id] = maxTokens
		temperature = 1
		topP = 1
		if conf["advancedMode"]:
			temperature = wnd.temperatureSpinCtrl.GetValue() / 100
			data["temperature_%s" % model.id] = wnd.temperatureSpinCtrl.GetValue()
			topP = wnd.topPSpinCtrl.GetValue() / 100
			conf["topP"] = wnd.topPSpinCtrl.GetValue()
			debug = wnd.debugModeCheckBox.IsChecked()
			conf["debug"] = debug
			stream = wnd.streamModeCheckBox.IsChecked()
			conf["stream"] = stream
		block.temperature = temperature
		block.topP = topP
		block.pathList = wnd.pathList.copy()
		block.audioPathList = wnd.audioPathList.copy()
		block.timing = {"startedAt": time.time()}

		current_audio_transcripts = None
		if wnd.audioPathList:
			wnd.message(_("Transcribing audio..."))
			try:
				t_transcribe_start = time.perf_counter()
				transcripts = []
				for path in wnd.audioPathList:
					path_str = path if isinstance(path, str) else getattr(path, "path", str(path))
					t = transcribe_audio_file(path_str, wnd.conf["audio"], wnd.client)
					transcripts.append((t or "").strip())
				self._log_timing(debug, "transcription", time.perf_counter() - t_transcribe_start)
				block.audioTranscriptList = transcripts
				current_audio_transcripts = transcripts
				if not prompt and any(t for t in transcripts):
					block.prompt = "\n".join(t for t in transcripts if t).strip()
			except Exception as err:
				log.error(f"Transcription error: {err}", exc_info=True)
				stop_progress_sound()
				wx.PostEvent(self._notifyWindow, ResultEvent(err))
				return

		if not 0 <= temperature <= model.maxTemperature * 100:
			wx.PostEvent(self._notifyWindow, ResultEvent(_("Invalid temperature")))
			return
		if not TOP_P_MIN <= topP <= TOP_P_MAX:
			wx.PostEvent(self._notifyWindow, ResultEvent(_("Invalid top P")))
			return
		t_build_start = time.perf_counter()
		messages = self._getMessages(system, prompt, current_audio_transcripts)
		self._log_timing(debug, "build messages (incl. history)", time.perf_counter() - t_build_start)
		nbImages = 0
		nbAudio = 0
		nbDocuments = 0
		for message in messages:
			if message["role"] == "user" and not isinstance(message["content"], str):
				for c in message["content"]:
					if c.get("type") == "image_url":
						nbImages += 1
					elif c.get("type") == "input_audio":
						nbAudio += 1
					elif c.get("type") == "input_file":
						nbDocuments += 1
		msg = _("Uploading %s, please wait...") % ", ".join(
			([_("%d image(s)") % nbImages] if nbImages else []) +
			([_("%d audio file(s)") % nbAudio] if nbAudio else []) +
			([_("%d document(s)") % nbDocuments] if nbDocuments else [])
		) if nbImages or nbAudio or nbDocuments else _("Please wait...")
		conf["modelVision" if nbImages else "model"] = model.id
		wnd.message(msg)
		if conf["chatFeedback"]["sndTaskInProgress"]:
			winsound.PlaySound(SND_PROGRESS, winsound.SND_ASYNC | winsound.SND_LOOP)
		account = wnd.getCurrentAccount() if hasattr(wnd, "getCurrentAccount") else None
		account_id = account.get("id") if account and account.get("provider") == model.provider else None
		configure_client_for_provider(client, model.provider, account_id=account_id)
		audio_output = getattr(model, "audioOutput", False)
		use_stream = stream and not audio_output
		params = {
			"model": model.id,
			"messages": messages,
			"stream": use_stream
		}
		if use_stream and model.provider in ("OpenAI", "CustomOpenAI", "OpenRouter", "xAI"):
			# OpenAI-compatible endpoints can return usage in final stream chunk.
			params["stream_options"] = {"include_usage": True}
		if audio_output or nbAudio > 0:
			voice = conf.get("TTSVoice") or TTS_DEFAULT_VOICE
			params["modalities"] = ["text", "audio"]
			params["audio"] = {"voice": voice, "format": "wav"}
		# Add sampling params; respect parameter_conflicts from model metadata
		params_to_add = []
		if "temperature" in model.supportedParameters:
			params_to_add.append(("temperature", temperature))
		if "top_p" in model.supportedParameters:
			params_to_add.append(("top_p", topP))
		conflicts = getattr(model, "parameterConflicts", []) or []
		for group in conflicts:
			group_set = set(group)
			candidates = [(k, v) for k, v in params_to_add if k in group_set]
			if len(candidates) > 1:
				# Pick one: prefer temperature, then top_p, then first in group
				order = ("temperature", "top_p", "top_k")
				chosen = next((c for p in order for c in candidates if c[0] == p), candidates[0])
				params_to_add = [(k, v) for k, v in params_to_add if (k, v) == chosen or k not in group_set]
		for k, v in params_to_add:
			params[k] = v
		reasoningEnabled = wnd.reasoningModeCheckBox.IsChecked()
		useReasoning = getattr(model, "reasoning", False) and reasoningEnabled
		if useReasoning and "include_reasoning" in getattr(model, "supportedParameters", []):
			params["include_reasoning"] = True
		if maxTokens > 0:
			params["max_completion_tokens" if useReasoning else "max_tokens"] = maxTokens
		# Reasoning: provider-specific parameters
		effort = conf.get("reasoningEffort", "medium")
		provider = model.provider
		if useReasoning:
			if provider == "Anthropic":
				params["reasoning_enabled"] = True
				params["reasoning_effort"] = effort
				params["adaptive_thinking"] = conf.get("adaptiveThinking", True)
			elif provider == "Google":
				params["reasoning_effort"] = effort
			elif provider == "xAI":
				# Only grok-3-mini supports reasoning_effort; grok-3/4 reason by default
				if "grok-3-mini" in model.id:
					params["reasoning_effort"] = "high" if effort in ("medium", "high") else "low"
			elif provider in ("OpenAI", "CustomOpenAI", "MistralAI", "OpenRouter"):
				params["reasoning_effort"] = effort
		elif provider == "Google" and "gemini-2.5" in model.id:
			# Gemini 2.5: explicitly disable thinking when user unchecks reasoning
			params["reasoning_effort"] = "none"
		# Web search: provider-specific parameters
		if model.supports_web_search and wnd.webSearchCheckBox.IsChecked():
			provider = model.provider
			if provider == "Anthropic":
				params["web_search_options"] = {}
			elif provider == "Google":
				# Gemini native format for grounding with Google Search
				params["tools"] = [{"google_search": {}}]
		if debug:
			log.info("Client base URL: %s", client.base_url)
			log.info("OpenAI [timing] Messages in request: %d", len(messages))
			if nbImages:
				log.info("%d images", nbImages)
			log.info(json.dumps(params, indent=2, ensure_ascii=False))
		try:
			t_api_start = time.perf_counter()
			block.timing["requestSentAt"] = time.time()
			response = client.chat.completions.create(**params)
			self._log_timing(debug, "API call", time.perf_counter() - t_api_start)
			block.timing["responseReceivedAt"] = time.time()
			if conf["chatFeedback"]["sndResponseSent"]:
				winsound.PlaySound(SND_CHAT_RESPONSE_SENT, winsound.SND_ASYNC)
		except Exception as err:
			log.error("Error when calling the API for model %s: %s", model.id, err, exc_info=True)
			log.error("Parameters used: %s", params)
			stop_progress_sound()
			doc_error = self._maybe_build_document_support_error(err, provider, nbDocuments)
			wx.PostEvent(self._notifyWindow, ResultEvent(doc_error if doc_error else err))
			return
		if wnd.lastBlock is None:
			wnd.firstBlock = wnd.lastBlock = block
		else:
			wnd.lastBlock.next = block
			block.previous = wnd.lastBlock
			wnd.lastBlock = block
		wnd.previousPrompt = wnd.promptTextCtrl.GetValue()
		wnd.promptTextCtrl.Clear()
		try:
			t_resp_start = time.perf_counter()
			if use_stream:
				self._responseWithStream(response, block, debug)
			else:
				self._responseWithoutStream(response, block, debug)
			self._apply_pricing_if_missing(block, model)
			self._log_timing(debug, "response processing", time.perf_counter() - t_resp_start)
		except Exception as err:
			log.error("Error processing response for model %s: %s", model.id, err, exc_info=True)
			stop_progress_sound()
			wx.PostEvent(self._notifyWindow, ResultEvent(err))
			return
		total = time.perf_counter() - t0
		block.timing["finishedAt"] = time.time()
		block.timing["elapsedSec"] = round(total, 3)
		self._finalize_timing_metrics(block)
		self._log_timing(debug, "total", total)
		if debug and total > 10:
			log.info("OpenAI [timing] Request took %.1fs. If 'history' is dominant, reduce conversation length.", total)
		wnd.pathList.clear()
		wnd.audioPathList.clear()
		wx.PostEvent(self._notifyWindow, ResultEvent())

	def _getMessages(self, system=None, prompt=None, current_audio_transcripts=None):
		wnd = self._notifyWindow
		debug = wnd.conf.get("debug", False)
		messages = []
		if system:
			messages.append({"role": "system", "content": system})
		t_hist = time.perf_counter()
		wnd.getMessages(messages)
		self._log_timing(debug, "  history (prior blocks)", time.perf_counter() - t_hist)
		t_cur = time.perf_counter()
		content_parts = []
		if prompt:
			content_parts.append({"type": "text", "text": prompt})
		if wnd.pathList:
			images = wnd.getImages(prompt=None)
			content_parts.extend(images)
		if wnd.audioPathList:
			if current_audio_transcripts and any(t for t in current_audio_transcripts):
				for t in current_audio_transcripts:
					if t:
						content_parts.append({"type": "text", "text": t})
			else:
				content_parts.extend(wnd.getAudioContent(prompt=None))
		self._log_timing(debug, "  current message (images/audio)", time.perf_counter() - t_cur)
		if content_parts:
			messages.append({"role": "user", "content": content_parts})
		elif prompt:
			messages.append({"role": "user", "content": prompt})
		return messages

	def abort(self):
		self._wantAbort = True

	def _finalize_timing_metrics(self, block):
		timing = getattr(block, "timing", None)
		if not isinstance(timing, dict):
			return

		def _as_float(value):
			try:
				return float(value)
			except (TypeError, ValueError):
				return None

		started = _as_float(timing.get("startedAt"))
		request_sent = _as_float(timing.get("requestSentAt"))
		first_token = _as_float(timing.get("firstTokenAt"))
		finished = _as_float(timing.get("finishedAt"))
		if request_sent is not None and started is not None and request_sent >= started:
			timing["timeToRequestSentSec"] = round(request_sent - started, 3)
		if first_token is not None and request_sent is not None and first_token >= request_sent:
			timing["timeToFirstTokenSec"] = round(first_token - request_sent, 3)
		if finished is not None and request_sent is not None and finished >= request_sent:
			timing["timeFromRequestSentToEndSec"] = round(finished - request_sent, 3)
		if finished is not None and first_token is not None and finished >= first_token:
			generation_sec = finished - first_token
			timing["generationDurationSec"] = round(generation_sec, 3)
			usage = getattr(block, "usage", None)
			if isinstance(usage, dict) and generation_sec > 0:
				def _to_int(value):
					try:
						return int(value or 0)
					except (TypeError, ValueError):
						return 0
				output_tokens = _to_int(usage.get("output_tokens")) or _to_int(usage.get("completion_tokens"))
				total_tokens = _to_int(usage.get("total_tokens"))
				if output_tokens > 0:
					timing["outputTokensPerSec"] = round(output_tokens / generation_sec, 3)
				if total_tokens > 0:
					timing["totalTokensPerSec"] = round(total_tokens / generation_sec, 3)

	def _responseWithStream(self, response, block, debug=False):
		wnd = self._notifyWindow
		speechBuffer = ""
		latest_usage = None
		for event in response:
			if time.time() - self.lastTime > 4:
				self.lastTime = int(time.time())
				if wnd.conf["chatFeedback"]["sndResponsePending"]:
					winsound.PlaySound(SND_CHAT_RESPONSE_PENDING, winsound.SND_ASYNC)
			if self._wantAbort or wnd.stopRequest.is_set():
				break
			usage = getattr(event, "usage", None)
			if isinstance(usage, dict) and usage:
				latest_usage = usage
			if not getattr(event, "choices", None) or len(event.choices) < 1:
				continue
			delta = event.choices[0].delta
			if delta and getattr(delta, "reasoning", ""):
				if "firstTokenAt" not in block.timing:
					block.timing["firstTokenAt"] = time.time()
				block.reasoningText += delta.reasoning
			if delta and delta.content:
				text = delta.content
				if "firstTokenAt" not in block.timing:
					block.timing["firstTokenAt"] = time.time()
				speechBuffer += text
				if speechBuffer.endswith("\n") or speechBuffer.endswith(". ") or speechBuffer.endswith("? ") or speechBuffer.endswith("! ") or speechBuffer.endswith(": "):
					if speechBuffer.strip():
						if hasattr(wnd, "canAutoReadStreamingResponse") and wnd.canAutoReadStreamingResponse():
							wnd.message(speechBuffer, speechOnly=True, onPromptFieldOnly=False)
					speechBuffer = ""
				block.responseText += text
		if speechBuffer:
			if hasattr(wnd, "canAutoReadStreamingResponse") and wnd.canAutoReadStreamingResponse():
				wnd.message(speechBuffer, speechOnly=True, onPromptFieldOnly=False)
		if isinstance(latest_usage, dict) and latest_usage:
			block.usage = {
				"input_tokens": int(latest_usage.get("input_tokens", 0) or 0),
				"output_tokens": int(latest_usage.get("output_tokens", 0) or 0),
				"total_tokens": int(latest_usage.get("total_tokens", 0) or 0),
				"prompt_tokens": int(latest_usage.get("prompt_tokens", 0) or 0),
				"completion_tokens": int(latest_usage.get("completion_tokens", 0) or 0),
				"reasoning_tokens": int(latest_usage.get("reasoning_tokens", 0) or 0),
				"cached_input_tokens": int(latest_usage.get("cached_input_tokens", 0) or 0),
				"cache_creation_input_tokens": int(latest_usage.get("cache_creation_input_tokens", 0) or 0),
				"input_audio_tokens": int(latest_usage.get("input_audio_tokens", 0) or 0),
				"output_audio_tokens": int(latest_usage.get("output_audio_tokens", 0) or 0),
			}
			if "cost" in latest_usage:
				try:
					block.usage["cost"] = float(latest_usage.get("cost"))
				except (TypeError, ValueError):
					pass
		block.responseTerminated = True

	def _responseWithoutStream(self, response, block, debug=False):
		wnd = self._notifyWindow
		text = ""
		played_audio = False
		self._set_block_usage_from_response(block, response)
		if "firstTokenAt" not in block.timing:
			first_token_at = block.timing.get("responseReceivedAt")
			if not isinstance(first_token_at, (int, float)):
				first_token_at = time.time()
			block.timing["firstTokenAt"] = float(first_token_at)
		if isinstance(response, (Choice, ChatCompletion)):
			for choice in response.choices:
				if self._wantAbort:
					break
				msg = choice.message
				text += msg.content or ""
				block.reasoningText += getattr(msg, "reasoning", "") or ""
				audio = getattr(msg, "audio", None)
				if isinstance(audio, dict) and audio.get("data"):
					transcript = audio.get("transcript") or ""
					if transcript and not text:
						text = transcript
					try:
						data = base64.b64decode(audio["data"])
						path = os.path.join(TEMP_DIR, f"audio_response_{uuid.uuid4().hex}.wav")
						with open(path, "wb") as f:
							f.write(data)
						path = persist_local_file(path, "audio", prefix="chat_audio", fallback_ext=".wav")
						block.audioPath = path
						import gui
						wx.CallAfter(wnd._playBlockAudio, path)
						played_audio = True
					except Exception as e:
						log.error("Failed to save/play audio response: %s", e, exc_info=True)
						wx.CallAfter(
							lambda: gui.messageBox(
								_("An error occurred playing the audio response. More information is in the NVDA log."),
								_("OpenAI Error"),
								wx.OK | wx.ICON_ERROR
							)
						)
		else:
			raise TypeError(f"Invalid response type: {type(response)}")
		block.responseText += text
		if not played_audio and text:
			if hasattr(wnd, "canAutoReadStreamingResponse") and wnd.canAutoReadStreamingResponse():
				wnd.message(text, speechOnly=True, onPromptFieldOnly=False)
		block.responseTerminated = True


