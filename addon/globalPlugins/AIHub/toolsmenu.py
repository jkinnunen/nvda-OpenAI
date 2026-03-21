# coding: UTF-8
"""Tools menu and registry for single-tool dialogs."""

import addonHandler
import wx
from enum import StrEnum, auto

from . import apikeymanager
from .tool_lyria_dialog import Lyria3ProToolDialog
from .tool_mistral_ocr_dialog import MistralOCRToolDialog
from .tool_mistral_transcription_dialog import MistralSpeechToTextToolDialog
from .tool_ollama_models_dialog import OllamaModelManagerToolDialog
from .tool_openai_transcription_dialog import OpenAITranscriptionToolDialog
from .tool_openai_tts_dialog import OpenAITTSToolDialog
from .tool_voxtral_tts_dialog import VoxtralTTSToolDialog

addonHandler.initTranslation()


class ToolId(StrEnum):
	VOXTRAL_TTS = auto()
	MISTRAL_OCR = auto()
	MISTRAL_SPEECH_TO_TEXT = auto()
	LYRIA_3_PRO = auto()
	OPENAI_TTS = auto()
	OPENAI_TRANSCRIPTION = auto()
	OLLAMA_MODEL_MANAGER = auto()


TOOLS_REGISTRY = (
	{
		"id": ToolId.VOXTRAL_TTS,
		"label": _("Voxtral TTS..."),
		"provider": "Mistral",
		"manager_provider": "MistralAI",
		"dialog_cls": VoxtralTTSToolDialog,
	},
	{
		"id": ToolId.MISTRAL_OCR,
		"label": _("OCR..."),
		"provider": "Mistral",
		"manager_provider": "MistralAI",
		"dialog_cls": MistralOCRToolDialog,
	},
	{
		"id": ToolId.MISTRAL_SPEECH_TO_TEXT,
		"label": _("Speech to Text..."),
		"provider": "Mistral",
		"manager_provider": "MistralAI",
		"dialog_cls": MistralSpeechToTextToolDialog,
	},
	{
		"id": ToolId.LYRIA_3_PRO,
		"label": _("Lyria 3 Pro..."),
		"provider": "Google",
		"dialog_cls": Lyria3ProToolDialog,
	},
	{
		"id": ToolId.OPENAI_TTS,
		"label": _("TTS..."),
		"provider": "OpenAI",
		"dialog_cls": OpenAITTSToolDialog,
	},
	{
		"id": ToolId.OPENAI_TRANSCRIPTION,
		"label": _("Transcription / Translation..."),
		"provider": "OpenAI",
		"dialog_cls": OpenAITranscriptionToolDialog,
	},
	{
		"id": ToolId.OLLAMA_MODEL_MANAGER,
		"label": _("Model manager..."),
		"provider": "Ollama",
		"dialog_cls": OllamaModelManagerToolDialog,
	},
)

_OPEN_TOOL_DIALOGS = []


def _resolve_plugin(parent, plugin=None):
	if plugin is not None:
		return plugin
	if parent is not None:
		return getattr(parent, "_plugin", None)
	return None


def _populate_tools_provider_submenus(menu, parent, plugin):
	provider_order = ("OpenAI", "Mistral", "Google", "Ollama")
	for provider_name in provider_order:
		provider_tools = [td for td in TOOLS_REGISTRY if td.get("provider") == provider_name]
		if not provider_tools:
			continue
		submenu = wx.Menu()
		for tool_def in provider_tools:
			item = submenu.Append(wx.ID_ANY, tool_def["label"])
			submenu.Bind(
				wx.EVT_MENU,
				lambda evt, td=tool_def: open_tool_dialog(parent, td, plugin=plugin),
				id=item.GetId(),
			)
		menu.AppendSubMenu(submenu, provider_name)


def open_tool_dialog(parent, tool_def, conversationData=None, plugin=None):
	provider = tool_def.get("provider")
	manager_provider = tool_def.get("manager_provider") or provider
	if manager_provider:
		try:
			manager = apikeymanager.get(manager_provider)
		except Exception:
			manager = None
		if manager and not manager.isReady():
			provider_label = provider or manager_provider
			wx.MessageBox(
				_("No account configured for %s. Please add an account for this provider in AI Hub settings.") % provider_label,
				"OpenAI",
				wx.OK | wx.ICON_ERROR,
			)
			return
	dialog_cls = tool_def["dialog_cls"]
	plugin = _resolve_plugin(parent, plugin)
	dlg = dialog_cls(
		None,
		conversationData=conversationData,
		parentDialog=parent,
		plugin=plugin,
	)
	_OPEN_TOOL_DIALOGS.append(dlg)

	def _on_close(evt, dialog=dlg):
		try:
			if dialog in _OPEN_TOOL_DIALOGS:
				_OPEN_TOOL_DIALOGS.remove(dialog)
		except Exception:
			pass
		evt.Skip()

	dlg.Bind(wx.EVT_CLOSE, _on_close)
	dlg.Show()
	dlg.Raise()


def open_tool_dialog_by_class(parent, dialog_cls, conversationData=None, plugin=None):
	tool_def = {"dialog_cls": dialog_cls}
	open_tool_dialog(parent, tool_def, conversationData=conversationData, plugin=plugin)


def append_tools_submenu(menu, parent=None, plugin=None, label=None):
	"""Append a Tools submenu to an existing menu."""
	tools_menu = wx.Menu()
	plugin = _resolve_plugin(parent, plugin)
	_populate_tools_provider_submenus(tools_menu, parent, plugin)
	menu.AppendSubMenu(tools_menu, label or _("&Tools"))


def show_tools_menu(parent, anchor_btn=None, plugin=None):
	menu = wx.Menu()
	plugin = _resolve_plugin(parent, plugin)
	_populate_tools_provider_submenus(menu, parent, plugin)
	if anchor_btn is not None:
		pos = anchor_btn.GetPosition()
		pos = (pos.x, pos.y + anchor_btn.GetSize().height)
		parent.PopupMenu(menu, pos)
	else:
		parent.PopupMenu(menu)
	menu.Destroy()
