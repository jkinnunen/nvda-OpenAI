"""Mixins used by GlobalPlugin to keep __init__.py focused.

NVDA @script decorators are applied only on GlobalPlugin (__init__.py), not here,
so each gesture is registered once.
"""

import ctypes
import os
import time

import addonHandler
import api
import config
import gui
import ui
import wx
from logHandler import log

from . import apikeymanager
from .consts import ADDON_DIR, TEMP_DIR, ensure_temp_dir

addonHandler.initTranslation()

ROOT_ADDON_DIR = "\\".join(ADDON_DIR.split(os.sep)[:-2])
ADDON_INFO = addonHandler.Addon(ROOT_ADDON_DIR).manifest
NO_AUTHENTICATION_KEY_PROVIDED_MSG = _(
	"No API key provided for any provider, please provide at least one API key in the settings dialog"
)
conf = config.conf["AIHub"]


class MenuMixin:
	def createMenu(self):
		from .toolsmenu import append_tools_submenu

		self.submenu = wx.Menu()
		tray_menu = gui.mainFrame.sysTrayIcon
		for title, help_text, handler in (
			(_("Docu&mentation"), _("Open the documentation of this addon"), self.onDocumentation),
			(_("API &accounts..."), _("Manage API keys and provider accounts"), self.onManageApiAccounts),
			(_("&Conversation..."), _("Show or focus the AI-Hub conversation window"), self.onShowMainDialog),
			(_("Conversation &history..."), _("Manage saved conversations"), self.onShowConversationsManager),
		):
			item = self.submenu.Append(wx.ID_ANY, title, help_text)
			tray_menu.Bind(wx.EVT_MENU, handler, item)
		append_tools_submenu(self.submenu, parent=None, plugin=self)

		self.submenu.AppendSeparator()

		item = self.submenu.Append(wx.ID_ANY, _("Git&Hub repository"), _("Open the GitHub repository of this addon"))
		tray_menu.Bind(wx.EVT_MENU, self.onGitRepo, item)

		self.submenu.AppendSeparator()

		item = self.submenu.Append(wx.ID_ANY, _("BasiliskLLM"), _("Open the BasiliskLLM website"))
		tray_menu.Bind(wx.EVT_MENU, self.onBasiliskLLM, item)

		self.submenu_item = tray_menu.menu.InsertMenu(
			2,
			wx.ID_ANY,
			_("AI &Hub {addon_version}".format(addon_version=ADDON_INFO["version"])),
			self.submenu
		)

	def onGitRepo(self, evt):
		os.startfile("https://github.com/aaclause/nvda-OpenAI/")

	def onDocumentation(self, evt):
		import languageHandler
		languages = ["en"]
		language = languageHandler.getLanguage()
		if "_" in language:
			languages.insert(0, language.split("_")[0])
		languages.insert(0, language)
		for lang in languages:
			fp = os.path.join(ROOT_ADDON_DIR, "doc", lang, "readme.html")
			if os.path.exists(fp):
				os.startfile(fp)
				break

	def onBasiliskLLM(self, evt):
		os.startfile("https://github.com/SigmaNight/basiliskLLM/")

	def onShowConversationsManager(self, evt):
		from .conversations_manager_dialog import show_conversations_manager
		wx.CallAfter(show_conversations_manager, self)

	def onManageApiAccounts(self, evt):
		from .accounts_dialog import show_accounts_management
		show_accounts_management(gui.mainFrame)

	def script_showConversationsManager(self, gesture):
		self.onShowConversationsManager(None)


