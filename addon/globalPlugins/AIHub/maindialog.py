# coding: UTF-8
import base64
import datetime
import json
import mimetypes
import os
import re
import sys
import threading
import time
import winsound
import gui
import wx

import addonHandler
import api
import braille
import config
import controlTypes
import queueHandler
import speech
import ui
from logHandler import log

from . import apikeymanager
from .audiohandlers import AudioHandlersMixin
from .chatcompletion import CompletionThread
from .historyhandlers import HistoryHandlersMixin
from .imagehandlers import ImageHandlersMixin
from .modelhandlers_core import ModelHandlersMixin
from .consts import (
	ADDON_DIR, ADDON_LIBS_DIR, DATA_DIR, LIBS_BASE, TEMP_DIR, cleanup_temp_dir, stop_progress_sound,
	TOP_P_MIN, TOP_P_MAX,
	DEFAULT_SYSTEM_PROMPT,
	TTS_VOICES, TTS_DEFAULT_VOICE,
	AUDIO_EXT_TO_FORMAT,
	SND_CHAT_RESPONSE_RECEIVED, SND_PROGRESS,
	REASONING_EFFORT_OPTIONS, DEFAULT_REASONING_EFFORT,
)
from .history import HistoryBlock, TextSegment
from .imagehelper import encode_image, get_image_dimensions, resize_image
from .imagedlg import ImageFile, ImageFileTypes, get_display_size, URL_PATTERN
from .recordthread import RecordThread, WhisperTranscription, AudioInputResult
from .resultevent import ResultEvent, EVT_RESULT_ID
from .transcription import get_transcription_provider
from .toolsmenu import show_tools_menu

sys.path.insert(0, LIBS_BASE)
import markdown2
sys.path.remove(LIBS_BASE)

from .apiclient import (
	APIConnectionError,
	APIStatusError,
	Choice,
	ChatCompletion,
	Transcription,
	configure_client_for_provider,
)

addonHandler.initTranslation()

DATA_JSON_FP = os.path.join(DATA_DIR, "data.json")
AUDIO_RESPONSE_FILE = os.path.join(TEMP_DIR, "audio_response.wav")

addToSession = None
activeChatDlg = None

def EVT_RESULT(win, func):
	win.Connect(-1, -1, EVT_RESULT_ID, func)


def copyToClipAsHTML(html_content):
	html_data_object = wx.HTMLDataObject()
	html_data_object.SetHTML(html_content)
	if wx.TheClipboard.Open():
		wx.TheClipboard.Clear()
		wx.TheClipboard.SetData(html_data_object)
		wx.TheClipboard.Close()
	else:
		raise RuntimeError("Unable to open the clipboard")


