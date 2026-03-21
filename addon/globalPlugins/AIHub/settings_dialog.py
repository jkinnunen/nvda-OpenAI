# coding: UTF-8
"""Addon settings dialogs and account editor."""

import addonHandler
import config
import gui
import re
import wx

from . import apikeymanager
from .consts import (
	TTS_MODELS,
	TTS_VOICES,
	TRANSCRIPTION_PROVIDERS,
	BASE_URLs,
)
from .providertools_helpers import add_labeled_factory

addonHandler.initTranslation()

conf = config.conf["AIHub"]


class AccountDialog(wx.Dialog):
	def __init__(self, parent, title, account=None):
		super().__init__(parent, title=title)
		self.account = account or {}
		self._buildUI()
		self.CenterOnParent()
		self.SetSize((620, 470))

	def _buildUI(self):
		panel = wx.Panel(self)
		rootSizer = wx.BoxSizer(wx.VERTICAL)
		formPanel = wx.Panel(panel)
		formSizer = wx.BoxSizer(wx.VERTICAL)

		self.providerChoice = add_labeled_factory(
			formPanel,
			formSizer,
			_("&Provider:"),
			lambda: wx.Choice(formPanel, choices=apikeymanager.AVAILABLE_PROVIDERS),
		)
		provider = self.account.get("provider", apikeymanager.AVAILABLE_PROVIDERS[0])
		self.providerChoice.SetSelection(
			apikeymanager.AVAILABLE_PROVIDERS.index(provider) if provider in apikeymanager.AVAILABLE_PROVIDERS else 0
		)
		self.nameText = add_labeled_factory(
			formPanel,
			formSizer,
			_("Account &name:"),
			lambda: wx.TextCtrl(formPanel, value=self.account.get("name", "")),
		)
		self.apiKeyText = add_labeled_factory(
			formPanel,
			formSizer,
			_("&API key:"),
			lambda: wx.TextCtrl(formPanel, value=self.account.get("api_key", "")),
		)
		self.customBaseUrlText = add_labeled_factory(
			formPanel,
			formSizer,
			_("Custom base &URL:"),
			lambda: wx.TextCtrl(formPanel, value=self.account.get("base_url", "")),
		)
		self.customBaseUrlText.SetToolTip(_("Custom OpenAI-compatible endpoint. Include /v1 according to your server."))
		self.orgNameText = add_labeled_factory(
			formPanel,
			formSizer,
			_("Organization &name:"),
			lambda: wx.TextCtrl(formPanel, value=self.account.get("org_name", "")),
		)
		self.orgKeyText = add_labeled_factory(
			formPanel,
			formSizer,
			_("Organization &key:"),
			lambda: wx.TextCtrl(formPanel, value=self.account.get("org_key", "")),
		)
		self.providerChoice.Bind(wx.EVT_CHOICE, self.onProviderChoice)
		formPanel.SetSizer(formSizer)

		btnsizer = wx.StdDialogButtonSizer()
		btnOK = wx.Button(panel, wx.ID_OK)
		btnOK.SetDefault()
		btnsizer.AddButton(btnOK)
		btnsizer.AddButton(wx.Button(panel, wx.ID_CANCEL))
		btnsizer.Realize()

		rootSizer.Add(formPanel, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
		rootSizer.Add(btnsizer, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
		panel.SetSizer(rootSizer)
		self.onProviderChoice(None)
		self.providerChoice.SetFocus()

	def onProviderChoice(self, evt):
		provider = self.providerChoice.GetStringSelection()
		uses_custom_url = provider in ("CustomOpenAI", "Ollama")
		self.customBaseUrlText.Enable(uses_custom_url)
		self.orgNameText.Enable(provider not in ("CustomOpenAI", "Ollama"))
		self.orgKeyText.Enable(provider not in ("CustomOpenAI", "Ollama"))
		if provider == "Ollama" and not self.customBaseUrlText.GetValue().strip():
			self.customBaseUrlText.SetValue(BASE_URLs.get("Ollama", "http://127.0.0.1:11434/v1"))

	def _normalize_custom_base_url(self, value: str) -> str:
		url = (value or "").strip()
		if not url:
			return ""
		if not re.match(r"^[a-zA-Z][a-zA-Z0-9+\-.]*://", url):
			url = f"http://{url}"
		return url.rstrip("/")

	def getData(self):
		provider = self.providerChoice.GetStringSelection()
		base_url = self._normalize_custom_base_url(self.customBaseUrlText.GetValue())
		if provider == "Ollama" and not base_url:
			base_url = BASE_URLs.get("Ollama", "http://127.0.0.1:11434/v1")
		return {
			"provider": provider,
			"name": self.nameText.GetValue().strip(),
			"api_key": self.apiKeyText.GetValue().strip(),
			"base_url": base_url,
			"org_name": self.orgNameText.GetValue().strip(),
			"org_key": self.orgKeyText.GetValue().strip(),
		}


class SettingsDlg(gui.settingsDialogs.SettingsPanel):
	title = "AI Hub"

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

		accountsSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=_("API Accounts"))
		accountsBox = accountsSizer.GetStaticBox()
		accountsGroup = gui.guiHelper.BoxSizerHelper(self, sizer=accountsSizer)
		self.accountsListLabel = wx.StaticText(accountsBox, label=_("&Accounts list:"))
		accountsGroup.addItem(self.accountsListLabel)
		self.accountsList = accountsGroup.addItem(wx.ListBox(accountsBox, size=(480, 140)))
		accountButtons = wx.BoxSizer(wx.HORIZONTAL)
		self.addAccountBtn = wx.Button(accountsBox, label=_("&Add account..."))
		self.editAccountBtn = wx.Button(accountsBox, label=_("&Edit account..."))
		self.removeAccountBtn = wx.Button(accountsBox, label=_("&Remove account"))
		for btn in (self.addAccountBtn, self.editAccountBtn, self.removeAccountBtn):
			accountButtons.Add(btn, 0, wx.ALL, 5)
		accountsGroup.addItem(accountButtons)
		self.addAccountBtn.Bind(wx.EVT_BUTTON, self.onAddAccount)
		self.editAccountBtn.Bind(wx.EVT_BUTTON, self.onEditAccount)
		self.removeAccountBtn.Bind(wx.EVT_BUTTON, self.onRemoveAccount)
		self._refreshAccountsUI()
		sHelper.addItem(accountsSizer)

		mainDialogSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=_("Main dialog"))
		mainDialogBox = mainDialogSizer.GetStaticBox()
		mainDialogGroup = gui.guiHelper.BoxSizerHelper(self, sizer=mainDialogSizer)

		self.blockEscape = wx.CheckBox(mainDialogBox, label=_("Block the closing using the &escape key"))
		self.blockEscape.SetValue(conf["blockEscapeKey"])
		mainDialogGroup.addItem(self.blockEscape)

		self.saveSystem = wx.CheckBox(mainDialogBox, label=_("Remember the content of the S&ystem field between sessions"))
		self.saveSystem.SetValue(conf["saveSystem"])
		mainDialogGroup.addItem(self.saveSystem)

		self.autoSaveConversation = wx.CheckBox(mainDialogBox, label=_("&Auto-save conversations after each response"))
		self.autoSaveConversation.SetValue(conf.get("autoSaveConversation", True))
		mainDialogGroup.addItem(self.autoSaveConversation)

		self.advancedMode = wx.CheckBox(
			mainDialogBox,
			label=_("Enable &advanced settings (including temperature and probability mass)")
		)
		self.advancedMode.SetValue(conf["advancedMode"])
		mainDialogGroup.addItem(self.advancedMode)
		sHelper.addItem(mainDialogSizer)

		ttsSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=_("Text To Speech"))
		ttsGroup = gui.guiHelper.BoxSizerHelper(self, sizer=ttsSizer)
		self.voiceList = ttsGroup.addLabeledControl(_("&Voice:"), wx.Choice, choices=TTS_VOICES)
		voiceIndex = TTS_VOICES.index(conf["TTSVoice"]) if conf["TTSVoice"] in TTS_VOICES else 0
		self.voiceList.SetSelection(voiceIndex)
		self.modelList = ttsGroup.addLabeledControl(_("&Model:"), wx.Choice, choices=TTS_MODELS)
		modelIndex = TTS_MODELS.index(conf["TTSModel"]) if conf["TTSModel"] in TTS_MODELS else 0
		self.modelList.SetSelection(modelIndex)
		sHelper.addItem(ttsSizer)

		imageSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=_("Image description"))
		imageBox = imageSizer.GetStaticBox()
		imageGroup = gui.guiHelper.BoxSizerHelper(self, sizer=imageSizer)
		self.resize = imageGroup.addItem(
			wx.CheckBox(imageBox, label=_("&Resize images before sending them to the API"))
		)
		self.resize.SetValue(conf["images"]["resize"])
		self.resize.Bind(wx.EVT_CHECKBOX, self.onResize)
		self.maxWidth = imageGroup.addLabeledControl(
			_("Maximum &width (0 to resize proportionally to the height):"),
			wx.SpinCtrl,
			min=0,
			max=2000
		)
		self.maxWidth.SetValue(conf["images"]["maxWidth"])
		self.maxHeight = imageGroup.addLabeledControl(
			_("Maximum &height (0 to resize proportionally to the width):"),
			wx.SpinCtrl,
			min=0,
			max=2000
		)
		self.maxHeight.SetValue(conf["images"]["maxHeight"])
		self.quality = imageGroup.addLabeledControl(
			_("&Quality for JPEG images (0 [worst] to 95 [best], values above 95 should be avoided):"),
			wx.SpinCtrl,
			min=1,
			max=100
		)
		self.quality.SetValue(conf["images"]["quality"])
		self.useCustomPrompt = imageGroup.addItem(
			wx.CheckBox(imageBox, label=_("Customize default text &prompt"))
		)
		self.useCustomPrompt.Bind(wx.EVT_CHECKBOX, self.onDefaultPrompt)
		self.useCustomPrompt.SetValue(conf["images"]["useCustomPrompt"])
		self.customPromptText = imageGroup.addLabeledControl(
			_("Default &text prompt:"),
			wxCtrlClass=wx.TextCtrl,
			style=wx.TE_MULTILINE
		)
		self.customPromptText.SetMinSize((250, -1))
		self.customPromptText.Enable(False)
		if conf["images"]["useCustomPrompt"]:
			self.useCustomPrompt.SetValue(True)
			self.customPromptText.SetValue(conf["images"]["customPromptText"])
			self.customPromptText.Enable()
		sHelper.addItem(imageSizer)

		chatFeedbackSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=_("Chat feedback"))
		chatFeedbackBox = chatFeedbackSizer.GetStaticBox()
		chatFeedbackGroup = gui.guiHelper.BoxSizerHelper(self, sizer=chatFeedbackSizer)
		self.chatFeedback = {
			"sndTaskInProgress": chatFeedbackGroup.addItem(
				wx.CheckBox(chatFeedbackBox, label=_("Play sound when a task is in progress"))
			),
			"sndResponseSent": chatFeedbackGroup.addItem(
				wx.CheckBox(chatFeedbackBox, label=_("Play sound when a response is sent"))
			),
			"sndResponsePending": chatFeedbackGroup.addItem(
				wx.CheckBox(chatFeedbackBox, label=_("Play sound when a response is pending"))
			),
			"sndResponseReceived": chatFeedbackGroup.addItem(
				wx.CheckBox(chatFeedbackBox, label=_("Play sound when a response is received"))
			),
			"brailleAutoFocusHistory": chatFeedbackGroup.addItem(
				wx.CheckBox(chatFeedbackBox, label=_("Attach braille to the history if the focus is in the prompt field"))
			),
			"speechResponseReceived": chatFeedbackGroup.addItem(
				wx.CheckBox(chatFeedbackBox, label=_("Speak response when the focus is in the prompt field"))
			),
		}
		for key, item in self.chatFeedback.items():
			item.SetValue(conf["chatFeedback"][key])
		sHelper.addItem(chatFeedbackSizer)

		recordingSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=_("Recording"))
		recordingGroup = gui.guiHelper.BoxSizerHelper(self, sizer=recordingSizer)

		providerSizer = wx.StaticBoxSizer(wx.VERTICAL, recordingSizer.GetStaticBox(), label=_("Provider"))
		providerGroup = gui.guiHelper.BoxSizerHelper(self, sizer=providerSizer)
		transcriptionChoices = [
			_("whisper.cpp (local)"),
			_("OpenAI Whisper"),
			_("Mistral Voxtral"),
		]
		self.transcriptionProviderChoice = providerGroup.addLabeledControl(
			_("Transcription &provider:"),
			wx.Choice,
			choices=transcriptionChoices,
		)
		provider = conf["audio"].get("transcriptionProvider", "openai")
		if conf["audio"]["whisper.cpp"]["enabled"]:
			provider = "whisper_cpp"
		providerIndex = list(TRANSCRIPTION_PROVIDERS).index(provider) if provider in TRANSCRIPTION_PROVIDERS else 1
		self.transcriptionProviderChoice.SetSelection(providerIndex)
		self.transcriptionProviderChoice.Bind(wx.EVT_CHOICE, self.onTranscriptionProviderChange)
		self.whisperHost = providerGroup.addLabeledControl(
			_("&Host (whisper.cpp):"),
			wx.TextCtrl,
			value=conf["audio"]["whisper.cpp"]["host"]
		)
		recordingGroup.addItem(providerSizer)

		accountsMapSizer = wx.StaticBoxSizer(
			wx.VERTICAL,
			recordingSizer.GetStaticBox(),
			label=_("Provider account mapping")
		)
		accountsMapGroup = gui.guiHelper.BoxSizerHelper(self, sizer=accountsMapSizer)
		accountsMapHint = wx.StaticText(
			accountsMapSizer.GetStaticBox(),
			label=_("Use these only when dictation must always use a specific account.")
		)
		accountsMapGroup.addItem(accountsMapHint)
		self.openaiTranscriptionAccountChoice = accountsMapGroup.addLabeledControl(
			_("OpenAI transcription account:"),
			wx.Choice,
			choices=[],
		)
		self.mistralTranscriptionAccountChoice = accountsMapGroup.addLabeledControl(
			_("Mistral transcription account:"),
			wx.Choice,
			choices=[],
		)
		self._refreshTranscriptionAccountChoices()
		recordingGroup.addItem(accountsMapSizer)

		cleanupSizer = wx.StaticBoxSizer(wx.VERTICAL, recordingSizer.GetStaticBox(), label=_("Audio preprocessing"))
		cleanupGroup = gui.guiHelper.BoxSizerHelper(self, sizer=cleanupSizer)
		self.trimSilenceCheckbox = cleanupGroup.addItem(
			wx.CheckBox(
				cleanupSizer.GetStaticBox(),
				label=_("&Trim silence (remove leading/trailing and silence > 2s)")
			)
		)
		self.trimSilenceCheckbox.SetValue(conf["audio"].get("trimSilence", True))
		self.trimSilenceCheckbox.Bind(wx.EVT_CHECKBOX, self.onTrimSilenceChange)
		self.minSilenceSec = cleanupGroup.addLabeledControl(
			_("Minimum silence &duration to remove (seconds):"),
			wx.SpinCtrl,
			min=1,
			max=10
		)
		self.minSilenceSec.SetValue(int(conf["audio"].get("minSilenceSec", 2.0)))
		self.minSilenceSec.Enable(conf["audio"].get("trimSilence", True))
		recordingGroup.addItem(cleanupSizer)

		sHelper.addItem(recordingSizer)

		self.onResize(None)
		self.onTranscriptionProviderChange(None)

	def _refreshAccountsUI(self, select_key=None):
		self._accountEntries = []
		self.accountsList.Clear()
		for provider in apikeymanager.AVAILABLE_PROVIDERS:
			manager = apikeymanager.get(provider)
			active_id = manager.get_active_account_id()
			for acc in manager.list_accounts(include_env=True):
				entry = {
					"provider": provider,
					"id": acc["id"],
					"name": acc.get("name") or _("Account"),
					"api_key": acc.get("api_key", ""),
					"base_url": acc.get("base_url", ""),
					"org_name": acc.get("org_name", ""),
					"org_key": acc.get("org_key", ""),
				}
				entry["key"] = f"{provider}/{entry['id']}"
				label = f"{provider} / {entry['name']}"
				if provider in ("CustomOpenAI", "Ollama") and entry["base_url"]:
					label = f"{label} - {entry['base_url']}"
				if entry["id"] == active_id:
					label = f"{label} ({_('default')})"
				self._accountEntries.append(entry)
				self.accountsList.Append(label)
		if self._accountEntries:
			target = select_key
			if not target:
				for i, entry in enumerate(self._accountEntries):
					manager = apikeymanager.get(entry["provider"])
					if manager.get_active_account_id() == entry["id"]:
						self.accountsList.SetSelection(i)
						break
				else:
					self.accountsList.SetSelection(0)
			else:
				for i, entry in enumerate(self._accountEntries):
					if entry["key"] == target:
						self.accountsList.SetSelection(i)
						break
				else:
					self.accountsList.SetSelection(0)
		self._refreshTranscriptionAccountChoices()

	def _buildTranscriptionAccountChoices(self, provider_name: str, configured_id: str):
		manager = apikeymanager.get(provider_name)
		active_id = manager.get_active_account_id()
		accounts = manager.list_accounts(include_env=True)
		labels = [_("Use provider active account (default)")]
		ids = [""]
		selected_idx = 0
		for acc in accounts:
			acc_id = acc.get("id", "")
			if not acc_id:
				continue
			name = acc.get("name") or _("Account")
			label = name
			if acc_id == active_id:
				label = f"{label} ({_('default')})"
			labels.append(label)
			ids.append(acc_id)
			if configured_id and acc_id == configured_id:
				selected_idx = len(ids) - 1
		return labels, ids, selected_idx

	def _refreshTranscriptionAccountChoices(self):
		if not hasattr(self, "openaiTranscriptionAccountChoice") or not hasattr(self, "mistralTranscriptionAccountChoice"):
			return
		audio_conf = conf.get("audio", {})
		openai_id = audio_conf.get("openaiTranscriptionAccountId", "")
		mistral_id = audio_conf.get("mistralTranscriptionAccountId", "")
		labels, ids, selected_idx = self._buildTranscriptionAccountChoices("OpenAI", openai_id)
		self._openaiTranscriptionAccountIds = ids
		self.openaiTranscriptionAccountChoice.SetItems(labels)
		self.openaiTranscriptionAccountChoice.SetSelection(selected_idx)
		labels, ids, selected_idx = self._buildTranscriptionAccountChoices("MistralAI", mistral_id)
		self._mistralTranscriptionAccountIds = ids
		self.mistralTranscriptionAccountChoice.SetItems(labels)
		self.mistralTranscriptionAccountChoice.SetSelection(selected_idx)

	def _getSelectedAccountEntry(self):
		idx = self.accountsList.GetSelection()
		if idx == wx.NOT_FOUND:
			return None
		if idx < 0 or idx >= len(getattr(self, "_accountEntries", [])):
			return None
		return self._accountEntries[idx]

	def onAddAccount(self, evt):
		dlg = AccountDialog(self, _("Add account"))
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return
		data = dlg.getData()
		dlg.Destroy()
		if data["provider"] == "CustomOpenAI":
			if not data["base_url"]:
				gui.messageBox(_("Custom base URL is required for CustomOpenAI accounts."), _("AI Hub"), wx.OK | wx.ICON_ERROR)
				return
		elif data["provider"] == "Ollama":
			pass
		elif not data["api_key"]:
			gui.messageBox(_("API key is required."), _("AI Hub"), wx.OK | wx.ICON_ERROR)
			return
		manager = apikeymanager.get(data["provider"])
		acc_id = manager.add_account(
			name=data["name"] or _("Account"),
			api_key=data["api_key"],
			base_url=data.get("base_url", ""),
			org_name=data["org_name"],
			org_key=data["org_key"],
			set_active=True
		)
		self._refreshAccountsUI(select_key=f"{data['provider']}/{acc_id}")

	def onEditAccount(self, evt):
		entry = self._getSelectedAccountEntry()
		if not entry:
			return
		dlg = AccountDialog(self, _("Edit account"), account=entry)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return
		updated = dlg.getData()
		dlg.Destroy()
		if updated["provider"] == "CustomOpenAI":
			if not updated["base_url"]:
				gui.messageBox(_("Custom base URL is required for CustomOpenAI accounts."), _("AI Hub"), wx.OK | wx.ICON_ERROR)
				return
		elif updated["provider"] == "Ollama":
			pass
		elif not updated["api_key"]:
			gui.messageBox(_("API key is required."), _("AI Hub"), wx.OK | wx.ICON_ERROR)
			return
		if updated["provider"] == entry["provider"]:
			manager = apikeymanager.get(entry["provider"])
			manager.update_account(
				entry["id"],
				name=updated["name"] or _("Account"),
				api_key=updated["api_key"],
				base_url=updated.get("base_url", ""),
				org_name=updated["org_name"],
				org_key=updated["org_key"]
			)
			manager.set_active_account(entry["id"])
			self._refreshAccountsUI(select_key=f"{entry['provider']}/{entry['id']}")
			return
		old_manager = apikeymanager.get(entry["provider"])
		new_manager = apikeymanager.get(updated["provider"])
		new_id = new_manager.add_account(
			name=updated["name"] or _("Account"),
			api_key=updated["api_key"],
			base_url=updated.get("base_url", ""),
			org_name=updated["org_name"],
			org_key=updated["org_key"],
			set_active=True
		)
		old_manager.remove_account(entry["id"])
		self._refreshAccountsUI(select_key=f"{updated['provider']}/{new_id}")

	def onRemoveAccount(self, evt):
		entry = self._getSelectedAccountEntry()
		if not entry:
			return
		res = gui.messageBox(
			_("Remove account %s from provider %s?") % (entry["name"], entry["provider"]),
			_("Remove account"),
			wx.YES_NO | wx.ICON_QUESTION
		)
		if res != wx.YES:
			return
		manager = apikeymanager.get(entry["provider"])
		manager.remove_account(entry["id"])
		self._refreshAccountsUI()

	def onResize(self, evt):
		self.maxWidth.Enable(self.resize.GetValue())
		self.maxHeight.Enable(self.resize.GetValue())
		self.quality.Enable(self.resize.GetValue())

	def onTranscriptionProviderChange(self, evt):
		idx = self.transcriptionProviderChoice.GetSelection()
		is_whisper_cpp = idx == 0
		is_openai = idx == 1
		is_mistral = idx == 2
		self.whisperHost.Enable(is_whisper_cpp)
		self.openaiTranscriptionAccountChoice.Enable(is_openai)
		self.mistralTranscriptionAccountChoice.Enable(is_mistral)

	def onTrimSilenceChange(self, evt):
		self.minSilenceSec.Enable(self.trimSilenceCheckbox.GetValue())

	def onWhisperCheckbox(self, evt):
		self.onTranscriptionProviderChange(None)

	def onDefaultPrompt(self, evt):
		if self.useCustomPrompt.GetValue():
			self.customPromptText.Enable()
			self.customPromptText.SetValue(conf["images"]["customPromptText"])
		else:
			self.customPromptText.Enable(False)

	def onSave(self):
		conf["blockEscapeKey"] = self.blockEscape.GetValue()
		conf["renewClient"] = True
		conf["saveSystem"] = self.saveSystem.GetValue()
		conf["autoSaveConversation"] = self.autoSaveConversation.GetValue()
		conf["advancedMode"] = self.advancedMode.GetValue()
		conf["TTSVoice"] = self.voiceList.GetString(self.voiceList.GetSelection())
		conf["TTSModel"] = self.modelList.GetString(self.modelList.GetSelection())
		conf["images"]["resize"] = self.resize.GetValue()
		conf["images"]["maxWidth"] = int(self.maxWidth.GetValue())
		conf["images"]["maxHeight"] = int(self.maxHeight.GetValue())
		conf["images"]["quality"] = int(self.quality.GetValue())
		if self.useCustomPrompt.GetValue():
			conf["images"]["useCustomPrompt"] = True
			conf["images"]["customPromptText"] = self.customPromptText.GetValue()
		else:
			conf["images"]["useCustomPrompt"] = False
		providerIndex = self.transcriptionProviderChoice.GetSelection()
		provider = TRANSCRIPTION_PROVIDERS[providerIndex]
		conf["audio"]["transcriptionProvider"] = provider
		conf["audio"]["whisper.cpp"]["enabled"] = provider == "whisper_cpp"
		conf["audio"]["whisper.cpp"]["host"] = self.whisperHost.GetValue()
		openai_idx = self.openaiTranscriptionAccountChoice.GetSelection()
		mistral_idx = self.mistralTranscriptionAccountChoice.GetSelection()
		conf["audio"]["openaiTranscriptionAccountId"] = (
			self._openaiTranscriptionAccountIds[openai_idx]
			if 0 <= openai_idx < len(getattr(self, "_openaiTranscriptionAccountIds", []))
			else ""
		)
		conf["audio"]["mistralTranscriptionAccountId"] = (
			self._mistralTranscriptionAccountIds[mistral_idx]
			if 0 <= mistral_idx < len(getattr(self, "_mistralTranscriptionAccountIds", []))
			else ""
		)
		conf["audio"]["trimSilence"] = self.trimSilenceCheckbox.GetValue()
		conf["audio"]["minSilenceSec"] = int(self.minSilenceSec.GetValue())
		for key, item in self.chatFeedback.items():
			conf["chatFeedback"][key] = item.GetValue()