class DialogSessionMixin:
	def _showNoAccountConfiguredDialog(self):
		wx.MessageBox(
			_("No account is configured yet. Use API accounts from the AI Hub menu or NVDA Preferences → AI-Hub."),
			"OpenAI",
			wx.OK | wx.ICON_ERROR,
		)

	def _refocusHubWindow(self, dlg):
		"""Bring the AI-Hub window to the foreground (used after NVDA+G and history open)."""
		try:
			dlg.Raise()
			dlg.Show(True)
			dlg.SetFocus()
			api.processPendingEvents()
			hwnd = dlg.GetHandle()
			if hwnd:
				ctypes.windll.user32.SetForegroundWindow(int(hwnd))
		except Exception:
			log.debug("Refocus AI-Hub window failed", exc_info=True)

	def _openMainDialog(self, pathList=None, conversationData=None, forceNew=False, openConversationInNewTab=False):
		"""Create and show a non-modal conversation window."""
		from . import conversation_dialog
		client = self.getClient()
		if not client:
			self._showNoAccountConfiguredDialog()
			return

		self._openMainDialogs = [d for d in getattr(self, "_openMainDialogs", []) if d and d.IsShown()]
		if forceNew and self._openMainDialogs:
			dlg = self._openMainDialogs[-1]
			if hasattr(dlg, "_addConversationTab"):
				dlg._addConversationTab()
				wx.CallAfter(dlg.promptTextCtrl.SetFocus)
			self._refocusHubWindow(dlg)
			return
		if not forceNew and self._openMainDialogs:
			dlg = self._openMainDialogs[-1]
			if conversationData and hasattr(dlg, "_loadConversation"):
				if openConversationInNewTab and hasattr(dlg, "_openConversationFromHistory"):
					dlg._openConversationFromHistory(conversationData)
				else:
					dlg._loadConversation(conversationData, focus_message_history=True)
			self._refocusHubWindow(dlg)
			return

		dlg = conversation_dialog.ConversationDialog(
			gui.mainFrame,
			client=client,
			conf=conf,
			pathList=pathList,
			plugin=self,
			conversationData=conversationData
		)
		self._openMainDialogs.append(dlg)

		def _on_close(evt, dialog=dlg):
			try:
				if dialog in self._openMainDialogs:
					self._openMainDialogs.remove(dialog)
			except Exception:
				pass
			evt.Skip()

		dlg.Bind(wx.EVT_CLOSE, _on_close)
		dlg.Show()
		if len(self._openMainDialogs) > 1:
			last = self._openMainDialogs[-2]
			try:
				x, y = last.GetPosition()
				offset = 26
				dlg.SetPosition((x + offset, y + offset))
			except Exception:
				log.debug("Failed to offset stacked dialog position", exc_info=True)
		self._refocusHubWindow(dlg)

	def onShowMainDialog(self, evt=None, forceNew=False):
		if not self.getClient():
			self._showNoAccountConfiguredDialog()
			return
		wx.CallAfter(self._openMainDialog, None, None, forceNew)

	def script_showMainDialog(self, gesture):
		wx.CallAfter(self.onShowMainDialog, None, False)

	def startChatSession(self, pathList):
		from . import conversation_dialog
		instance = None
		if conversation_dialog.addToSession and isinstance(conversation_dialog.addToSession, conversation_dialog.ConversationDialog):
			instance = conversation_dialog.addToSession
		elif conversation_dialog.activeChatDlg and isinstance(conversation_dialog.activeChatDlg, conversation_dialog.ConversationDialog):
			instance = conversation_dialog.activeChatDlg
		if instance:
			page = instance.get_active_page()
			if not page.pathList:
				page.pathList = []
			instance.addImageToList(pathList, True)
			instance.updateImageList()
			instance.SetFocus()
			instance.Raise()
			api.processPendingEvents()
			ui.message(_("Image added to an existing session"))
			return
		wx.CallAfter(self._openMainDialog, [pathList], None, False)

	def script_recognizeScreen(self, gesture):
		from .imagehelper import save_screenshot

		if not self.getClient():
			return ui.message(NO_AUTHENTICATION_KEY_PROVIDED_MSG)
		now = time.strftime("%Y-%m-%d_-_%H:%M:%S")
		ensure_temp_dir()
		tmpPath = os.path.join(TEMP_DIR, f"screen_{now}.png".replace(":", ""))
		if os.path.exists(tmpPath):
			return
		if not save_screenshot(tmpPath):
			return ui.message(_("Failed to capture screenshot"))
		name = _("Screenshot %s") % (now.split("_-_")[-1])
		self.startChatSession((tmpPath, name))

	def script_recognizeObject(self, gesture):
		from .imagehelper import save_screenshot

		if not self.getClient():
			return ui.message(NO_AUTHENTICATION_KEY_PROVIDED_MSG)
		now = time.strftime("%Y-%m-%d_-_%H:%M:%S")
		ensure_temp_dir()
		tmpPath = os.path.join(TEMP_DIR, f"object_{now}.png".replace(":", ""))
		if os.path.exists(tmpPath):
			return
		nav = api.getNavigatorObject()
		nav.scrollIntoView()
		location = nav.location
		bbox = (location.left, location.top, location.left + location.width, location.top + location.height)
		if not save_screenshot(tmpPath, bbox=bbox):
			return ui.message(_("Failed to capture object region"))
		default_name = _("Navigator Object %s") % (now.split("_-_")[-1])
		name = nav.name
		if (not name or not name.strip() or "\n" in name or len(name) > 80):
			name = default_name
		else:
			name = "%s (%s)" % (name.strip(), default_name)
		self.startChatSession((tmpPath, name))