class AIHubDlg(ModelHandlersMixin, ImageHandlersMixin, AudioHandlersMixin, HistoryHandlersMixin, wx.Dialog):

	def __init__(
		self,
		parent,
		client,
		conf,
		title=None,
		pathList=None,
		plugin=None,
		conversationData=None
	):
		global addToSession
		if not client or not conf:
			raise ValueError("AIHubDlg requires client and conf")
		self._plugin = plugin
		self.client = client
		self._base_url = client.base_url
		self._api_key = client.api_key
		self._organization = client.organization
		self.conf = conf
		self.data = self.loadData()
		self._orig_data = self.data.copy() if isinstance(self.data, dict) else None
		self._showThinkingInHistory = bool(self.data.get("showThinkingInHistory", True))
		self._historyPath = None
		self._conversationId = None
		self.blocks = []
		self._models = []
		self.pathList = []
		self.audioPathList = []
		self._fileToRemoveAfter = []
		self.lastFocusedItem = None
		self.historyObj = None
		self.foregroundObj = None
		if pathList:
			addToSession = self
			for path in pathList:
				self.addImageToList(
					path,
					removeAfter=True
				)
		self.previousPrompt = None
		self._lastSystem = None
		if self.conf["saveSystem"]:
			# If the user has chosen to save the system prompt, use the last system prompt used by the user as the default value, otherwise use the default system prompt.
			if "system" in self.data:
				self._lastSystem = self.data["system"]
			else:
				self._lastSystem = DEFAULT_SYSTEM_PROMPT
		else:
			# removes the system entry from data so that the last system prompt is not remembered when the user unchecks the save system prompt checkbox.
			self.data.pop("system", None)
		if conversationData:
			conv_name = conversationData.get("name", _("Untitled conversation"))
			title = f"{conv_name} - AI Hub"
		else:
			title = _("New conversation") + " - AI Hub"
		super().__init__(parent, title=title)

		self.Bind(wx.EVT_CHILD_FOCUS, self.onSetFocus)
		mainSizer = wx.BoxSizer(wx.VERTICAL)

		convButtonsSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.renameConversationBtn = wx.Button(
			self,
			# Translators: Button to rename the current conversation.
			label=_("&Rename conversation") + " (F2)"
		)
		self.renameConversationBtn.Bind(wx.EVT_BUTTON, self._renameConversation)
		convButtonsSizer.Add(self.renameConversationBtn, 0, wx.ALL, 5)
		self.newConversationBtn = wx.Button(
			self,
			# Translators: Button to start a new conversation.
			label=_("&New conversation") + " (Ctrl+N)"
		)
		self.newConversationBtn.Bind(wx.EVT_BUTTON, self._newConversation)
		convButtonsSizer.Add(self.newConversationBtn, 0, wx.ALL, 5)
		self.conversationListBtn = wx.Button(
			self,
			# Translators: Button to open the conversation history / list dialog.
			label=_("Conversation &list...") + " (Ctrl+L)"
		)
		self.conversationListBtn.Bind(wx.EVT_BUTTON, self._onConversationList)
		convButtonsSizer.Add(self.conversationListBtn, 0, wx.ALL, 5)
		self.saveConversationBtn = wx.Button(
			self,
			# Translators: Button to save current conversation manually.
			label=_("&Save conversation") + " (Ctrl+S)"
		)
		self.saveConversationBtn.Bind(wx.EVT_BUTTON, self._saveConversation)
		convButtonsSizer.Add(self.saveConversationBtn, 0, wx.ALL, 5)
		mainSizer.Add(convButtonsSizer, 0, wx.ALL, 0)

		accountsLabel = wx.StaticText(
			self,
			label=_("&Account:")
		)
		self.accountListCtrl = wx.ListBox(
			self,
			size=(700, 110)
		)
		mainSizer.Add(accountsLabel, 0, wx.ALL, 5)
		mainSizer.Add(self.accountListCtrl, 0, wx.ALL, 5)
		self.accountListCtrl.Bind(wx.EVT_LISTBOX, self.onAccountChange)

		systemLabel = wx.StaticText(
			self,
			# Translators: This is the label for the system prompt text control in the main dialog.
			label=_("S&ystem prompt:")
		)
		self.systemTextCtrl = wx.TextCtrl(
			self,
			size=(700, -1),
			style=wx.TE_MULTILINE,
		)
		mainSizer.Add(systemLabel, 0, wx.ALL, 5)
		mainSizer.Add(self.systemTextCtrl, 0, wx.ALL, 5)
		# Adds event handler to reset the system prompt to the default value when the user opens the context menu on the system prompt.
		self.systemTextCtrl.Bind(wx.EVT_CONTEXT_MENU, self.onSystemContextMenu)
		# If the system prompt has been defined by the user, use it as the default value, otherwise use the default system prompt.
		if conf["saveSystem"]:
			self.systemTextCtrl.SetValue(self._lastSystem)
		else:
			self.systemTextCtrl.SetValue(DEFAULT_SYSTEM_PROMPT)

		messagesLabel = wx.StaticText(
			self,
			# Translators: This is the label for the messages text control in the main dialog.
			label=_("&Messages:")
		)
		self.messagesTextCtrl = wx.TextCtrl(
			self,
			# Translators: This is the label for the messages text control in the main dialog.
			style=wx.TE_MULTILINE | wx.TE_READONLY,
			size=(700, -1)
		)
		mainSizer.Add(messagesLabel, 0, wx.ALL, 5)
		mainSizer.Add(self.messagesTextCtrl, 0, wx.ALL, 5)
		self.messagesTextCtrl.Bind(wx.EVT_CONTEXT_MENU, self.onHistoryContextMenu)
		self.messagesTextCtrl.Bind(wx.EVT_KEY_DOWN, self.onMessagesKeyDown)

		promptLabel = wx.StaticText(
			self,
			# Translators: This is the label for the prompt text control in the main dialog.
			label=_("&Prompt:")
		)
		self.promptTextCtrl = wx.TextCtrl(
			self,
			size=(700, -1),
		style=wx.TE_MULTILINE
		)
		mainSizer.Add(promptLabel, 0, wx.ALL, 5)
		self.promptTextCtrl.Bind(wx.EVT_CONTEXT_MENU, self.onPromptContextMenu)
		self.promptTextCtrl.Bind(wx.EVT_KEY_DOWN, self.onPromptKeyDown)
		self.promptTextCtrl.Bind(wx.EVT_TEXT_PASTE, self.onPromptPasteSmart)
		mainSizer.Add(self.promptTextCtrl, 0, wx.ALL | wx.EXPAND, 5)

		self.imagesLabel = wx.StaticText(
			self,
			# Translators: This is the label for the attachments list control in the main dialog.
			label=_("Files:")
		)
		self.imagesListCtrl = wx.ListCtrl(
			self,
			style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES,
			size=(700, 200)
		)
		self.imagesListCtrl.InsertColumn(
			0,
			# Translators: This is the label for the name column in the image list control in the main dialog.
			_("name")
		)
		self.imagesListCtrl.InsertColumn(
			1,
			# Translators: This is the label for the path column in the image list control in the main dialog.
			_("path")
		)
		self.imagesListCtrl.InsertColumn(
			2,
			# Translators: This is the label for the size column in the image list control in the main dialog.
			_("size")
		)
		self.imagesListCtrl.InsertColumn(
			3,
			# Translators: This is the label for the dimensions column in the file list control in the main dialog.
			_("Dimensions")
		)
		self.imagesListCtrl.InsertColumn(
			4,
			# Translators: This is the label for the description column in the image list control in the main dialog.
			_("description")
		)
		self.imagesListCtrl.SetColumnWidth(0, 100)
		self.imagesListCtrl.SetColumnWidth(1, 200)
		self.imagesListCtrl.SetColumnWidth(2, 100)
		self.imagesListCtrl.SetColumnWidth(3, 100)
		self.imagesListCtrl.SetColumnWidth(4, 200)
		mainSizer.Add(self.imagesLabel, 0, wx.ALL, 5)
		mainSizer.Add(self.imagesListCtrl, 0, wx.ALL, 5)
		self.imagesListCtrl.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onImageListContextMenu)
		self.imagesListCtrl.Bind(wx.EVT_KEY_DOWN, self.onImageListKeyDown)
		self.imagesListCtrl.Bind(wx.EVT_CONTEXT_MENU, self.onImageListContextMenu)
		self.imagesListCtrl.Bind(wx.EVT_RIGHT_UP, self.onImageListContextMenu)

		self.audioLabel = wx.StaticText(
			self,
			label=_("&Audio files:")
		)
		self.audioListCtrl = wx.ListCtrl(
			self,
			style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES,
			size=(700, 120)
		)
		self.audioListCtrl.InsertColumn(0, _("File"))
		self.audioListCtrl.InsertColumn(1, _("Path"))
		self.audioListCtrl.SetColumnWidth(0, 150)
		self.audioListCtrl.SetColumnWidth(1, 450)
		mainSizer.Add(self.audioLabel, 0, wx.ALL, 5)
		mainSizer.Add(self.audioListCtrl, 0, wx.ALL, 5)
		self.audioListCtrl.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onAudioListContextMenu)
		self.audioListCtrl.Bind(wx.EVT_CONTEXT_MENU, self.onAudioListContextMenu)
		self.audioListCtrl.Bind(wx.EVT_KEY_DOWN, self.onAudioListKeyDown)
		self.audioLabel.Hide()
		self.audioListCtrl.Hide()

		if self.pathList:
			self.promptTextCtrl.SetValue(
				self.getDefaultImageDescriptionsPrompt()
			)
		self.updateImageList()
		self.updateAudioList()

		modelsLabel = wx.StaticText(
			self,
			# Translators: This is the label for the model list box in the main dialog.
			label=_("M&odel:")
		)
		self.modelsListCtrl = wx.ListBox(
			self,
			size=(700, 200)
		)
		self.modelsListCtrl.Bind(wx.EVT_KEY_DOWN, self.onModelKeyDown)
		self.modelsListCtrl.Bind(wx.EVT_CONTEXT_MENU, self.onModelContextMenu)
		self.modelsListCtrl.Bind(wx.EVT_RIGHT_UP, self.onModelContextMenu)
		mainSizer.Add(modelsLabel, 0, wx.ALL, 5)
		mainSizer.Add(self.modelsListCtrl, 0, wx.ALL, 5)

		# Model-specific options: shown only when the selected model supports them
		modelOptionsSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.reasoningModeCheckBox = wx.CheckBox(
			self,
			# Translators: Enable reasoning/thinking for models that support it (e.g. O1, O4).
			label=_("&Reasoning mode")
		)
		self.reasoningModeCheckBox.SetValue(False)
		self.reasoningModeCheckBox.Bind(wx.EVT_CHECKBOX, self._onReasoningModeChange)
		modelOptionsSizer.Add(self.reasoningModeCheckBox, 0, wx.ALL, 5)
		# Translators: Use adaptive thinking when model supports it (Anthropic 4.6).
		self.adaptiveThinkingCheckBox = wx.CheckBox(
			self,
			label=_("&Adaptive thinking")
		)
		self.adaptiveThinkingCheckBox.SetValue(conf.get("adaptiveThinking", True))
		self.adaptiveThinkingCheckBox.Bind(wx.EVT_CHECKBOX, self._onAdaptiveThinkingChange)
		modelOptionsSizer.Add(self.adaptiveThinkingCheckBox, 0, wx.ALL, 5)
		self.webSearchCheckBox = wx.CheckBox(
			self,
			# Translators: Enable web search for up-to-date information (models that support it).
			label=_("&Web search")
		)
		self.webSearchCheckBox.SetValue(False)
		modelOptionsSizer.Add(self.webSearchCheckBox, 0, wx.ALL, 5)
		mainSizer.Add(modelOptionsSizer, 0, wx.ALL, 0)

		self.reasoningEffortLabel = wx.StaticText(
			self,
			# Translators: Label for the reasoning effort dropdown, like Whisper Response Format.
			label=_("Reasoning &effort:")
		)
		self.reasoningEffortChoice = wx.Choice(self, choices=[])
		self.reasoningEffortChoice.Bind(wx.EVT_CHOICE, self._onReasoningEffortChange)
		mainSizer.Add(self.reasoningEffortLabel, 0, wx.ALL, 5)
		mainSizer.Add(self.reasoningEffortChoice, 0, wx.ALL, 5)

		maxTokensLabel = wx.StaticText(
			self,
			# Translators: This is the label for the max tokens spin control in the main dialog.
			label=_("Max to&kens:")
		)
		self.maxTokensSpinCtrl = wx.SpinCtrl(
			self,
			min=0
		)
		mainSizer.Add(maxTokensLabel, 0, wx.ALL, 5)
		mainSizer.Add(self.maxTokensSpinCtrl, 0, wx.ALL, 5)

		if conf["advancedMode"]:
			self.temperatureLabel = wx.StaticText(
				self,
				# Translators: This is the label for the temperature spin control in the main dialog.
				label=_("&Temperature:")
			)
			self.temperatureSpinCtrl = wx.SpinCtrl(
				self,
				min=0,
				max=200
			)
			mainSizer.Add(self.temperatureLabel, 0, wx.ALL, 5)
			mainSizer.Add(self.temperatureSpinCtrl, 0, wx.ALL, 5)

			self.topPLabel = wx.StaticText(
				self,
				# Translators: This is the label for the top P spin control in the main dialog.
				label=_("Pro&bability Mass (top P):")
			)
			self.topPSpinCtrl = wx.SpinCtrl(
				self,
				min=TOP_P_MIN,
				max=TOP_P_MAX,
				initial=conf["topP"]
			)
			mainSizer.Add(self.topPLabel, 0, wx.ALL, 5)
			mainSizer.Add(self.topPSpinCtrl, 0, wx.ALL, 5)

			self.streamModeCheckBox = wx.CheckBox(
				self,
				label=_("&Stream mode")
			)
			self.streamModeCheckBox.SetValue(conf["stream"])
			mainSizer.Add(self.streamModeCheckBox, 0, wx.ALL, 5)

			self.debugModeCheckBox = wx.CheckBox(
				self,
				label=_("Debu&g mode")
			)
			self.debugModeCheckBox.SetValue(conf["debug"])
			mainSizer.Add(self.debugModeCheckBox, 0, wx.ALL, 5)

		# Initialize the state of the controls according to the selected model.
		self._refreshAccountsList()
		self.onAccountChange(None)
		self.onModelChange(None)
		self.modelsListCtrl.Bind(wx.EVT_LISTBOX, self.onModelChange)

		buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.toolsBtn = wx.Button(
			self,
			label=_("&Tools...")
		)
		self.toolsBtn.Bind(wx.EVT_BUTTON, self.onProviderTools)
		self.toolsBtn.SetToolTip(_("Open tools menu (OpenAI, Mistral, Google)."))

		for btn in (
			self.toolsBtn,
		):
			buttonsSizer.Add(btn, 0, wx.ALL, 5)
		mainSizer.Add(buttonsSizer, 0, wx.ALL, 5)

		submitCancelSizer = wx.BoxSizer(wx.HORIZONTAL)

		self.submitBtn = wx.Button(
			self,
			id=wx.ID_OK,
			# Translators: This is the label for the submit button in the main dialog.
			label=_("Submit") + " (Ctrl+Enter)"
		)
		self.submitBtn.Bind(wx.EVT_BUTTON, self.onSubmit)
		self.submitBtn.SetDefault()
		submitCancelSizer.Add(self.submitBtn, 0, wx.ALL, 5)

		self.closeBtn = wx.Button(
			self,
			id=wx.ID_CLOSE
		)
		self.closeBtn.Bind(wx.EVT_BUTTON, self.onCancel)
		submitCancelSizer.Add(self.closeBtn, 0, wx.ALL, 5)

		mainSizer.Add(submitCancelSizer, 0, wx.ALL | wx.ALIGN_CENTER, 5)

		self.SetSizerAndFit(mainSizer)
		mainSizer.SetSizeHints(self)
		if parent:
			self.CentreOnParent(wx.BOTH)
		else:
			self.Centre(wx.BOTH)
		self.SetEscapeId(wx.ID_CLOSE)

		self.addShortcuts()
		self.promptTextCtrl.SetFocus()
		EVT_RESULT(self, self.OnResult)
		global activeChatDlg
		activeChatDlg = self

		self.worker = None
		self.firstBlock = None
		self.lastBlock = None
		self._audioPlayingPath = None  # Path of audio currently playing (for stop)
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
		self.timer.Start (100)
		self.Bind(wx.EVT_CHAR_HOOK, self.onCharHook)
		self.Bind(wx.EVT_CLOSE, self.onCancel)
		if conversationData:
			self._loadConversation(conversationData)

	def _onReasoningModeChange(self, evt):
		"""Update effort/adaptive visibility when reasoning checkbox toggles."""
		self.onModelChange(evt)

	def _onReasoningEffortChange(self, evt):
		"""Persist reasoning effort to config when user changes the dropdown."""
		opts = getattr(self, "_reasoningEffortOptions", ())
		idx = self.reasoningEffortChoice.GetSelection()
		if 0 <= idx < len(opts):
			self.conf["reasoningEffort"] = opts[idx][0]

	def _onAdaptiveThinkingChange(self, evt):
		"""Persist adaptive thinking preference when user changes the checkbox."""
		self.conf["adaptiveThinking"] = self.adaptiveThinkingCheckBox.IsChecked()

	def onResetSystemPrompt(self, event):
		self.systemTextCtrl.SetValue(DEFAULT_SYSTEM_PROMPT)

	def onDelete(self, event):
		self.systemTextCtrl.SetValue('')

	def addStandardMenuOptions(self, menu, include_paste=True):
		menu.Append(wx.ID_UNDO)
		menu.Append(wx.ID_REDO)
		menu.AppendSeparator()
		menu.Append(wx.ID_CUT)
		menu.Append(wx.ID_COPY)
		if include_paste:
			menu.Append(wx.ID_PASTE)
		menu.Append(wx.ID_DELETE)
		menu.AppendSeparator()
		menu.Append(wx.ID_SELECTALL)
		self.Bind(wx.EVT_MENU, self.onDelete, id=wx.ID_DELETE)

	def loadData(self):
		if not os.path.exists(DATA_JSON_FP):
			return {}
		try:
			with open(DATA_JSON_FP, 'r') as f :
				return json.loads(f.read())
		except Exception as err:
			log.error(f"loadData: {err}", exc_info=True)

	def saveData(self, force=False):
		if not force and self.data == self._orig_data:
			return
		tmp_path = DATA_JSON_FP + ".tmp"
		with open(tmp_path, "w", encoding="utf-8") as f:
			json.dump(self.data, f, ensure_ascii=False)
		os.replace(tmp_path, DATA_JSON_FP)

	def _appendBlockToMessages(self, block):
		"""Render a completed HistoryBlock into the messages text control.
		Assign segment refs to block so j/k navigation and context menu work."""
		if block != self.firstBlock:
			block.previous.segmentBreakLine = TextSegment(self.messagesTextCtrl, "\n", block)
		block.segmentPromptLabel = TextSegment(self.messagesTextCtrl, _("User:") + " ", block)
		prompt_text = block.prompt or ""
		if not prompt_text:
			tlist = getattr(block, "audioTranscriptList", None)
			if tlist and any(t for t in tlist):
				prompt_text = "\n".join(t for t in tlist if t).strip()
		block.segmentPrompt = TextSegment(self.messagesTextCtrl, (prompt_text or "") + "\n", block)
		block.segmentResponseLabel = TextSegment(self.messagesTextCtrl, _("Assistant:") + " ", block)
		# Keep think block before visible assistant response.
		if self._showThinkingInHistory and (block.reasoningText or "").strip():
			block.segmentReasoningLabel = TextSegment(self.messagesTextCtrl, "", block)
			block.segmentReasoning = TextSegment(self.messagesTextCtrl, self._formatThinkingForHistory(block.reasoningText), block)
			block.segmentReasoningSuffix = None
			block.lastReasoningLen = len(block.reasoningText or "")
		block.segmentResponse = TextSegment(self.messagesTextCtrl, (block.responseText or "") + "\n", block)

	def _formatThinkingForHistory(self, reasoning_text):
		text = (reasoning_text or "").strip()
		if not text:
			return ""
		return f"<think>\n{text}\n</think>\n"

	def _clearMessagesSegments(self):
		self.messagesTextCtrl.Clear()
		if hasattr(self.messagesTextCtrl, "firstSegment"):
			self.messagesTextCtrl.firstSegment = None
			self.messagesTextCtrl.lastSegment = None

	def _getHistoryAnchor(self):
		segment = TextSegment.getCurrentSegment(self.messagesTextCtrl)
		if not segment:
			return None, "prompt"
		block = getattr(segment, "owner", None)
		if not block:
			return None, "prompt"
		if segment in (block.segmentPromptLabel, block.segmentPrompt):
			return block, "prompt"
		if segment in (block.segmentResponseLabel, block.segmentResponse):
			return block, "response"
		if segment in (block.segmentReasoningLabel, block.segmentReasoning):
			return block, "reasoning"
		return block, "response"

	def _restoreHistoryAnchor(self, block, part="response"):
		if not block:
			if self.firstBlock and self.firstBlock.segmentPrompt is not None:
				self.messagesTextCtrl.SetInsertionPoint(self.firstBlock.segmentPrompt.start)
			return
		target_segment = None
		if part == "reasoning":
			target_segment = block.segmentReasoning or block.segmentReasoningLabel
		if target_segment is None and part == "response":
			target_segment = block.segmentResponse or block.segmentResponseLabel
		if target_segment is None:
			target_segment = block.segmentPrompt or block.segmentPromptLabel
		if target_segment is None:
			target_segment = block.segmentResponse or block.segmentResponseLabel or block.segmentReasoning or block.segmentReasoningLabel
		if target_segment is not None:
			self.messagesTextCtrl.SetInsertionPoint(target_segment.start)

	def _rerenderMessages(self, anchor_block=None, anchor_part="response"):
		self._clearMessagesSegments()
		b = self.firstBlock
		while b:
			b.segmentBreakLine = None
			b.segmentPromptLabel = None
			b.segmentPrompt = None
			b.segmentResponseLabel = None
			b.segmentResponse = None
			b.segmentReasoningLabel = None
			b.segmentReasoning = None
			b.segmentReasoningSuffix = None
			self._appendBlockToMessages(b)
			b = b.next
		self._restoreHistoryAnchor(anchor_block, anchor_part)

	def onToggleThinkingInHistory(self, evt=None):
		anchor_block, anchor_part = self._getHistoryAnchor()
		self._showThinkingInHistory = not self._showThinkingInHistory
		self.data["showThinkingInHistory"] = self._showThinkingInHistory
		self._rerenderMessages(anchor_block, anchor_part)
		self.message(_("Thinking content shown in history.") if self._showThinkingInHistory else _("Thinking content hidden in history."))

	def _loadConversation(self, data):
		"""Load conversation data (blocks, system) from saved conversation."""
		from . import conversations
		blocks = data.get("blocks", [])
		if not blocks:
			return
		# Clear messages control and reset segment chain for a clean load
		self._clearMessagesSegments()
		system = data.get("system", "")
		if system and self.conf["saveSystem"]:
			self.systemTextCtrl.SetValue(system)
			self._lastSystem = system
		draft_prompt = data.get("draftPrompt", "")
		if isinstance(draft_prompt, str) and draft_prompt:
			self.promptTextCtrl.SetValue(draft_prompt)
			self.promptTextCtrl.SetInsertionPointEnd()
		draft_path_list = data.get("draftPathList", [])
		self.pathList = []
		if isinstance(draft_path_list, list):
			for item in draft_path_list:
				if isinstance(item, dict):
					path = item.get("path", "")
					name = item.get("name", "")
					if path:
						try:
							self.pathList.append(ImageFile(path, name=name or None))
						except Exception as err:
							log.warning(f"load draft image skipped {path}: {err}")
				elif isinstance(item, str) and item:
					try:
						self.pathList.append(ImageFile(item))
					except Exception as err:
						log.warning(f"load draft image skipped {item}: {err}")
		draft_audio_list = data.get("draftAudioPathList", [])
		self.audioPathList = []
		if isinstance(draft_audio_list, list):
			for item in draft_audio_list:
				if isinstance(item, str) and item:
					self.audioPathList.append(item)
		self.updateImageList(focusPrompt=False)
		self.updateAudioList(focusPrompt=False)
		conv_id = data.get("id")
		if conv_id:
			self._conversationId = conv_id
		prev = None
		for b in blocks:
			b.lastLen = len(b.responseText or "")
			b.lastReasoningLen = len(b.reasoningText or "")
			b.displayHeader = False  # Already rendered
			if prev is not None:
				prev.next = b
				b.previous = prev
			else:
				self.firstBlock = b
			prev = b
		self.lastBlock = prev
		for b in blocks:
			self._appendBlockToMessages(b)
		# Move cursor to start of first message for consistent navigation
		if self.firstBlock and self.firstBlock.segmentPrompt is not None:
			self.messagesTextCtrl.SetInsertionPoint(self.firstBlock.segmentPrompt.start)

	def _getBlocksForSave(self):
		"""Collect all blocks from firstBlock to lastBlock for saving."""
		blocks = []
		b = self.firstBlock
		while b:
			blocks.append(b)
			b = b.next
		return blocks

	def _autoSaveConversation(self, force=False):
		"""Save conversation state. Auto-save obeys setting unless forced (manual save)."""
		from . import conversations
		if not force and not self.conf.get("autoSaveConversation", True):
			return False
		blocks = self._getBlocksForSave()
		draft_prompt = self.promptTextCtrl.GetValue()
		if not blocks and not (force and draft_prompt.strip()):
			return False
		system = self.systemTextCtrl.GetValue().strip()
		model = self.getCurrentModel()
		model_id = model.id if model else ""
		name = None
		if not self._conversationId:
			if blocks:
				first = blocks[0]
				prompt = getattr(first, "prompt", "") or ""
				tlist = getattr(first, "audioTranscriptList", None)
				if not prompt and tlist and any(t for t in tlist):
					prompt = "\n".join(t for t in tlist if t).strip()
			else:
				prompt = draft_prompt.strip()
			name = conversations.get_default_title(prompt)
		try:
			conv_id = conversations.save_conversation(
				blocks,
				system=system,
				model=model_id,
				name=name,
				conv_id=self._conversationId,
				draftPrompt=draft_prompt,
				draftPathList=self.pathList,
				draftAudioPathList=self.audioPathList,
			)
			self._conversationId = conv_id
			if name:
				self.SetTitle(f"{name} - AI Hub")
			return True
		except Exception as err:
			log.error(f"auto-save conversation: {err}", exc_info=True)
			return False

	def _saveConversation(self, evt=None):
		"""Save current conversation to storage (manual, from menu)."""
		blocks = self._getBlocksForSave()
		draft_prompt = self.promptTextCtrl.GetValue().strip()
		if not blocks and not draft_prompt:
			ui.message(_("No messages or prompt to save."))
			return
		if self._autoSaveConversation(force=True):
			ui.message(_("Conversation saved."))
		else:
			gui.messageBox(
				_("Unable to save conversation. Check the NVDA log for details."),
				_("Save conversation"),
				wx.OK | wx.ICON_ERROR
			)

	def _renameConversation(self, evt=None):
		"""Rename current conversation."""
		from . import conversations
		if not self._conversationId:
			ui.message(_("Save the conversation first before renaming."))
			return
		entry = next((e for e in conversations.list_conversations() if e.get("id") == self._conversationId), None)
		current_name = entry.get("name", _("Untitled conversation")) if entry else ""
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
		if conversations.rename_conversation(self._conversationId, new_name):
			self.SetTitle(f"{new_name} - AI Hub")

	def _onConversationList(self, evt=None):
		"""Open the conversation history dialog."""
		from .conversationdlg import show_conversations_manager
		if self._plugin:
			wx.CallAfter(show_conversations_manager, self._plugin)

	def _newConversation(self, evt=None):
		"""Start a new conversation in a fresh dialog instance."""
		if self._plugin:
			wx.CallAfter(self._plugin._openMainDialog, None, None, True)
			return
		self.promptTextCtrl.Clear()
		ui.message(_("New conversation"))

	def onSubmit(self, evt):
		try:
			self._onSubmitImpl(evt)
		except Exception as err:
			log.error(f"onSubmit: {err}", exc_info=True)
			self.enableControls()
			self.worker = None
			gui.messageBox(
				_("An error occurred. More information is in the NVDA log."),
				_("OpenAI Error"),
				wx.OK | wx.ICON_ERROR
			)

	def _onSubmitImpl(self, evt):
		if not getattr(self, "_askPromptOverride", None) and not self.promptTextCtrl.GetValue().strip() and not self.pathList and not self.audioPathList:
			self.promptTextCtrl.SetFocus()
			return
		if self.worker:
			return
		model = self._requireModel(modal=True)
		if not model:
			return
		account = self._requireAccount(modal=True)
		if not account:
			return
		if account["provider"] != model.provider:
			gui.messageBox(
				_("The selected account provider (%s) does not match the selected model provider (%s). Please select a compatible account or model.") % (
					account["provider"],
					model.provider
				),
				_("Provider mismatch"),
				wx.OK | wx.ICON_ERROR
			)
			return
		if not apikeymanager.get(model.provider).isReady(account_id=account["id"]):
			gui.messageBox(
				_("This model is only available with the %s provider and the selected account is not ready. Please verify your account API key in settings, or select another account/model.") % (
					model.provider
				),
				_("No API key for %s") % model.provider,
				wx.OK | wx.ICON_ERROR
			)
			return

		ok, validation_message = self.validateAttachmentsForProvider(provider=model.provider, pathList=self.pathList)
		if not ok:
			gui.messageBox(
				validation_message,
				_("Unsupported attachments"),
				wx.OK | wx.ICON_ERROR
			)
			return

		if not model.vision and self.pathList:
			visionModels = [m.id for m in self._models if m.vision]
			gui.messageBox(
				_("This model (%s) does not support image description. Please select one of the following models: %s.") % (
					model.id,
					", ".join(visionModels)
				),
				_("Invalid model"),
				wx.OK | wx.ICON_ERROR
			)
			return
		if self.audioPathList and not getattr(model, "audioInput", False):
			audioModels = [m.id for m in self._models if getattr(m, "audioInput", False)]
			gui.messageBox(
				_("This model (%s) does not support audio input. Please select one of the following models: %s.") % (
					model.id,
					", ".join(audioModels) if audioModels else _("none available")
				),
				_("Invalid model"),
				wx.OK | wx.ICON_ERROR
			)
			return
		if (
			model.vision
			and not self.conf["images"]["resize"]
			and not self.conf["images"]["resizeInfoDisplayed"]
		):
			msg = _("Be aware that the add-on may auto-resize images before API submission to lower request sizes and costs. Adjust this feature in the AI Hub settings if needed. This message won't show again.")
			gui.messageBox(
				msg,
				_("Image resizing"),
				wx.OK | wx.ICON_INFORMATION
			)
			self.conf["images"]["resizeInfoDisplayed"] = True
		system = self.systemTextCtrl.GetValue().strip()
		if self.conf["saveSystem"] and system != self._lastSystem:
			self.data["system"] = system
			self._lastSystem = system
		self.disableControls()
		api.processPendingEvents()
		self.foregroundObj = api.getForegroundObject()
		if not self.foregroundObj:
			log.error("Unable to retrieve the foreground object", exc_info=True)
		try:
			children = getattr(self.foregroundObj, "children", []) or []
			obj = children[4] if len(children) > 4 else None
			if obj and obj.role == controlTypes.ROLE_EDITABLETEXT:
				self.historyObj = obj
			else:
				self.historyObj = None
				if obj is None and children:
					log.debug("History object not at children[4] (foreground may not be dialog)")
		except Exception as err:
			log.error(f"Error finding history object: {err}", exc_info=True)
			self.historyObj = None
		self.stopRequest = threading.Event()
		self.worker = CompletionThread(self)
		self.worker.start()

	def onCancel(self, evt):
		stop_progress_sound()  # Stop all sounds (progress, etc.) first
		global addToSession, activeChatDlg
		if addToSession and addToSession is self:
			addToSession = None
		if activeChatDlg is self:
			activeChatDlg = None
		plugin = getattr(self, "_plugin", None)
		if plugin:
			if getattr(plugin, "askRecordThread", None):
				try:
					plugin.askRecordThread.stop()
				except Exception:
					pass
				try:
					plugin.askRecordThread.join(timeout=0.8)
				except Exception:
					pass
				plugin.askRecordThread = None
			if getattr(plugin, "_askAudioPlaying", False):
				from .ask_question import mci_stop_ask_audio
				mci_stop_ask_audio()
				plugin._askAudioPlaying = False
		if self.worker:
			if hasattr(self, "stopRequest") and self.stopRequest:
				self.stopRequest.set()
			if hasattr(self.worker, "stop"):
				try:
					self.worker.stop()
				except Exception:
					pass
			elif hasattr(self.worker, "abort"):
				try:
					self.worker.abort()
				except Exception:
					pass
			try:
				self.worker.join(timeout=0.8)
			except Exception:
				pass
			self.worker = None
		# Persist draft prompt and current conversation state on close when auto-save is enabled.
		if self.conf.get("autoSaveConversation", True):
			try:
				# Do not create empty conversation entries on close.
				self._autoSaveConversation()
			except Exception as err:
				log.error(f"onCancel auto-save conversation: {err}", exc_info=True)
		cleanup_temp_dir()
		# remove files marked for deletion
		for path in self._fileToRemoveAfter:
			if os.path.exists(path):
				try:
					os.remove(path)
				except Exception as err:
					log.error(f"onCancel delete file: {err}", exc_info=True)
					gui.messageBox(
						_("Unable to delete the file: %s\nPlease remove it manually.") % path,
						"AI Hub",
						wx.OK | wx.ICON_ERROR
					)
		self.saveData()
		self.timer.Stop()
		self.Destroy()

	def OnResult(self, event):
		stop_progress_sound()  # Always stop progress/loop sounds first
		is_success = (
			event.data is None
			or isinstance(event.data, (Choice, Transcription, WhisperTranscription, AudioInputResult))
		)
		if is_success and self.conf["chatFeedback"]["sndResponseReceived"]:
			winsound.PlaySound(SND_CHAT_RESPONSE_RECEIVED, winsound.SND_ASYNC)
		self.enableControls()
		self.worker = None

		if not event.data:
			# Streaming complete; auto-save conversation
			self._autoSaveConversation()
			if getattr(self, "_askQuestionDeferred", False):
				self._askQuestionDeferred = False
				wx.CallAfter(self.onSubmit, None)
			return

		if isinstance(event.data, Choice):
			historyBlock = HistoryBlock()
			historyBlock.system = self.systemTextCtrl.GetValue().strip()
			historyBlock.prompt = self.promptTextCtrl.GetValue().strip()
			model = self.getCurrentModel()
			if model:
				historyBlock.model = model.id
				if self.conf["advancedMode"]:
					historyBlock.temperature = self.temperatureSpinCtrl.GetValue() / 100
					historyBlock.topP = self.topPSpinCtrl.GetValue() / 100
				else:
					historyBlock.temperature = model.defaultTemperature
					historyBlock.topP = self.conf["topP"] / 100
			else:
				historyBlock.model = self._models[0].id if self._models else ""
				if self.conf["advancedMode"]:
					historyBlock.temperature = self.temperatureSpinCtrl.GetValue() / 100
					historyBlock.topP = self.topPSpinCtrl.GetValue() / 100
				else:
					historyBlock.temperature = self.conf.get("temperature", 0.7)
					historyBlock.topP = self.conf["topP"] / 100
			historyBlock.maxTokens = self.maxTokensSpinCtrl.GetValue()
			historyBlock.responseText = event.data.message.content
			historyBlock.reasoningText = getattr(event.data.message, "reasoning", "") or ""
			historyBlock.responseTerminated = True
			if self.lastBlock is None:
				self.firstBlock = self.lastBlock = historyBlock
			else:
				self.lastBlock.next = historyBlock
				historyBlock.previous = self.lastBlock
				self.lastBlock = historyBlock
			self.previousPrompt = self.promptTextCtrl.GetValue()
			self.promptTextCtrl.Clear()
			# Non-streaming response; auto-save conversation
			self._autoSaveConversation()
			if getattr(self, "_askQuestionDeferred", False):
				self._askQuestionDeferred = False
				wx.CallAfter(self.onSubmit, None)
			return
		if isinstance(event.data, AudioInputResult):
			path = self.persistAudioPath(event.data.path)
			if path not in self.audioPathList:
				self.audioPathList.append(path)
			self.updateAudioList(focusPrompt=False)
			self.message(_("Audio added for direct model input"))
			if getattr(self, "_askQuestionPending", False):
				self._askQuestionPending = False
				wx.CallAfter(self.onSubmit, None)
			return
		if isinstance(event.data, (Transcription, WhisperTranscription)):
			self.promptTextCtrl.AppendText(
				event.data.text if event.data.text else ""
			)
			self.promptTextCtrl.SetFocus()
			self.promptTextCtrl.SetInsertionPointEnd()
			self.message(
				_("Insertion of: %s") % event.data.text,
				True
			)
			return

		errMsg = _("An error occurred. More information is in the NVDA log.")
		if isinstance(event.data, str):
			log.error(f"OpenAI add-on error: {event.data}", exc_info=True)
			errMsg = event.data if len(event.data) < 500 else event.data[:500] + "..."
		elif isinstance(event.data, (APIConnectionError, APIStatusError)):
			log.error(f"OpenAI add-on error: {event.data.message}", exc_info=True)
			errMsg = event.data.message
		else:
			log.error(f"OpenAI add-on error: {event.data}", exc_info=True)
			if hasattr(event.data, 'message'):
				errMsg = str(event.data.message)
			else:
				errMsg = _("An error occurred. More information is in the NVDA log.")
		# check if the error contains an URL, retrieve it to ask if the user wants to open it in the browser
		url = re.search(r"https?://[^\s]+", errMsg)
		if url:
			errMsg += "\n\n" + _("Do you want to open the URL in your browser?")
		res = gui.messageBox(
			errMsg,
			_("OpenAI Error"),
			wx.OK | wx.ICON_ERROR | wx.CENTRE if not url else wx.YES_NO | wx.ICON_ERROR | wx.CENTRE,
		)
		if url and res == wx.YES:
			os.startfile(url.group(0).rstrip("."))
		if "model's maximum context length is " in errMsg:
			self.modelsListCtrl.SetFocus()
		else:
			self.promptTextCtrl.SetFocus()
		if getattr(self, "_askQuestionDeferred", False):
			self._askQuestionDeferred = False
			wx.CallAfter(self.onSubmit, None)
			return

	def onCharHook(self, evt):
		if self.conf["blockEscapeKey"] and evt.GetKeyCode() == wx.WXK_ESCAPE:
			self.message(_("Press Alt+F4 to close the dialog"))
		else:
			evt.Skip()

	def onTimer(self, event):
		if self.lastBlock is not None:
			block = self.lastBlock
			if block.displayHeader:
				if block != self.firstBlock:
					block.previous.segmentBreakLine = TextSegment(self.messagesTextCtrl, "\n", block)
				block.segmentPromptLabel = TextSegment(self.messagesTextCtrl, _("User:") + ' ', block)
				prompt_text = block.prompt
				if not prompt_text:
					tlist = getattr(block, "audioTranscriptList", None)
					if tlist and any(t for t in tlist):
						prompt_text = "\n".join(t for t in tlist if t).strip()
				block.segmentPrompt = TextSegment(self.messagesTextCtrl, (prompt_text or "") + "\n", block)
				block.segmentResponseLabel = TextSegment(self.messagesTextCtrl, _("Assistant:") + ' ', block)
				block.displayHeader = False
			l = len(block.responseText)
			if block.lastLen == 0 and l > 0:
				cur_pos = self.messagesTextCtrl.GetInsertionPoint()
				end_pos = self.messagesTextCtrl.GetLastPosition()
				user_reading_history = self.messagesTextCtrl.HasFocus() and cur_pos < end_pos
				if not user_reading_history:
					self.messagesTextCtrl.SetInsertionPointEnd()
					if (
						self.historyObj
						and self.foregroundObj is api.getForegroundObject()
					):
						if braille.handler.buffer is braille.handler.messageBuffer:
							braille.handler._dismissMessage()
						self.focusHistoryBrl()
					else:
						log.debug("Unable to focus the history object or the foreground object has changed")
				block.responseText = block.responseText.lstrip()
				l = len(block.responseText)
			if l > block.lastLen:
				newText = block.responseText[block.lastLen:]
				block.lastLen = l
				if block.segmentResponse is None:
					block.segmentResponse = TextSegment(self.messagesTextCtrl, newText, block)
				else:
					block.segmentResponse.appendText(newText)
			reasoning_len = len(block.reasoningText or "")
			last_reasoning_len = getattr(block, "lastReasoningLen", 0)
			if self._showThinkingInHistory and reasoning_len > last_reasoning_len:
				# Optimize thinking streaming:
				# - append directly when the thinking segment already exists
				# - create it in place when possible (before response starts)
				# - rerender only once if response already started and thinking must be inserted before it
				reasoning_delta = (block.reasoningText or "")[last_reasoning_len:]
				reasoning_suffix = getattr(block, "segmentReasoningSuffix", None)
				if block.segmentReasoning is not None and reasoning_suffix is not None:
					block.segmentReasoning.appendText(reasoning_delta)
				elif not (block.responseText or "").strip():
					block.segmentReasoningLabel = TextSegment(self.messagesTextCtrl, "", block)
					block.segmentReasoning = TextSegment(self.messagesTextCtrl, "<think>\n" + (block.reasoningText or ""), block)
					block.segmentReasoningSuffix = TextSegment(self.messagesTextCtrl, "\n</think>\n", block)
				else:
					anchor_block, anchor_part = self._getHistoryAnchor()
					if anchor_block is None:
						anchor_block = block
						anchor_part = "response"
					self._rerenderMessages(anchor_block=anchor_block, anchor_part=anchor_part)
				block.lastReasoningLen = reasoning_len
			if (
				self._showThinkingInHistory
				and block.responseTerminated
				and (block.reasoningText or "").strip()
				and block.segmentReasoning is None
			):
				# Streaming text is already appended; rebuild once so think renders before response.
				anchor_block, anchor_part = self._getHistoryAnchor()
				if anchor_block is None:
					anchor_block, anchor_part = block, "response"
				self._rerenderMessages(anchor_block=anchor_block, anchor_part=anchor_part)

	def addEntry(self, accelEntries, modifiers, key, func):
		id_ = wx.Window.NewControlId()
		self.Bind(wx.EVT_MENU, func, id=id_)
		accelEntries.append ( (modifiers, key, id_))

	def addShortcuts(self):
		self.messagesTextCtrl.Bind(wx.EVT_TEXT_COPY, self.onCopyMessage)
		accelEntries  = []
		self.addEntry(accelEntries, wx.ACCEL_NORMAL, ord("M"), self.onCurrentMessage)
		self.addEntry(accelEntries, wx.ACCEL_CTRL + wx.ACCEL_SHIFT, wx.WXK_UP, self.onPreviousMessage)
		self.addEntry(accelEntries, wx.ACCEL_CTRL + wx.ACCEL_SHIFT, wx.WXK_DOWN, self.onNextMessage)
		self.addEntry(accelEntries, wx.ACCEL_SHIFT, ord("B"), self.onMoveToStartOfThinking)
		self.addEntry(accelEntries, wx.ACCEL_SHIFT, ord("N"), self.onMoveToEndOfThinking)
		self.addEntry(accelEntries, wx.ACCEL_NORMAL, ord("B"), self.onMoveToBeginOfContent)
		self.addEntry(accelEntries, wx.ACCEL_NORMAL, ord("N"), self.onMoveToEndOfContent)
		self.addEntry(accelEntries, wx.ACCEL_CTRL + wx.ACCEL_SHIFT, ord("C"), lambda evt: self.onCopyMessage(evt, True))
		self.addEntry(accelEntries, wx.ACCEL_CTRL, ord("D"), self.onDeleteBlock)
		self.addEntry(accelEntries, wx.ACCEL_CTRL + wx.ACCEL_SHIFT, ord("S"), self.onSaveHistory)
		self.addEntry(accelEntries, wx.ACCEL_CTRL, ord("P"), self.onAudioPlayPause)
		self.addEntry(accelEntries, wx.ACCEL_ALT, wx.WXK_RETURN, self.onMessageProperties)
		self.addEntry(accelEntries, wx.ACCEL_CTRL | wx.ACCEL_ALT, wx.WXK_RETURN, self.onConversationProperties)
		self.addEntry(accelEntries, wx.ACCEL_NORMAL, wx.WXK_SPACE, lambda evt: self.onWebviewMessage(evt, True))
		self.addEntry(accelEntries, wx.ACCEL_SHIFT, wx.WXK_SPACE, lambda evt: self.onWebviewMessage(evt, False))
		self.addEntry(accelEntries, wx.ACCEL_NORMAL, ord("R"), self.onToggleThinkingInHistory)
		self.addEntry(accelEntries, wx.ACCEL_ALT, wx.WXK_LEFT, self.onCopyResponseToSystem)
		self.addEntry(accelEntries, wx.ACCEL_ALT, wx.WXK_RIGHT, self.onCopyPromptToPrompt)
		accelTable = wx.AcceleratorTable(accelEntries)
		self.messagesTextCtrl.SetAcceleratorTable(accelTable)

		accelEntries  = []
		self.addEntry(accelEntries, wx.ACCEL_CTRL, wx.WXK_UP, self.onPreviousPrompt)
		accelTable = wx.AcceleratorTable(accelEntries)
		self.promptTextCtrl.SetAcceleratorTable(accelTable)

		accelEntries  = []
		self.addEntry(accelEntries, wx.ACCEL_NORMAL, wx.WXK_F2, self._renameConversation)
		self.addEntry(accelEntries, wx.ACCEL_CTRL, ord("N"), self._newConversation)
		self.addEntry(accelEntries, wx.ACCEL_CTRL, ord("S"), self._saveConversation)
		self.addEntry(accelEntries, wx.ACCEL_CTRL, ord("L"), self._onConversationList)
		self.addEntry(accelEntries, wx.ACCEL_CTRL, ord("r"), self.onRecord)
		self.addEntry(accelEntries, wx.ACCEL_CTRL, ord("i"), self.onImageDescriptionFromFilePath)
		self.addEntry(accelEntries, wx.ACCEL_CTRL, ord("u"), self.onImageDescriptionFromURL)
		self.addEntry(accelEntries, wx.ACCEL_CTRL, ord("e"), self.onImageDescriptionFromScreenshot)
		self.addEntry(accelEntries, wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord("T"), self.onProviderTools)
		accelTable = wx.AcceleratorTable(accelEntries)
		self.SetAcceleratorTable(accelTable)

	def getImages(
		self,
		pathList: list = None,
		prompt: str = None
	) -> list:
		conf = self.conf
		if not pathList:
			pathList = self.pathList
		images = []
		if prompt:
			images.append({
				"type": "text",
				"text": prompt
			})
		for imageFile in pathList:
			path = imageFile.path
			log.debug(f"Processing {path}")
			if imageFile.type == ImageFileTypes.IMAGE_URL:
				images.append({"type": "image_url", "image_url": {"url": path}})
			elif imageFile.type == ImageFileTypes.DOCUMENT_URL:
				images.append({"type": "input_file", "file_url": path, "filename": imageFile.name})
			elif imageFile.type == ImageFileTypes.IMAGE_LOCAL:
				if conf["images"]["resize"]:
					path_resized_image = os.path.join(TEMP_DIR, "last_resized.jpg")
					if resize_image(
						path,
						max_width=conf["images"]["maxWidth"],
						max_height=conf["images"]["maxHeight"],
						quality=conf["images"]["quality"],
						target=path_resized_image
					):
						path = path_resized_image
				base64_image = encode_image(path)
				mime_type, _ = mimetypes.guess_type(path)
				images.append({
					"type": "image_url",
					"image_url": {
						"url": f"data:{mime_type};base64,{base64_image}"
					}
				})
			elif imageFile.type == ImageFileTypes.DOCUMENT_LOCAL:
				images.append({
					"type": "input_file",
					"file_path": path,
					"filename": imageFile.name,
				})
			else:
				raise ValueError(f"Invalid image type for {path}")
		return images

	def getAudioContent(self, pathList=None, prompt=None):
		"""Build input_audio content for audio-capable models."""
		pathList = pathList or self.audioPathList
		if not pathList:
			return []
		ext_to_format = {".wav": "wav", ".mp3": "mp3", ".m4a": "m4a", ".webm": "webm", ".mp4": "mp4"}
		content = []
		if prompt:
			content.append({"type": "text", "text": prompt})
		for path in pathList:
			path_str = path if isinstance(path, str) else getattr(path, "path", str(path))
			if not os.path.exists(path_str):
				continue
			ext = os.path.splitext(path_str)[1].lower()
			fmt = AUDIO_EXT_TO_FORMAT.get(ext, "wav")
			with open(path_str, "rb") as f:
				data_b64 = base64.b64encode(f.read()).decode("utf-8")
			content.append({
				"type": "input_audio",
				"input_audio": {"data": data_b64, "format": fmt}
			})
		return content

	def getMessages(
		self,
		messages: list
	):
		block = self.firstBlock
		while block:
			userContent = []
			if block.pathList or getattr(block, "audioPathList", None):
				if block.prompt:
					userContent.append({"type": "text", "text": block.prompt})
				if block.pathList:
					userContent.extend(self.getImages(block.pathList, prompt=None))
				if getattr(block, "audioPathList", None):
					tlist = getattr(block, "audioTranscriptList", None)
					if tlist is not None and len(tlist) == len(block.audioPathList) and any(t for t in tlist):
						for t in tlist:
							if t:
								userContent.append({"type": "text", "text": t})
					else:
						userContent.extend(self.getAudioContent(block.audioPathList, prompt=None))
			elif block.prompt:
				userContent = block.prompt
			if userContent:
				messages.append({
					"role": "user",
					"content": userContent
				})
			if block.responseText:
				messages.append({
					"role": "assistant",
					"content": block.responseText
				})
			block = block.next

	def onSetFocus(self, evt):
		global activeChatDlg
		activeChatDlg = self
		self.lastFocusedItem = evt.GetEventObject()
		evt.Skip()

	def focusHistoryBrl(self, force=False):
		if (
			not force
			and not self.conf["chatFeedback"]["brailleAutoFocusHistory"]
		):
			return
		if (
			self.historyObj
			and self.foregroundObj is api.getForegroundObject()
		):
			if api.getNavigatorObject() is not self.historyObj:
				api.setNavigatorObject(self.historyObj)
			braille.handler.handleUpdate(self.historyObj)
			braille.handler.handleReviewMove(True)

	def canAutoReadStreamingResponse(self) -> bool:
		"""Return True when streamed response speech can be auto-read.

		Allowed only when this dialog is foreground and focus is inside the
		dialog but not in the history/messages field.
		"""
		try:
			if not self.IsShown():
				return False
		except Exception:
			return False
		try:
			active = wx.GetActiveWindow()
		except Exception:
			active = None
		if active is not self:
			return False
		try:
			focus = wx.Window.FindFocus()
		except Exception:
			focus = None
		if focus is None:
			return False
		if focus is self.messagesTextCtrl:
			return False
		try:
			return wx.GetTopLevelParent(focus) is self
		except Exception:
			return False

	def message(
		self,
		msg: str,
		speechOnly: bool = False,
		onPromptFieldOnly: bool = False
	):
		if not msg:
			return
		if onPromptFieldOnly and self.lastFocusedItem is not self.promptTextCtrl:
			return
		if (
			not onPromptFieldOnly
			or (
				onPromptFieldOnly
				and self.conf["chatFeedback"]["speechResponseReceived"]
			)
		):
			queueHandler.queueFunction(queueHandler.eventQueue, speech.speakMessage, msg)
		if not speechOnly:
			queueHandler.queueFunction(queueHandler.eventQueue, braille.handler.message, msg)
		if onPromptFieldOnly:
			self.focusHistoryBrl()

	def _resolveDictationConfig(self):
		model = None
		account = None
		try:
			model = self.getCurrentModel()
		except Exception:
			model = None
		try:
			account = self.getCurrentAccount()
		except Exception:
			account = None
		use_direct = bool(getattr(model, "audioInput", False))
		transcription_provider = get_transcription_provider(self.conf["audio"])
		transcription_account_id = None
		transcription_model = None
		if not use_direct:
			if transcription_provider == "openai":
				transcription_account_id = self.conf["audio"].get("openaiTranscriptionAccountId", "").strip()
				if not transcription_account_id and account and account.get("provider") == "OpenAI":
					transcription_account_id = account.get("id")
				model_id = getattr(model, "id", "")
				if (
					model
					and getattr(model, "provider", "") == "OpenAI"
					and isinstance(model_id, str)
					and (model_id == "whisper-1" or "transcribe" in model_id.lower())
				):
					transcription_model = model_id
			elif transcription_provider == "mistral":
				transcription_account_id = self.conf["audio"].get("mistralTranscriptionAccountId", "").strip()
				if not transcription_account_id and account and account.get("provider") == "MistralAI":
					transcription_account_id = account.get("id")
				model_id = getattr(model, "id", "")
				if (
					model
					and getattr(model, "provider", "") == "MistralAI"
					and isinstance(model_id, str)
					and ("voxtral" in model_id.lower() or "transcribe" in model_id.lower())
				):
					transcription_model = model_id
		return {
			"use_direct": use_direct,
			"transcription_provider": transcription_provider,
			"transcription_account_id": transcription_account_id,
			"transcription_model": transcription_model,
		}

	def onRecord(self, evt):
		if self.worker:
			self.onStopRecord(evt)
			return
		cfg = self._resolveDictationConfig()
		self.disableControls()
		self.worker = RecordThread(
			self.client,
			self,
			conf=self.conf["audio"],
			responseFormat="json",
			useDirectAudio=cfg["use_direct"],
			transcriptionProvider=cfg["transcription_provider"],
			transcriptionAccountId=cfg["transcription_account_id"],
			transcriptionModel=cfg["transcription_model"],
		)
		self.worker.start()

	def onProviderTools(self, evt):
		show_tools_menu(self, self.toolsBtn)

	def onStopRecord(self, evt):
		self.disableControls()
		if self.worker:
			self.worker.stop()
			self.worker = None
		self.enableControls()

	def disableControls(self):
		self.submitBtn.Disable()
		self.closeBtn.Disable()
		self.toolsBtn.Disable()
		self.accountListCtrl.Disable()
		self.modelsListCtrl.Disable()
		self.reasoningModeCheckBox.Disable()
		self.reasoningEffortChoice.Disable()
		self.adaptiveThinkingCheckBox.Disable()
		self.webSearchCheckBox.Disable()
		self.maxTokensSpinCtrl.Disable()
		self.renameConversationBtn.Disable()
		self.newConversationBtn.Disable()
		self.conversationListBtn.Disable()
		self.saveConversationBtn.Disable()
		self.promptTextCtrl.SetEditable(False)
		self.systemTextCtrl.SetEditable(False)
		self.imagesListCtrl.Disable()
		self.audioListCtrl.Disable()
		if self.conf["advancedMode"]:
			self.temperatureSpinCtrl.Disable()
			self.topPSpinCtrl.Disable()
			self.streamModeCheckBox.Disable()
			self.debugModeCheckBox.Disable()

	def enableControls(self):
		self.submitBtn.Enable()
		self.closeBtn.Enable()
		self.toolsBtn.Enable()
		self.accountListCtrl.Enable()
		self.modelsListCtrl.Enable()
		try:
			model = self.getCurrentModel()
			if model:
				if model.reasoning:
					self.reasoningModeCheckBox.Enable()
					reasoning_on = self.reasoningModeCheckBox.IsChecked()
					if model.reasoning_effort_options and reasoning_on:
						self.reasoningEffortChoice.Enable()
					if model.adaptive_choice_visible and reasoning_on:
						self.adaptiveThinkingCheckBox.Enable()
				if model.supports_web_search:
					self.webSearchCheckBox.Enable()
		except (IndexError, TypeError):
			pass
		self.maxTokensSpinCtrl.Enable()
		self.renameConversationBtn.Enable()
		self.newConversationBtn.Enable()
		self.conversationListBtn.Enable()
		self.saveConversationBtn.Enable()
		self.promptTextCtrl.SetEditable(True)
		self.systemTextCtrl.SetEditable(True)
		self.imagesListCtrl.Enable()
		self.audioListCtrl.Enable()
		if self.conf["advancedMode"]:
			self.temperatureSpinCtrl.Enable()
			self.topPSpinCtrl.Enable()
			self.streamModeCheckBox.Enable()
			self.debugModeCheckBox.Enable()
		self.updateImageList(False)


# Backward compatibility alias for older imports/extensions.
OpenAIDlg = AIHubDlg
