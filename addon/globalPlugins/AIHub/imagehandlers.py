# coding: UTF-8
"""Image list handlers for AIHubDlg."""
import mimetypes
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import wx

import addonHandler
import gui
from logHandler import log

from .imagehelper import get_image_dimensions, resize_image
from .imagedlg import ImageFile, ImageFileTypes, URL_PATTERN
from .consts import TEMP_DIR
from .mediastore import persist_local_file

addonHandler.initTranslation()

IMAGE_EXTENSIONS = {
	".png", ".jpeg", ".jpg", ".gif", ".webp"
}
OPENAI_DOCUMENT_EXTENSIONS = {
	".pdf", ".txt", ".md", ".json", ".html", ".xml", ".csv", ".tsv",
	".doc", ".docx", ".rtf", ".odt", ".ppt", ".pptx", ".xls", ".xlsx",
}

# Every provider explicitly declares supported attachment file extensions.
# Kept conservative to align with officially documented formats.
PROVIDER_SUPPORTED_FILES = {
	"OpenAI": {"images": IMAGE_EXTENSIONS, "documents": OPENAI_DOCUMENT_EXTENSIONS},
	"CustomOpenAI": {"images": IMAGE_EXTENSIONS, "documents": OPENAI_DOCUMENT_EXTENSIONS},
	"DeepSeek": {"images": set(), "documents": set()},
	"Ollama": {"images": IMAGE_EXTENSIONS, "documents": set()},
	"MistralAI": {"images": IMAGE_EXTENSIONS, "documents": {".pdf"}},
	"OpenRouter": {"images": IMAGE_EXTENSIONS, "documents": {".pdf"}},
	"Anthropic": {"images": {".jpeg", ".jpg", ".png", ".gif", ".webp"}, "documents": {".pdf"}},
	"xAI": {"images": IMAGE_EXTENSIONS, "documents": {".pdf"}},
	"Google": {"images": IMAGE_EXTENSIONS, "documents": {".pdf"}},
}

PROVIDER_SUPPORTED_URL_MIME = {
	"OpenAI": {
		"images": {"image/png", "image/jpeg", "image/gif", "image/webp"},
		"documents": {
			"application/pdf",
			"text/plain",
			"text/markdown",
			"application/json",
			"text/html",
			"application/xml",
			"text/xml",
			"text/csv",
			"text/tab-separated-values",
			"application/msword",
			"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
			"application/rtf",
			"application/vnd.oasis.opendocument.text",
			"application/vnd.ms-powerpoint",
			"application/vnd.openxmlformats-officedocument.presentationml.presentation",
			"application/vnd.ms-excel",
			"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
		},
	},
	"CustomOpenAI": {
		"images": {"image/png", "image/jpeg", "image/gif", "image/webp"},
		"documents": {
			"application/pdf",
			"text/plain",
			"text/markdown",
			"application/json",
			"text/html",
			"application/xml",
			"text/xml",
			"text/csv",
			"text/tab-separated-values",
			"application/msword",
			"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
			"application/rtf",
			"application/vnd.oasis.opendocument.text",
			"application/vnd.ms-powerpoint",
			"application/vnd.openxmlformats-officedocument.presentationml.presentation",
			"application/vnd.ms-excel",
			"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
		},
	},
	"DeepSeek": {"images": set(), "documents": set()},
	"Ollama": {"images": {"image/png", "image/jpeg", "image/gif", "image/webp"}, "documents": set()},
	"MistralAI": {"images": {"image/png", "image/jpeg", "image/gif", "image/webp"}, "documents": {"application/pdf"}},
	"OpenRouter": {"images": {"image/png", "image/jpeg", "image/gif", "image/webp"}, "documents": {"application/pdf"}},
	"Anthropic": {"images": {"image/png", "image/jpeg", "image/gif", "image/webp"}, "documents": {"application/pdf"}},
	"xAI": {"images": {"image/png", "image/jpeg", "image/gif", "image/webp"}, "documents": {"application/pdf"}},
	"Google": {"images": {"image/png", "image/jpeg", "image/gif", "image/webp"}, "documents": {"application/pdf"}},
}