class AskRecordingMixin:
	def _onAskQuestionTranscription(self, question):
		from .ask_question import AskQuestionThread

		if not question or not question.strip():
			return
		question = question.strip()
		from . import conversation_dialog
		dlg = conversation_dialog.activeChatDlg
		if dlg:
			dlg._askPromptOverride = question
			if dlg.worker:
				dlg._askQuestionDeferred = True
			else:
				wx.CallAfter(dlg.onSubmit, None)
			return
		client = self.getClient()
		if not client:
			ui.message(NO_AUTHENTICATION_KEY_PROVIDED_MSG)
			return
		AskQuestionThread(client, question=question, conf=conf, plugin=self).start()

	def _onAskQuestionAudio(self, path):
		from .ask_question import AskQuestionThread

		client = self.getClient()
		if not client:
			ui.message(NO_AUTHENTICATION_KEY_PROVIDED_MSG)
			return
		AskQuestionThread(client, conf=conf, audio_path=path, plugin=self).start()

	def _useDirectAudioForAsk(self, model=None):
		return bool(model and getattr(model, "audioInput", False))

	def script_askQuestion(self, gesture):
		from .ask_question import AskQuestionThread, mci_stop_ask_audio
		from .model import getModels
		from .recordthread import RecordThread
		from . import conversation_dialog

		if not self.getClient():
			return ui.message(NO_AUTHENTICATION_KEY_PROVIDED_MSG)
		if self._askAudioPlaying:
			mci_stop_ask_audio()
			self._askAudioPlaying = False
			ui.message(_("Audio stopped"))
			return
		if self.askRecordThread:
			self.askRecordThread.stop()
			self.askRecordThread = None
			return

		dlg = conversation_dialog.activeChatDlg
		if dlg:
			model = dlg.getCurrentModel()
			if model and self._useDirectAudioForAsk(model):
				dlg._askQuestionPending = True
				ui.message(_("Recording question (direct audio)"))
				self.askRecordThread = RecordThread(
					self.getClient(),
					notifyWindow=dlg,
					conf=conf["audio"],
					useDirectAudio=True,
				)
			else:
				ui.message(_("Recording question"))
				self.askRecordThread = RecordThread(
					self.getClient(),
					conf=conf["audio"],
					onTranscription=self._onAskQuestionTranscription,
				)
			self.askRecordThread.start()
			return

		for provider in apikeymanager.AVAILABLE_PROVIDERS:
			if not apikeymanager.get(provider).isReady():
				continue
			try:
				for model in getModels(provider):
					if getattr(model, "audioInput", False):
						ui.message(_("Recording question (direct audio)"))
						self.askRecordThread = RecordThread(
							self.getClient(),
							conf=conf["audio"],
							useDirectAudio=True,
							onAudioPath=self._onAskQuestionAudio,
						)
						self.askRecordThread.start()
						return
			except Exception:
				pass

		ui.message(_("Recording question"))
		self.askRecordThread = RecordThread(
			self.getClient(),
			conf=conf["audio"],
			onTranscription=self._onAskQuestionTranscription,
		)
		self.askRecordThread.start()

	def script_toggleRecording(self, gesture):
		from .recordthread import RecordThread

		if not self.getClient():
			return ui.message(NO_AUTHENTICATION_KEY_PROVIDED_MSG)
		if self.recordThread:
			self.recordThread.stop()
			self.recordThread = None
			return
		self.recordThread = RecordThread(self.getClient(), conf=conf["audio"])
		self.recordThread.start()
