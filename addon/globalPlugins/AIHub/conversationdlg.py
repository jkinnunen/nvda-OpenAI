# coding: UTF-8
"""Conversation management dialog: list, open, rename, delete saved conversations."""
import datetime
import os

import addonHandler
import config
import gui
import wx
import ui

from . import conversations
from .conversations import ConversationFormat, normalize_conversation_format
from .tool_lyria_dialog import Lyria3ProToolDialog
from .tool_mistral_ocr_dialog import MistralOCRToolDialog
from .tool_mistral_transcription_dialog import MistralSpeechToTextToolDialog
from .tool_openai_transcription_dialog import OpenAITranscriptionToolDialog
from .tool_openai_tts_dialog import OpenAITTSToolDialog
from .toolsmenu import open_tool_dialog_by_class
from .tool_voxtral_tts_dialog import VoxtralTTSToolDialog

addonHandler.initTranslation()


def format_date(ts: int) -> str:
	if not ts:
		return ""
	try:
		dt = datetime.datetime.fromtimestamp(ts)
		return dt.strftime("%Y-%m-%d %H:%M")
	except Exception:
		return str(ts)


def format_size(size: int | None) -> str:
	if not isinstance(size, int) or size < 0:
		return _("unknown")
	units = ["B", "KB", "MB", "GB"]
	val = float(size)
	for unit in units:
		if val < 1024.0 or unit == units[-1]:
			if unit == "B":
				return f"{int(val)} {unit}"
			return f"{val:.1f} {unit}"
		val /= 1024.0
	return f"{size} B"


def _open_tool_dialog_from_conversation(plugin, dialog_cls, conversation_data):
	open_tool_dialog_by_class(
		None,
		dialog_cls,
		conversationData=conversation_data,
		plugin=plugin,
	)


