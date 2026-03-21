# coding: UTF-8
"""Persistent media helpers for OpenAI add-on."""

import datetime
import os
import shutil
import uuid

from .consts import DATA_DIR, TEMP_DIR, ensure_dir_exists

MEDIA_DIR = os.path.join(DATA_DIR, "media")


def ensure_media_dir():
	ensure_dir_exists(DATA_DIR)
	ensure_dir_exists(MEDIA_DIR)


def _safe_ext(path, fallback=".bin"):
	ext = os.path.splitext(path or "")[1].lower()
	if ext:
		return ext
	return fallback


def build_media_path(category: str, ext: str, prefix: str = "asset") -> str:
	"""Return unique path in DATA_DIR/media/<category>."""
	ensure_media_dir()
	category_dir = os.path.join(MEDIA_DIR, category)
	ensure_dir_exists(category_dir)
	if not ext.startswith("."):
		ext = "." + ext
	now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
	return os.path.join(category_dir, f"{prefix}_{now}_{uuid.uuid4().hex[:8]}{ext}")


def persist_local_file(path: str, category: str, prefix: str = "asset", fallback_ext=".bin") -> str:
	"""
	Copy file into DATA_DIR/media/<category> when needed.
	Returns original path for non-local URLs or already-persistent files.
	"""
	if not path:
		return path
	if path.startswith("http://") or path.startswith("https://"):
		return path
	if not os.path.isfile(path):
		return path
	abs_path = os.path.abspath(path)
	abs_media = os.path.abspath(MEDIA_DIR)
	if abs_path.startswith(abs_media):
		return path
	# Persist temp files to avoid losing attachments after cleanup.
	abs_temp = os.path.abspath(TEMP_DIR)
	if not abs_path.startswith(abs_temp):
		return path
	dst = build_media_path(category, _safe_ext(path, fallback_ext), prefix=prefix)
	shutil.copy2(path, dst)
	return dst