class ImageHandlersMixin:
	def _get_provider_file_support(self, provider: str):
		return PROVIDER_SUPPORTED_FILES.get(provider) or {"images": IMAGE_EXTENSIONS, "documents": {".pdf"}}

	def _get_file_extension(self, imageFile: ImageFile) -> str:
		path = (getattr(imageFile, "path", "") or "").strip()
		if not path:
			return ""
		if re.match(URL_PATTERN, path):
			parsed = urllib.parse.urlparse(path)
			path = parsed.path or ""
		return os.path.splitext(path)[1].lower()

	def _get_attachment_mime(self, imageFile: ImageFile) -> str:
		desc = getattr(imageFile, "description", "") or ""
		if isinstance(desc, str) and "/" in desc:
			mime = desc.split(",", 1)[0].strip().lower()
			if ";" in mime:
				mime = mime.split(";", 1)[0].strip()
			if "/" in mime:
				return mime
		path = (getattr(imageFile, "path", "") or "").strip()
		if not path:
			return ""
		guess_target = urllib.parse.urlparse(path).path if re.match(URL_PATTERN, path) else path
		mime, _ = mimetypes.guess_type(guess_target)
		return (mime or "").lower()

	def _is_url_attachment_supported_by_mime(self, provider: str, imageFile: ImageFile) -> bool:
		mime = self._get_attachment_mime(imageFile)
		if not mime:
			return False
		mime_support = PROVIDER_SUPPORTED_URL_MIME.get(provider) or {"images": set(), "documents": {"application/pdf"}}
		if imageFile.type == ImageFileTypes.IMAGE_URL:
			return mime in mime_support["images"]
		if imageFile.type == ImageFileTypes.DOCUMENT_URL:
			return mime in mime_support["documents"]
		return False

	def getUnsupportedAttachments(self, provider: str = None, pathList=None):
		pathList = self.pathList if pathList is None else pathList
		if not pathList:
			return []
		if provider is None:
			model = self.getCurrentModel() if hasattr(self, "getCurrentModel") else None
			provider = getattr(model, "provider", "") if model else ""
		support = self._get_provider_file_support(provider)
		unsupported = []
		for imageFile in pathList:
			ext = self._get_file_extension(imageFile)
			if imageFile.type in (ImageFileTypes.IMAGE_LOCAL, ImageFileTypes.IMAGE_URL):
				if imageFile.type == ImageFileTypes.IMAGE_URL and self._is_url_attachment_supported_by_mime(provider, imageFile):
					continue
				if ext not in support["images"]:
					unsupported.append((imageFile.path, ext or _("unknown"), _("image")))
			elif imageFile.type in (ImageFileTypes.DOCUMENT_LOCAL, ImageFileTypes.DOCUMENT_URL):
				if imageFile.type == ImageFileTypes.DOCUMENT_URL and self._is_url_attachment_supported_by_mime(provider, imageFile):
					continue
				if ext not in support["documents"]:
					unsupported.append((imageFile.path, ext or _("unknown"), _("document")))
		return unsupported

	def validateAttachmentsForProvider(self, provider: str = None, pathList=None):
		unsupported = self.getUnsupportedAttachments(provider=provider, pathList=pathList)
		if not unsupported:
			return True, ""
		provider_name = provider or _("selected provider")
		details = "\n".join(
			f"- {os.path.basename(path) or path} ({kind}, {ext})"
			for path, ext, kind in unsupported
		)
		msg = _(
			"The following attachments are not supported by {provider} and cannot be sent:\n{details}"
		).format(**{
			"provider": provider_name,
			"details": details,
		})
		return False, msg

	def addImageToList(self, path, removeAfter=False):
		if not path:
			return
		if isinstance(path, ImageFile):
			path.path = persist_local_file(path.path, "images", prefix="image", fallback_ext=".png")
			self.pathList.append(path)
		elif isinstance(path, str):
			stored = persist_local_file(path, "images", prefix="image", fallback_ext=".png")
			self.pathList.append(ImageFile(stored))
		elif isinstance(path, tuple) and len(path) == 2:
			location, name = path
			stored = persist_local_file(location, "images", prefix="image", fallback_ext=".png")
			self.pathList.append(ImageFile(stored, name=name))
			if removeAfter and location != stored:
				self._fileToRemoveAfter.append(location)
		else:
			raise ValueError(f"Invalid path: {path}")

	def getDefaultImageDescriptionsPrompt(self):
		if self.conf["images"]["useCustomPrompt"]:
			return self.conf["images"]["customPromptText"]
		return _("Describe the images in as much detail as possible.")

	def onImageDescription(self, evt):
		menu = wx.Menu()
		item_id = wx.NewIdRef()
		menu.Append(item_id, _("From f&ile path...") + " (Ctrl+I)")
		self.Bind(wx.EVT_MENU, self.onImageDescriptionFromFilePath, id=item_id)
		item_id = wx.NewIdRef()
		menu.Append(item_id, _("From &URL...") + " (Ctrl+U)")
		self.Bind(wx.EVT_MENU, self.onImageDescriptionFromURL, id=item_id)
		item_id = wx.NewIdRef()
		menu.Append(item_id, _("From &screenshot") + " (Ctrl+E)")
		self.Bind(wx.EVT_MENU, self.onImageDescriptionFromScreenshot, id=item_id)
		self.PopupMenu(menu)
		menu.Destroy()

	def onImageListKeyDown(self, evt):
		key_code = evt.GetKeyCode()
		if key_code == wx.WXK_DELETE:
			self.onRemoveSelectedImages(evt)
		elif key_code == ord('A') and evt.ControlDown():
			self.onImageListSelectAll(evt)
		evt.Skip()

	def onImageListContextMenu(self, evt):
		menu = wx.Menu()
		if self.pathList:
			if self.imagesListCtrl.GetItemCount() > 0 and self.imagesListCtrl.GetSelectedItemCount() > 0:
				item_id = wx.NewIdRef()
				menu.Append(item_id, _("&Remove selected images") + " (Del)")
				self.Bind(wx.EVT_MENU, self.onRemoveSelectedImages, id=item_id)
			item_id = wx.NewIdRef()
			menu.Append(item_id, _("Remove &all images"))
			self.Bind(wx.EVT_MENU, self.onRemoveAllImages, id=item_id)
			menu.AppendSeparator()
		item_id = wx.NewIdRef()
		menu.Append(item_id, _("Add from f&ile path...") + " (Ctrl+I)")
		self.Bind(wx.EVT_MENU, self.onImageDescriptionFromFilePath, id=item_id)
		item_id = wx.NewIdRef()
		menu.Append(item_id, _("Add from &URL...") + " (Ctrl+U)")
		self.Bind(wx.EVT_MENU, self.onImageDescriptionFromURL, id=item_id)
		self.PopupMenu(menu)
		menu.Destroy()

	def onImageListSelectAll(self, evt):
		for i in range(self.imagesListCtrl.GetItemCount()):
			self.imagesListCtrl.Select(i)

	def onRemoveSelectedImages(self, evt):
		if not self.pathList:
			return
		focused_item = self.imagesListCtrl.GetFocusedItem()
		items_to_remove = []
		selectedItem = self.imagesListCtrl.GetFirstSelected()
		while selectedItem != wx.NOT_FOUND:
			items_to_remove.append(selectedItem)
			selectedItem = self.imagesListCtrl.GetNextSelected(selectedItem)
		if not items_to_remove:
			return
		self.pathList = [
			path for i, path in enumerate(self.pathList)
			if i not in items_to_remove
		]
		self.updateImageList()
		if focused_item == wx.NOT_FOUND:
			return
		if focused_item > self.imagesListCtrl.GetItemCount() - 1:
			focused_item -= 1
		self.imagesListCtrl.Focus(focused_item)
		self.imagesListCtrl.Select(focused_item)

	def onRemoveAllImages(self, evt):
		self.pathList.clear()
		self.updateImageList()

	def imageExists(self, path, pathList=None):
		if not pathList:
			pathList = self.pathList
		for imageFile in pathList:
			if imageFile.path.lower() == path.lower():
				return True
		block = self.firstBlock
		while block is not None:
			if block.pathList:
				for imageFile in block.pathList:
					if imageFile.path.lower() == path.lower():
						return True
			block = block.next
		return False

	def updateImageList(self, focusPrompt=True):
		self.imagesListCtrl.DeleteAllItems()
		if not self.pathList:
			self.imagesLabel.Hide()
			self.imagesListCtrl.Hide()
			self.Layout()
			if focusPrompt:
				self.promptTextCtrl.SetFocus()
			return
		for path in self.pathList:
			self.imagesListCtrl.Append([
				path.name,
				path.path,
				path.size,
				f"{path.dimensions[0]}x{path.dimensions[1]}" if isinstance(path.dimensions, tuple) else "N/A",
				path.description or "N/A"
			])
		self.imagesListCtrl.SetItemState(
			0,
			wx.LIST_STATE_FOCUSED,
			wx.LIST_STATE_FOCUSED
		)
		self.imagesLabel.Show()
		self.imagesListCtrl.Show()
		self.Layout()

	def ensureModelVisionSelected(self):
		model = self.getCurrentModel()
		if model and model.vision:
			return
		vision_id = self.conf.get("modelVision")
		if vision_id and self._selectModelById(vision_id):
			return
		vision_models = [m for m in self._models if m.vision]
		if vision_models:
			self._selectModelById(vision_models[0].id)

	def focusLastImage(self):
		index = self.imagesListCtrl.GetItemCount() - 1
		self.imagesListCtrl.SetItemState(
			index,
			wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
			wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
		)
		self.imagesListCtrl.EnsureVisible(index)

	def onImageDescriptionFromFilePath(self, evt):
		if not self.pathList:
			self.pathList = []
		dlg = wx.FileDialog(
			None,
			message=_("Select files"),
			defaultFile="",
			wildcard=_("Supported files") + " (*.png;*.jpeg;*.jpg;*.gif;*.webp;*.bmp;*.pdf;*.txt;*.md;*.json;*.html;*.xml;*.csv;*.tsv;*.doc;*.docx;*.rtf;*.odt;*.ppt;*.pptx;*.xls;*.xlsx)|*.png;*.jpeg;*.jpg;*.gif;*.webp;*.bmp;*.pdf;*.txt;*.md;*.json;*.html;*.xml;*.csv;*.tsv;*.doc;*.docx;*.rtf;*.odt;*.ppt;*.pptx;*.xls;*.xlsx",
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE
		)
		if dlg.ShowModal() != wx.ID_OK:
			return
		paths = dlg.GetPaths()
		if not paths:
			return
		added_image = False
		rejected = []
		model = self.getCurrentModel() if hasattr(self, "getCurrentModel") else None
		provider = getattr(model, "provider", "") if model else ""
		for path in paths:
			if not self.imageExists(path):
				image_file = ImageFile(path)
				unsupported = self.getUnsupportedAttachments(provider=provider, pathList=[image_file])
				if unsupported:
					rejected.append(path)
					continue
				self.pathList.append(image_file)
				if image_file.type in (ImageFileTypes.IMAGE_LOCAL, ImageFileTypes.IMAGE_URL):
					added_image = True
			else:
				gui.messageBox(
					_("The following file has already been added and will be ignored:\n%s") % path,
					"OpenAI",
					wx.OK | wx.ICON_ERROR
				)
		if rejected:
			gui.messageBox(
				_("Some files are not supported by the selected provider and were ignored:\n%s") % "\n".join(rejected),
				_("Unsupported files"),
				wx.OK | wx.ICON_WARNING
			)
		if added_image:
			self.ensureModelVisionSelected()
		if not self.promptTextCtrl.GetValue().strip():
			self.promptTextCtrl.SetValue(self.getDefaultImageDescriptionsPrompt())
		self.updateImageList()
		self.focusLastImage()

	def onImageDescriptionFromURL(self, evt):
		dlg = wx.TextEntryDialog(
			None,
			message=_("Enter file URL"),
			caption="OpenAI",
			style=wx.OK | wx.CANCEL
		)
		if dlg.ShowModal() != wx.ID_OK:
			return
		url = dlg.GetValue().strip()
		if not url:
			return
		if not re.match(URL_PATTERN, url):
			gui.messageBox(
				_("Invalid URL, bad format."),
				"OpenAI",
				wx.OK | wx.ICON_ERROR
			)
			return
		try:
			with urllib.request.urlopen(url, timeout=15) as r:
				if not self.pathList:
					self.pathList = []
				content_type = (r.headers.get_content_type() or "").lower().strip()
				if not content_type:
					content_type = "application/octet-stream"
				description = content_type
				size = r.headers.get("Content-Length")
				if size and size.isdigit():
					size = int(size)
				is_image = content_type.startswith("image/")
				image_file = ImageFile(
					url,
					description=description,
					size=size or -1,
					dimensions=None
				)
				if image_file.type == ImageFileTypes.UNKNOWN:
					image_file.type = ImageFileTypes.IMAGE_URL if is_image else ImageFileTypes.DOCUMENT_URL
				model = self.getCurrentModel() if hasattr(self, "getCurrentModel") else None
				provider = getattr(model, "provider", "") if model else ""
				unsupported = self.getUnsupportedAttachments(provider=provider, pathList=[image_file])
				if unsupported:
					gui.messageBox(
						_("This URL file type is not supported by the selected provider."),
						_("Unsupported file type"),
						wx.OK | wx.ICON_ERROR
					)
					return
				if is_image:
					try:
						image_file.dimensions = get_image_dimensions(r)
					except Exception as err:
						log.error(f"get_image_dimensions: {err}", exc_info=True)
						gui.messageBox(
							_("Failed to get image dimensions. %s") % err,
							"OpenAI",
							wx.OK | wx.ICON_ERROR
						)
						return
				self.pathList.append(image_file)
				if is_image:
					self.ensureModelVisionSelected()
					if not self.promptTextCtrl.GetValue().strip():
						self.promptTextCtrl.SetValue(self.getDefaultImageDescriptionsPrompt())
				self.updateImageList()
				self.focusLastImage()
				return
		except urllib.error.HTTPError as err:
			gui.messageBox(
				_("HTTP error %s.") % err,
				"OpenAI",
				wx.OK | wx.ICON_ERROR
			)
			return

	def onImageDescriptionFromScreenshot(self, evt):
		from . import maindialog
		if maindialog.addToSession and maindialog.addToSession is self:
			maindialog.addToSession = None
			self.message(_("Screenshot reception disabled"))
			return
		maindialog.addToSession = self
		self.message(_("Screenshot reception enabled"))
