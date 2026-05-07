import os
import addonHandler
import config
import globalPluginHandler
import gui
from logHandler import log
from scriptHandler import script
from . import apikeymanager
from . import configspec
from .apiclient import OpenAIClient
from .consts import ADDON_DIR, BASE_URLs, DATA_DIR
from .plugin_mixins import AskRecordingMixin, DialogSessionMixin, MenuMixin
from .settings_dialog import SettingsDlg

addonHandler.initTranslation()
ROOT_ADDON_DIR = "\\".join(ADDON_DIR.split(os.sep)[:-2])
ADDON_INFO = addonHandler.Addon(ROOT_ADDON_DIR).manifest
conf = config.conf["AIHub"]


class GlobalPlugin(MenuMixin, DialogSessionMixin, AskRecordingMixin, globalPluginHandler.GlobalPlugin):
	scriptCategory = "AI-Hub"

	def __init__(self):
		super().__init__()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(SettingsDlg)
		self._openMainDialogs = []
		self.recordThread = None
		self.askRecordThread = None
		self._askAudioPlaying = False
		self.createMenu()
		apikeymanager.load(DATA_DIR)
		log.info("AI-Hub initialized. Version: %s. %d providers", ADDON_INFO["version"], len(apikeymanager._managers or []))

	def terminate(self):
		from .consts import cleanup_temp_dir
		from .ask_question import mci_stop_ask_audio
		if self.recordThread:
			try:
				self.recordThread.stop()
			except Exception:
				log.warning("Failed to stop record thread during terminate", exc_info=True)
			self.recordThread = None
		if self.askRecordThread:
			try:
				self.askRecordThread.stop()
			except Exception:
				log.warning("Failed to stop ask record thread during terminate", exc_info=True)
			self.askRecordThread = None
		if self._askAudioPlaying:
			mci_stop_ask_audio()
			self._askAudioPlaying = False
		cleanup_temp_dir()
		if SettingsDlg in gui.settingsDialogs.NVDASettingsDialog.categoryClasses:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(SettingsDlg)
		if getattr(self, "submenu_item", None):
			gui.mainFrame.sysTrayIcon.menu.DestroyItem(self.submenu_item)
		super().terminate()

	def getClient(self):
		if conf["renewClient"]:
			conf["renewClient"] = False
		for provider in apikeymanager.AVAILABLE_PROVIDERS:
			manager = apikeymanager.get(provider)
			if not manager.isReady():
				continue
			api_key = manager.get_api_key()
			base_url = manager.get_base_url() or BASE_URLs[manager.provider]
			if provider not in ("CustomOpenAI", "Ollama") and (not api_key or not api_key.strip()):
				return None
			organization = manager.get_api_key(use_org=True)
			org_val = organization.split(":=", 1)[1] if organization and organization.count(":=") == 1 else None
			return OpenAIClient(api_key=api_key, base_url=base_url, organization=org_val)
		return None

	@script(
		gesture="kb:nvda+g",
		description=_("Show AI-Hub dialog")
	)
	def script_showMainDialog(self, gesture):
		return DialogSessionMixin.script_showMainDialog(self, gesture)

	@script(
		gesture="kb:nvda+e",
		description=_("Take a screenshot and describe it")
	)
	def script_recognizeScreen(self, gesture):
		return DialogSessionMixin.script_recognizeScreen(self, gesture)

	@script(
		gesture="kb:nvda+o",
		description=_("Grab the current navigator object and describe it")
	)
	def script_recognizeObject(self, gesture):
		return DialogSessionMixin.script_recognizeObject(self, gesture)

	@script(
		description=_("Manage saved conversations")
	)
	def script_showConversationsManager(self, gesture):
		return MenuMixin.script_showConversationsManager(self, gesture)

	@script(
		description=_("Ask a question via voice: record, send to AI, and play the response")
	)
	def script_askQuestion(self, gesture):
		return AskRecordingMixin.script_askQuestion(self, gesture)

	@script(
		description=_("Toggle the microphone recording and transcribe the audio from anywhere")
	)
	def script_toggleRecording(self, gesture):
		return AskRecordingMixin.script_toggleRecording(self, gesture)
