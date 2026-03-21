# coding: UTF-8
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
	scriptCategory = "AI Hub"

	def __init__(self):
		super().__init__()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(SettingsDlg)
		self.client = None
		self._openMainDialogs = []
		self.recordThread = None
		self.askRecordThread = None
		self._askAudioPlaying = False
		self.createMenu()
		apikeymanager.load(DATA_DIR)
		log.info("AI Hub initialized. Version: %s. %d providers", ADDON_INFO["version"], len(apikeymanager._managers or []))

	def terminate(self):
		from .consts import cleanup_temp_dir
		cleanup_temp_dir()
		if SettingsDlg in gui.settingsDialogs.NVDASettingsDialog.categoryClasses:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(SettingsDlg)
		if getattr(self, "submenu_item", None):
			gui.mainFrame.sysTrayIcon.menu.DestroyItem(self.submenu_item)
		super().terminate()

	def getClient(self):
		if conf["renewClient"]:
			self.client = None
			conf["renewClient"] = False
		if self.client:
			return self.client
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
			self.client = OpenAIClient(api_key=api_key, base_url=base_url, organization=org_val)
			return self.client
		return None

	@script(
		gesture="kb:nvda+g",
		description=_("Show AI Hub dialog")
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