class ConversationsManagerDlg(wx.Dialog):
	# Translators: Title of the conversation management dialog
	title = _("Conversation history")

	def __init__(self, parent, plugin):
		super().__init__(parent, title=self.title)
		self._plugin = plugin
		self._entries = []
		self._list = wx.ListCtrl(
			self,
			style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES,
			size=(600, 320)
		)
		self._list.InsertColumn(0, _("Name"), width=300)
		self._list.InsertColumn(1, _("Format"), width=180)
		self._list.InsertColumn(2, _("Last modified"), width=140)
		self._list.InsertColumn(3, _("Messages"), width=80)
		self._list.InsertColumn(4, _("Tokens"), width=90)
		self._list.InsertColumn(5, _("Main model"), width=180)
		self._list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onOpen)
		self._list.Bind(wx.EVT_LIST_KEY_DOWN, self.onListKeyDown)
		self._list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelectionChanged)
		main = wx.BoxSizer(wx.VERTICAL)
		main.Add(
			wx.StaticText(self, label=_("Saved conversations:")),
			0, wx.ALL, 5
		)
		main.Add(self._list, 1, wx.EXPAND | wx.ALL, 5)
		self._propertiesText = wx.TextCtrl(
			self,
			style=wx.TE_MULTILINE | wx.TE_READONLY,
			size=(600, 120)
		)
		main.Add(
			wx.StaticText(self, label=_("Selected conversation properties:")),
			0, wx.LEFT | wx.RIGHT | wx.TOP, 5
		)
		main.Add(self._propertiesText, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
		btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
		open_btn = wx.Button(self, id=wx.ID_OPEN, label=_("&Open"))
		open_btn.Bind(wx.EVT_BUTTON, self.onOpen)
		rename_btn = wx.Button(self, label=_("&Rename") + " (F2)")
		rename_btn.Bind(wx.EVT_BUTTON, self.onRename)
		props_btn = wx.Button(self, label=_("&Properties") + " (Alt+Enter)")
		props_btn.Bind(wx.EVT_BUTTON, self.onProperties)
		delete_btn = wx.Button(self, id=wx.ID_DELETE, label=_("&Delete") + " (Del)")
		delete_btn.Bind(wx.EVT_BUTTON, self.onDelete)
		delete_all_btn = wx.Button(self, label=_("Delete a&ll"))
		delete_all_btn.Bind(wx.EVT_BUTTON, self.onDeleteAll)
		new_btn = wx.Button(self, id=wx.ID_NEW, label=_("&New conversation"))
		new_btn.Bind(wx.EVT_BUTTON, self.onNew)
		close_btn = wx.Button(self, id=wx.ID_CLOSE, label=_("Clos&e"))
		close_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CLOSE))
		for b in (open_btn, rename_btn, props_btn, delete_btn, delete_all_btn, new_btn, close_btn):
			btn_sizer.Add(b, 0, wx.ALL, 5)
		main.Add(btn_sizer, 0, wx.ALL, 5)
		self.SetSizerAndFit(main)
		self.CentreOnParent(wx.BOTH)
		self.SetEscapeId(wx.ID_CLOSE)
		self.refresh_list()

	def refresh_list(self):
		self._entries = conversations.list_conversations()
		self._list.DeleteAllItems()
		for e in self._entries:
			props = conversations.get_conversation_properties(e.get("id")) or {}
			e["properties"] = props
			name = e.get("name", _("Untitled conversation"))
			date_str = format_date(e.get("updated", 0))
			model_counts = props.get("model_counts", {}) if isinstance(props, dict) else {}
			main_model = _("unknown")
			if model_counts:
				main_model = max(model_counts.items(), key=lambda item: item[1])[0]
			conv_format = e.get("format", "generic")
			self._list.Append([
				name,
				str(conv_format),
				date_str,
				str(props.get("messages", 0)),
				str(props.get("total_tokens", 0)),
				main_model,
			])
		if self._entries:
			self._list.Select(0)
			self._list.SetItemState(0, wx.LIST_STATE_FOCUSED, wx.LIST_STATE_FOCUSED)
			self._list.SetFocus()
			self._updatePropertiesPanel(self._entries[0])
		else:
			self._propertiesText.SetValue("")

	def _buildPropertiesLines(self, entry, props):
		props = props or {}
		lines = [
			_("Name: %s") % entry.get("name", _("Untitled conversation")),
			_("Format: %s") % entry.get("format", "generic"),
			_("Messages: %d") % int(props.get("messages", 0)),
			_("System prompt length: %d characters") % int(props.get("system_len", 0)),
			_("Draft prompt length: %d characters") % int(props.get("draft_len", 0)),
			_("Total input tokens: %d") % int(props.get("total_input", 0)),
			_("Total output tokens: %d") % int(props.get("total_output", 0)),
			_("Total tokens: %d") % int(props.get("total_tokens", 0)),
		]
		if int(props.get("total_reasoning", 0)):
			lines.append(_("Total reasoning tokens: %d") % int(props.get("total_reasoning", 0)))
		if int(props.get("total_cached", 0)):
			lines.append(_("Total cached input tokens: %d") % int(props.get("total_cached", 0)))
		if int(props.get("total_cache_write", 0)):
			lines.append(_("Total cache write tokens: %d") % int(props.get("total_cache_write", 0)))
		if int(props.get("total_input_audio", 0)):
			lines.append(_("Total input audio tokens: %d") % int(props.get("total_input_audio", 0)))
		if int(props.get("total_output_audio", 0)):
			lines.append(_("Total output audio tokens: %d") % int(props.get("total_output_audio", 0)))
		if props.get("has_cost"):
			lines.append(_("Total cost: $%.6f") % float(props.get("total_cost", 0.0)))
		model_counts = props.get("model_counts", {})
		if model_counts:
			lines.extend(["", _("Models used:")])
			for model_name, count in sorted(model_counts.items(), key=lambda x: x[1], reverse=True):
				lines.append(f"- {model_name}: {count}")
		files = props.get("files", [])
		if isinstance(files, list) and files:
			lines.extend(["", _("Files (input/output):")])
			for item in files:
				if not isinstance(item, dict):
					continue
				role = item.get("role", "input")
				kind = item.get("kind", "file")
				path = item.get("path", "")
				name = os.path.basename(path) if isinstance(path, str) and path else _("(no path)")
				size = format_size(item.get("size"))
				lines.append(_("- [{role}] {name} ({kind}, {size})").format(**{
					"role": role,
					"name": name,
					"kind": kind,
					"size": size,
				}))
		return lines

	def _updatePropertiesPanel(self, entry):
		if not entry:
			self._propertiesText.SetValue("")
			return
		props = entry.get("properties")
		if not isinstance(props, dict):
			props = conversations.get_conversation_properties(entry.get("id")) or {}
			entry["properties"] = props
		self._propertiesText.SetValue("\n".join(self._buildPropertiesLines(entry, props)))

	def onSelectionChanged(self, evt):
		idx = evt.GetIndex()
		if 0 <= idx < len(self._entries):
			self._updatePropertiesPanel(self._entries[idx])
		evt.Skip()

	def _get_selected_entries(self):
		selected = []
		idx = self._list.GetFirstSelected()
		while idx != -1:
			if 0 <= idx < len(self._entries):
				selected.append(self._entries[idx])
			idx = self._list.GetNextSelected(idx)
		return selected

	def onListKeyDown(self, evt):
		key = evt.GetKeyCode()
		if key == wx.WXK_DELETE:
			self.onDelete(evt)
		elif key == wx.WXK_RETURN and evt.GetModifiers() == wx.MOD_ALT:
			self.onProperties(evt)
		elif key == wx.WXK_NUMPAD_ENTER or key == wx.WXK_RETURN:
			self.onOpen(evt)
		elif key == wx.WXK_F2:
			self.onRename(evt)
		else:
			evt.Skip()

	def onProperties(self, evt):
		selected = self._get_selected_entries()
		if not selected:
			wx.Bell()
			return
		if len(selected) > 1:
			ui.message(_("Select only one conversation to show properties."))
			return
		entry = selected[0]
		props = entry.get("properties")
		if not isinstance(props, dict):
			props = conversations.get_conversation_properties(entry.get("id")) or {}
			entry["properties"] = props
		lines = [_("Conversation properties"), ""] + self._buildPropertiesLines(entry, props)
		ui.browseableMessage("\n".join(lines), _("Conversation properties"), False)

	def onOpen(self, evt):
		selected = self._get_selected_entries()
		if not selected:
			return
		if len(selected) > 1:
			ui.message(_("Select only one conversation to open."))
			return
		entry = selected[0]
		conv_id = entry.get("id")
		data = conversations.load_conversation(conv_id)
		if not data:
			gui.messageBox(
				_("Unable to load conversation."),
				self.title,
				wx.OK | wx.ICON_ERROR
			)
			return
		plugin = self._plugin
		client = plugin.getClient()
		conf = config.conf.get("AIHub", {})
		conv_format = normalize_conversation_format(data.get("format", ConversationFormat.GENERIC.value))
		self.EndModal(wx.ID_OK)
		self.Destroy()
		if not client or not conf:
			return
		tool_dialog_map = {
			ConversationFormat.TOOL_MISTRAL_OCR: MistralOCRToolDialog,
			ConversationFormat.TOOL_MISTRAL_SPEECH_TO_TEXT: MistralSpeechToTextToolDialog,
			ConversationFormat.TOOL_MISTRAL_VOXTRAL_TTS: VoxtralTTSToolDialog,
			ConversationFormat.TOOL_GOOGLE_LYRIA_PRO: Lyria3ProToolDialog,
			ConversationFormat.TOOL_OPENAI_TTS: OpenAITTSToolDialog,
			ConversationFormat.TOOL_OPENAI_TRANSCRIPTION: OpenAITranscriptionToolDialog,
		}
		if conv_format in tool_dialog_map:
			dialog_cls = tool_dialog_map[conv_format]
			wx.CallAfter(_open_tool_dialog_from_conversation, plugin, dialog_cls, data)
			return
		wx.CallAfter(plugin._openMainDialog, None, data, False)

	def onRename(self, evt):
		selected = self._get_selected_entries()
		if not selected:
			wx.Bell()
			return
		if len(selected) > 1:
			ui.message(_("Select only one conversation to rename."))
			return
		entry = selected[0]
		current_name = entry.get("name", "")
		dlg = wx.TextEntryDialog(
			self,
			_("Enter new name for this conversation:"),
			_("Rename conversation"),
			value=current_name
		)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return
		new_name = dlg.GetValue().strip()
		dlg.Destroy()
		if not new_name:
			return
		if conversations.rename_conversation(entry["id"], new_name):
			self.refresh_list()

	def onDelete(self, evt):
		selected = self._get_selected_entries()
		if not selected:
			wx.Bell()
			return
		count = len(selected)
		confirm_msg = (
			_("Delete this conversation? This cannot be undone.")
			if count == 1
			else _("Delete %d conversations? This cannot be undone.") % count
		)
		res = gui.messageBox(
			confirm_msg,
			_("Delete conversation"),
			wx.YES_NO | wx.ICON_QUESTION
		)
		if res != wx.YES:
			return
		deleted = 0
		for entry in selected:
			if conversations.delete_conversation(entry["id"]):
				deleted += 1
		if deleted:
			self.refresh_list()
			ui.message(
				_("Deleted %d conversation.") % deleted
				if deleted == 1
				else _("Deleted %d conversations.") % deleted
			)

	def onDeleteAll(self, evt):
		if not self._entries:
			wx.Bell()
			return
		total = len(self._entries)
		res = gui.messageBox(
			_("Delete all %d conversations? This cannot be undone.") % total,
			_("Delete all conversations"),
			wx.YES_NO | wx.ICON_WARNING
		)
		if res != wx.YES:
			return
		deleted = 0
		for entry in list(self._entries):
			if conversations.delete_conversation(entry["id"]):
				deleted += 1
		self.refresh_list()
		ui.message(
			_("Deleted %d conversation.") % deleted
			if deleted == 1
			else _("Deleted %d conversations.") % deleted
		)

	def onNew(self, evt):
		plugin = self._plugin
		client = plugin.getClient()
		conf = config.conf.get("AIHub", {})
		self.EndModal(wx.ID_OK)
		self.Destroy()
		if not client or not conf:
			return
		wx.CallAfter(plugin._openMainDialog, None, None, False)


def show_conversations_manager(plugin):
	"""Show the conversation management dialog."""
	from . import __init__ as init_mod
	client = plugin.getClient()
	conf = config.conf.get("AIHub", {})
	if not client or not conf:
		ui.message(getattr(init_mod, "NO_AUTHENTICATION_KEY_PROVIDED_MSG", _("No API key provided")))
		return
	gui.mainFrame.prePopup()
	try:
		dlg = ConversationsManagerDlg(gui.mainFrame, plugin)
		dlg.ShowModal()
		dlg.Destroy()
	finally:
		gui.mainFrame.postPopup()
