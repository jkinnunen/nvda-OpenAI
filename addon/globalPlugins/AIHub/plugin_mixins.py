# coding: UTF-8
"""Mixins used by GlobalPlugin to keep __init__.py focused."""

import os
import time

import addonHandler
import api
import config
import gui
import ui
import wx
from scriptHandler import script

from . import apikeymanager
from .ask_question import AskQuestionThread, mci_stop_ask_audio
from .consts import ADDON_DIR, TEMP_DIR, ensure_temp_dir
from .imagehelper import save_screenshot
from .model import getModels
from .recordthread import RecordThread
from .toolsmenu import append_tools_submenu

addonHandler.initTranslation()

ROOT_ADDON_DIR = "\\".join(ADDON_DIR.split(os.sep)[:-2])
ADDON_INFO = addonHandler.Addon(ROOT_ADDON_DIR).manifest
NO_AUTHENTICATION_KEY_PROVIDED_MSG = _(
	"No API key provided for any provider, please provide at least one API key in the settings dialog"
)
conf = config.conf["AIHub"]


class MenuMixin:
	def createMenu(self):
		self.submenu = wx.Menu()
		item = self.submenu.Append(wx.ID_ANY, _("Docu&mentation"), _("Open the documentation of this addon"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onDocumentation, item)
		item = self.submenu.Append(wx.ID_ANY, _("Main d&ialog..."), _("Show the AI Hub dialog"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onShowMainDialog, item)
		item = self.submenu.Append(wx.ID_ANY, _("Conversation &history..."), _("Manage saved conversations"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onShowConversationsManager, item)
		append_tools_submenu(self.submenu, parent=None, plugin=self)

		self.submenu.AppendSeparator()

		item = self.submenu.Append(wx.ID_ANY, _("Git&Hub repository"), _("Open the GitHub repository of this addon"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onGitRepo, item)

		self.submenu.AppendSeparator()

		item = self.submenu.Append(wx.ID_ANY, _("BasiliskLLM"), _("Open the BasiliskLLM website"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onBasiliskLLM, item)

		self.submenu_item = gui.mainFrame.sysTrayIcon.menu.InsertMenu(
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
		from .conversationdlg import show_conversations_manager
		wx.CallAfter(show_conversations_manager, self)

	@script(
		description=_("Manage saved conversations")
	)
	def script_showConversationsManager(self, gesture):
		self.onShowConversationsManager(None)


class DialogSessionMixin:
	def _showNoAccountConfiguredDialog(self):
		wx.MessageBox(
			_("No account is configured yet. Please add a first account in AI Hub settings."),
			"OpenAI",
			wx.OK | wx.ICON_ERROR,
		)

	def _openMainDialog(self, pathList=None, conversationData=None, forceNew=False):
		"""Create and show a non-modal main dialog instance."""
		from . import maindialog
		client = self.getClient()
		if not client:
			self._showNoAccountConfiguredDialog()
			return

		# Drop stale references first.
		self._openMainDialogs = [d for d in getattr(self, "_openMainDialogs", []) if d and d.IsShown()]
		if not forceNew and self._openMainDialogs:
			dlg = self._openMainDialogs[-1]
			dlg.Raise()
			dlg.SetFocus()
			return

		dlg = maindialog.AIHubDlg(
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
		# Keep multiple windows visible instead of perfectly stacking them.
		if len(self._openMainDialogs) > 1:
			last = self._openMainDialogs[-2]
			try:
				x, y = last.GetPosition()
				offset = 26
				dlg.SetPosition((x + offset, y + offset))
			except Exception:
				pass
		dlg.Raise()

	def onShowMainDialog(self, evt=None, forceNew=False):
		if not self.getClient():
			self._showNoAccountConfiguredDialog()
			return
		wx.CallAfter(self._openMainDialog, None, None, forceNew)

	@script(
		gesture="kb:nvda+g",
		description=_("Show AI Hub dialog")
	)
	def script_showMainDialog(self, gesture):
		# Always open a new window on NVDA+G.
		wx.CallAfter(self.onShowMainDialog, None, True)

	def startChatSession(self, pathList):
		from . import maindialog
		instance = None
		if maindialog.addToSession and isinstance(maindialog.addToSession, maindialog.AIHubDlg):
			instance = maindialog.addToSession
		elif maindialog.activeChatDlg and isinstance(maindialog.activeChatDlg, maindialog.AIHubDlg):
			instance = maindialog.activeChatDlg
		if instance:
			if not instance.pathList:
				instance.pathList = []
			instance.addImageToList(pathList, True)
			instance.updateImageList()
			instance.SetFocus()
			instance.Raise()
			api.processPendingEvents()
			ui.message(_("Image added to an existing session"))
			return
		wx.CallAfter(self._openMainDialog, [pathList], None, False)

	@script(
		gesture="kb:nvda+e",
		description=_("Take a screenshot and describe it")
	)
	def script_recognizeScreen(self, gesture):
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

	@script(
		gesture="kb:nvda+o",
		description=_("Grab the current navigator object and describe it")
	)
	def script_recognizeObject(self, gesture):
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
		if not question or not question.strip():
			return
		question = question.strip()
		from . import maindialog
		dlg = maindialog.activeChatDlg
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
		client = self.getClient()
		if not client:
			ui.message(NO_AUTHENTICATION_KEY_PROVIDED_MSG)
			return
		AskQuestionThread(client, conf=conf, audio_path=path, plugin=self).start()

	def _useDirectAudioForAsk(self, model=None):
		return bool(model and getattr(model, "audioInput", False))

	@script(
		description=_("Ask a question via voice: record, send to AI, and play the response")
	)
	def script_askQuestion(self, gesture):
		from . import maindialog
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

		dlg = maindialog.activeChatDlg
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

	@script(
		description=_("Toggle the microphone recording and transcribe the audio from anywhere")
	)
	def script_toggleRecording(self, gesture):
		if not self.getClient():
			return ui.message(NO_AUTHENTICATION_KEY_PROVIDED_MSG)
		if self.recordThread:
			self.recordThread.stop()
			self.recordThread = None
			return
		self.recordThread = RecordThread(self.getClient(), conf=conf["audio"])
		self.recordThread.start()
