# coding: UTF-8
"""Model/account list handlers for AIHubDlg."""

import wx

import addonHandler
import gui
import ui

from . import apikeymanager
from .modeldetailsutils import build_model_details_html
from .model import clearModelCache, getModels

addonHandler.initTranslation()

MODEL_SORT_OPTIONS = {
	"created": (lambda m: getattr(m, "created", 0), True),
	"created_asc": (lambda m: getattr(m, "created", 0), False),
	"name": (lambda m: (m.name or m.id).lower(), False),
	"name_desc": (lambda m: (m.name or m.id).lower(), True),
	"context": (lambda m: m.contextWindow, True),
	"context_asc": (lambda m: m.contextWindow, False),
	"max_tokens": (lambda m: (m.maxOutputToken if m.maxOutputToken > 0 else 0), True),
	"max_tokens_asc": (lambda m: (m.maxOutputToken if m.maxOutputToken > 0 else 0), False),
}
MODEL_SORT_DEFAULT = "created"


class ModelHandlersMixin:
	def _modelKey(self, model):
		return f"{model.provider}:{model.id}"

	def _accountKey(self, account):
		return f"{account['provider'].lower()}/{account['id']}"

	def _accountLabel(self, account):
		name = account.get("name") or _("Account")
		label = f"{account['provider']} / {name}"
		if account.get("provider") in ("CustomOpenAI", "Ollama") and account.get("base_url"):
			label = f"{label} - {account['base_url']}"
		return label

	def _loadAccounts(self):
		accounts = []
		for provider in apikeymanager.AVAILABLE_PROVIDERS:
			manager = apikeymanager.get(provider)
			for acc in manager.list_accounts(include_env=True):
				if not manager.isReady(account_id=acc["id"]):
					continue
				account = {
					"provider": provider,
					"id": acc["id"],
					"name": acc.get("name") or _("Account"),
					"base_url": acc.get("base_url", ""),
				}
				account["key"] = self._accountKey(account)
				accounts.append(account)
		self._accounts = sorted(accounts, key=lambda a: (a["provider"].lower(), (a.get("name") or "").lower()))

	def getCurrentAccount(self):
		if not hasattr(self, "accountListCtrl"):
			return None
		idx = self.accountListCtrl.GetSelection()
		if idx == wx.NOT_FOUND:
			return None
		return self.accountListCtrl.GetClientData(idx)

	def _requireAccount(self, modal=False):
		account = self.getCurrentAccount()
		if account:
			return account
		msg = _("Please select an account.")
		if modal:
			gui.messageBox(msg, "OpenAI", wx.OK | wx.ICON_ERROR)
		else:
			ui.message(msg)
		return None

	def _selectAccount(self, account_key):
		if not account_key:
			return False
		account_key = account_key.lower()
		for i in range(self.accountListCtrl.GetCount()):
			acc = self.accountListCtrl.GetClientData(i)
			if acc and acc.get("key", "").lower() == account_key:
				self.accountListCtrl.SetSelection(i)
				return True
		return False

	def _refreshAccountsList(self, account_to_select=None):
		self._loadAccounts()
		self.accountListCtrl.Clear()
		for account in self._accounts:
			self.accountListCtrl.Append(self._accountLabel(account), account)
		selector = account_to_select or self.data.get("lastAccountKey")
		if not self._selectAccount(selector) and self.accountListCtrl.GetCount():
			self.accountListCtrl.SetSelection(0)

	def onAccountChange(self, evt):
		account = self.getCurrentAccount()
		if not account:
			self._models = []
			self._refreshModelsList()
			return
		if self.data.get("lastAccountKey") != account["key"]:
			self.data["lastAccountKey"] = account["key"]
			self.saveData(True)
		self._models = getModels(account["provider"], account_id=account.get("id"))
		self._refreshModelsList()
		self.onModelChange(None)

	def getCurrentModel(self):
		if not hasattr(self, "modelsListCtrl"):
			return None
		idx = self.modelsListCtrl.GetSelection()
		if idx == wx.NOT_FOUND:
			return self._models[0] if self._models else None
		return self.modelsListCtrl.GetClientData(idx)

	def _requireModel(self, modal=False):
		model = self.getCurrentModel()
		if model:
			return model
		msg = _("Please select a model.")
		if modal:
			gui.messageBox(msg, "OpenAI", wx.OK | wx.ICON_ERROR)
		else:
			ui.message(msg)
		return None

	def _getCurrentModelKey(self):
		model = self.getCurrentModel()
		return self._modelKey(model) if model else None

	def _selectModel(self, selector):
		if not selector:
			return False
		selector_norm = selector.lower() if isinstance(selector, str) else selector
		for i in range(self.modelsListCtrl.GetCount()):
			model = self.modelsListCtrl.GetClientData(i)
			if not model:
				continue
			if selector_norm == model.id.lower() or selector == self._modelKey(model):
				self.modelsListCtrl.SetSelection(i)
				return True
			if isinstance(selector_norm, str) and "/" in selector_norm and selector_norm.endswith("/" + model.id.lower()):
				self.modelsListCtrl.SetSelection(i)
				return True
		return False

	def _getFavoriteModels(self):
		fav = self.data.get("favorite_models", [])
		return fav if isinstance(fav, list) else []

	def _favoriteKey(self, model):
		return self._modelKey(model)

	def _isModelFavorite(self, model):
		fav = self._getFavoriteModels()
		key = self._favoriteKey(model)
		return key in fav or model.id in fav

	def _getModelSortOrder(self):
		return self.data.get("modelSort", MODEL_SORT_DEFAULT)

	def _sortModelsBySetting(self, models):
		sort_key = self._getModelSortOrder()
		key_fn, reverse = MODEL_SORT_OPTIONS.get(sort_key, MODEL_SORT_OPTIONS[MODEL_SORT_DEFAULT])
		by_key = sorted(models, key=key_fn, reverse=reverse)
		return sorted(by_key, key=lambda m: not self._isModelFavorite(m))

	def _formatModelLabel(self, model):
		capabilities = [_("text")]
		if model.vision:
			capabilities.append(_("image"))
		if getattr(model, "audioInput", False) or getattr(model, "audioOutput", False):
			capabilities.append(_("audio"))
		if model.reasoning:
			capabilities.append(_("reasoning"))
		if model.supports_web_search:
			capabilities.append(_("web search"))
		cap_str = ", ".join(capabilities)
		ctx_k = model.contextWindow // 1000
		prefix = "★ " if self._isModelFavorite(model) else ""
		return f"{prefix}{model.name}  |  {cap_str}  |  {ctx_k}k"

	def _getDefaultSelection(self):
		account = self.getCurrentAccount()
		if account:
			account_key = account["key"]
			last_by_account = self.data.get("lastModelByAccount", {})
			if isinstance(last_by_account, dict):
				model_id = last_by_account.get(account_key)
				if isinstance(model_id, str) and model_id:
					return model_id
			last_selection = self.data.get("lastModelSelection")
			prefix = f"{account_key}/"
			if isinstance(last_selection, str) and last_selection.lower().startswith(prefix):
				parts = last_selection.split("/", 2)
				if len(parts) == 3 and parts[2]:
					return parts[2]
		last_model = self.data.get("lastModel")
		if isinstance(last_model, str) and last_model:
			return last_model
		return self.conf["modelVision" if self.pathList else "model"]

	def _persistCurrentModelSelection(self, model):
		if not model:
			return
		changed = False
		account = self.getCurrentAccount()
		if account:
			account_key = account["key"]
			if not isinstance(self.data.get("lastModelByAccount"), dict):
				self.data["lastModelByAccount"] = {}
				changed = True
			if self.data["lastModelByAccount"].get(account_key) != model.id:
				self.data["lastModelByAccount"][account_key] = model.id
				changed = True
			if self.data.get("lastAccountKey") != account_key:
				self.data["lastAccountKey"] = account_key
				changed = True
			new_sel = f"{account_key}/{model.id}"
			if self.data.get("lastModelSelection") != new_sel:
				self.data["lastModelSelection"] = new_sel
				changed = True
		if self.data.get("lastModel") != model.id:
			self.data["lastModel"] = model.id
			changed = True
		if changed:
			self.saveData(True)

	def _refreshModelsList(self, model_to_select=None):
		self.modelsListCtrl.Clear()
		if not self._models:
			return
		for model in self._sortModelsBySetting(self._models):
			self.modelsListCtrl.Append(self._formatModelLabel(model), model)
		selector = model_to_select or self._getDefaultSelection()
		if not self._selectModel(selector) and self.modelsListCtrl.GetCount():
			self.modelsListCtrl.SetSelection(0)

	def onModelChange(self, evt):
		model = self.getCurrentModel()
		if not model:
			return
		self._persistCurrentModelSelection(model)
		self.maxTokensSpinCtrl.SetRange(0, model.maxOutputToken if model.maxOutputToken > 1 else model.contextWindow)
		key_maxTokens = "maxTokens_%s" % model.id
		defaultMaxOutputToken = self.data.get(key_maxTokens, 0) if isinstance(self.data.get(key_maxTokens, 0), int) else 0
		self.maxTokensSpinCtrl.SetValue(defaultMaxOutputToken)

		if model.reasoning:
			self.reasoningModeCheckBox.Enable(True)
			self.reasoningModeCheckBox.Show(True)
			reasoning_on = self.reasoningModeCheckBox.IsChecked()
			opts = model.reasoning_effort_options
			if opts and reasoning_on:
				labels = [o[1] for o in opts]
				self._reasoningEffortOptions = opts
				self.reasoningEffortChoice.Set(labels)
				saved = self.conf.get("reasoningEffort", "medium")
				idx = next((i for i, (v, _) in enumerate(opts) if v == saved), 0)
				self.reasoningEffortChoice.SetSelection(idx)
				self.reasoningEffortChoice.Enable(True)
				self.reasoningEffortChoice.Show(True)
			else:
				self._reasoningEffortOptions = ()
				self.reasoningEffortChoice.Clear()
				self.reasoningEffortChoice.Enable(False)
				self.reasoningEffortChoice.Show(False)
			if model.adaptive_choice_visible and reasoning_on:
				self.adaptiveThinkingCheckBox.Enable(True)
				self.adaptiveThinkingCheckBox.Show(True)
				self.adaptiveThinkingCheckBox.SetValue(self.conf.get("adaptiveThinking", True))
			else:
				self.adaptiveThinkingCheckBox.Enable(False)
				self.adaptiveThinkingCheckBox.Show(False)
				if not model.adaptive_choice_visible:
					self.adaptiveThinkingCheckBox.SetValue(False)
		else:
			self.reasoningModeCheckBox.Enable(False)
			self.reasoningModeCheckBox.Show(False)
			self.reasoningModeCheckBox.SetValue(False)
			self.reasoningEffortChoice.Clear()
			self.reasoningEffortChoice.Enable(False)
			self.reasoningEffortChoice.Show(False)
			self.adaptiveThinkingCheckBox.Enable(False)
			self.adaptiveThinkingCheckBox.Show(False)
			self.adaptiveThinkingCheckBox.SetValue(False)

		if model.supports_web_search:
			self.webSearchCheckBox.Enable(True)
			self.webSearchCheckBox.Show(True)
		else:
			self.webSearchCheckBox.Enable(False)
			self.webSearchCheckBox.Show(False)
			self.webSearchCheckBox.SetValue(False)

		if self.conf["advancedMode"]:
			if "temperature" in model.supportedParameters:
				self.temperatureSpinCtrl.Enable(True)
				self.temperatureLabel.Enable(True)
				self.temperatureSpinCtrl.Show(True)
				self.temperatureLabel.Show(True)
				self.temperatureSpinCtrl.SetRange(0, int(model.maxTemperature * 100))
				key_temperature = "temperature_%s" % model.id
				if key_temperature in self.data:
					self.temperatureSpinCtrl.SetValue(int(self.data[key_temperature]))
				else:
					self.temperatureSpinCtrl.SetValue(int(model.defaultTemperature * 100))
			else:
				self.temperatureSpinCtrl.Enable(False)
				self.temperatureLabel.Enable(False)
				self.temperatureSpinCtrl.Show(False)
				self.temperatureLabel.Show(False)
			if "top_p" in model.supportedParameters:
				self.topPLabel.Enable(True)
				self.topPSpinCtrl.Enable(True)
				self.topPLabel.Show(True)
				self.topPSpinCtrl.Show(True)
			else:
				self.topPLabel.Enable(False)
				self.topPSpinCtrl.Enable(False)
				self.topPLabel.Show(False)
				self.topPSpinCtrl.Show(False)
	def showModelDetails(self, evt=None):
		model = self._requireModel()
		if not model:
			return
		html = build_model_details_html(model)
		ui.browseableMessage(html, _("Model details"), isHtml=True)

	def _reloadModels(self):
		account = self.getCurrentAccount()
		if not account:
			self._models = []
			self._refreshModelsList()
			return
		clearModelCache(account["provider"])
		self._models = getModels(account["provider"], account_id=account.get("id"))
		self._refreshModelsList(model_to_select=self._getCurrentModelKey())
		wx.CallAfter(self.onModelChange, None)

	def onFavoriteModel(self, evt):
		model = self._requireModel()
		if not model:
			return
		fav = self._getFavoriteModels()
		key = self._favoriteKey(model)
		if self._isModelFavorite(model):
			self.data["favorite_models"] = [x for x in fav if x != key and x != model.id]
		else:
			self.data["favorite_models"] = fav + [key]
		self.saveData(True)
		self._refreshModelsList(model_to_select=self._modelKey(model))
		wx.CallAfter(self.onModelChange, None)

	def onModelKeyDown(self, evt):
		if evt.GetKeyCode() == wx.WXK_SPACE:
			if evt.GetModifiers() == wx.MOD_SHIFT:
				self.onFavoriteModel(evt)
			elif evt.GetModifiers() == wx.MOD_NONE:
				self.showModelDetails()
		elif evt.GetKeyCode() == wx.WXK_RETURN:
			self.onSubmit(evt)
		else:
			evt.Skip()

	def _onModelSortChoice(self, evt, sort_key):
		self.data["modelSort"] = sort_key
		self.saveData(True)
		current_key = self._getCurrentModelKey()
		self._refreshModelsList(model_to_select=current_key)
		wx.CallAfter(self.onModelChange, None)

	def onModelContextMenu(self, evt):
		model = self._requireModel()
		if not model:
			return
		menu = wx.Menu()
		item_id = wx.NewIdRef()
		menu.Append(item_id, _("Show model &details") + " (Space)")
		self.Bind(wx.EVT_MENU, self.showModelDetails, id=item_id)
		isFavorite = self._isModelFavorite(model)
		item_id = wx.NewIdRef()
		label = _("Add to &favorites") if not isFavorite else _("Remove from &favorites")
		menu.Append(item_id, f"{label} (Shift+Space)")
		self.Bind(wx.EVT_MENU, self.onFavoriteModel, id=item_id)
		menu.AppendSeparator()
		sort_menu = wx.Menu()
		current_sort = self._getModelSortOrder()
		sort_labels = {
			"created": _("Most recent first"),
			"created_asc": _("Oldest first"),
			"name": _("Name (A–Z)"),
			"name_desc": _("Name (Z–A)"),
			"context": _("Context window (largest first)"),
			"context_asc": _("Context window (smallest first)"),
			"max_tokens": _("Max output tokens (highest first)"),
			"max_tokens_asc": _("Max output tokens (lowest first)"),
		}
		for key in MODEL_SORT_OPTIONS:
			item_id = wx.NewIdRef()
			label = sort_labels.get(key, key)
			sort_menu.AppendRadioItem(item_id, label)
			if key == current_sort:
				sort_menu.Check(item_id, True)
			self.Bind(wx.EVT_MENU, lambda e, k=key: self._onModelSortChoice(e, k), id=item_id)
		menu.AppendSubMenu(sort_menu, _("&Sort by"))
		menu.AppendSeparator()
		item_id = wx.NewIdRef()
		menu.Append(item_id, _("&Refresh model list"))
		self.Bind(wx.EVT_MENU, lambda e: self._reloadModels(), id=item_id)
		menu.AppendSeparator()
		self.modelsListCtrl.PopupMenu(menu)
		menu.Destroy()
