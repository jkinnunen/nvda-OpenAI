"""Image file handling for the conversation window: ImageFile, types, display size."""
import os
import re
import mimetypes
import urllib.parse

from .imagehelper import get_image_dimensions

URL_PATTERN = re.compile(
	r"^(?:http)s?://(?:[A-Z0-9-]+\.)+[A-Z]{2,6}(?::\d+)?(?:/?|[/?]\S+)$",
	re.IGNORECASE
)


def get_display_size(size):
	if size < 1024:
		return f"{size} B"
	if size < 1024 * 1024:
		return f"{size / 1024:.2f} KB"
	return f"{size / 1024 / 1024:.2f} MB"


class ImageFileTypes:
	UNKNOWN = 0
	IMAGE_LOCAL = 1
	IMAGE_URL = 2
	DOCUMENT_LOCAL = 3
	DOCUMENT_URL = 4


class ImageFile:
	def __init__(
		self,
		path: str,
		name: str = None,
		description: str = None,
		size: int = -1,
		dimensions: tuple = None
	):
		if not isinstance(path, str):
			raise TypeError("path must be a string")
		self.path = path
		self.type = self._get_type()
		self.name = name or self._get_name()
		self.description = description
		if size and size > 0:
			self.size = get_display_size(size)
		else:
			self.size = self._get_size()
		self.dimensions = dimensions or self._get_dimensions()

	def _get_type(self):
		if os.path.exists(self.path):
			return ImageFileTypes.IMAGE_LOCAL if self._is_image_path(self.path) else ImageFileTypes.DOCUMENT_LOCAL
		if re.match(URL_PATTERN, self.path):
			return ImageFileTypes.IMAGE_URL if self._is_image_path(self.path) else ImageFileTypes.DOCUMENT_URL
		return ImageFileTypes.UNKNOWN

	def _is_image_path(self, value: str) -> bool:
		parsed = urllib.parse.urlparse(value)
		path = parsed.path if parsed.scheme else value
		mime, _ = mimetypes.guess_type(path)
		return bool(mime and mime.startswith("image/"))

	def _get_name(self):
		if self.type in (ImageFileTypes.IMAGE_LOCAL, ImageFileTypes.DOCUMENT_LOCAL):
			return os.path.basename(self.path)
		if self.type in (ImageFileTypes.IMAGE_URL, ImageFileTypes.DOCUMENT_URL):
			return self.path.split("/")[-1]
		return "N/A"

	def _get_size(self):
		if self.type == ImageFileTypes.IMAGE_LOCAL:
			return get_display_size(os.path.getsize(self.path))
		return "N/A"

	def _get_dimensions(self):
		if self.type == ImageFileTypes.IMAGE_LOCAL:
			try:
				return get_image_dimensions(self.path)
			except Exception:
				return None
		return None

	def __str__(self):
		return f"{self.name} ({self.path}, {self.size}, {self.dimensions}, {self.description})"
