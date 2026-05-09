"""Reusable transcription helpers: provider resolution, text extraction."""


def get_transcription_provider(conf: dict) -> str:
	"""Resolve transcription provider from config. Backward compat with whisper.cpp.enabled."""
	if conf.get("whisper.cpp", {}).get("enabled", False):
		return "whisper_cpp"
	return conf.get("transcriptionProvider", "openai")


def get_transcription_text(transcription) -> str:
	"""Extract text from Transcription, WhisperTranscription, or str. Returns empty string if None/invalid."""
	if transcription is None:
		return ""
	if isinstance(transcription, str):
		return transcription
	return getattr(transcription, "text", None) or ""
