"""Modal dialog for API account management (add / edit / remove)."""

import re

import addonHandler
import gui
import wx

from . import apikeymanager
from .consts import BASE_URLs
from .providertools_helpers import add_labeled_factory

addonHandler.initTranslation()


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
			lambda: wx.TextCtrl(formPanel, value=self.account.get("base_url") or ""),
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
		if provider in ("CustomOpenAI", "Ollama"):
			base_url = self._normalize_custom_base_url(self.customBaseUrlText.GetValue())
			if provider == "Ollama" and not base_url:
				base_url = BASE_URLs.get("Ollama", "http://127.0.0.1:11434/v1")
		else:
			base_url = ""
		return {
			"provider": provider,
			"name": self.nameText.GetValue().strip(),
			"api_key": self.apiKeyText.GetValue().strip(),
			"base_url": base_url,
			"org_name": self.orgNameText.GetValue().strip(),
			"org_key": self.orgKeyText.GetValue().strip(),
		}


class AccountsManagementDialog(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, title=_("API accounts"))
		self._account_entries = []
		self._build_ui()
		self.CenterOnParent()
		self.SetSize((560, 440))
		self._refresh_list()

	def _build_ui(self):
		panel = wx.Panel(self)
		root = wx.BoxSizer(wx.VERTICAL)
		hint = wx.StaticText(
			panel,
			label=_("Provider accounts used by AI-Hub. Double-click an entry to edit."),
		)
		root.Add(hint, 0, wx.ALL, 10)
		self.accounts_list = wx.ListBox(panel, size=(520, 240))
		self.accounts_list.Bind(wx.EVT_LISTBOX_DCLICK, self.on_edit)
		root.Add(self.accounts_list, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
		btn_row = wx.BoxSizer(wx.HORIZONTAL)
		self.add_btn = wx.Button(panel, label=_("&Add..."))
		self.edit_btn = wx.Button(panel, label=_("&Edit..."))
		self.remove_btn = wx.Button(panel, label=_("&Remove"))
		for b in (self.add_btn, self.edit_btn, self.remove_btn):
			btn_row.Add(b, 0, wx.RIGHT, 8)
		root.Add(btn_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
		self.add_btn.Bind(wx.EVT_BUTTON, self.on_add)
		self.edit_btn.Bind(wx.EVT_BUTTON, self.on_edit)
		self.remove_btn.Bind(wx.EVT_BUTTON, self.on_remove)
		btns = wx.StdDialogButtonSizer()
		close_btn = wx.Button(panel, wx.ID_CANCEL, label=_("&Close"))
		btns.AddButton(close_btn)
		btns.Realize()
		close_btn.SetDefault()
		root.Add(btns, 0, wx.ALIGN_CENTER | wx.BOTTOM, 12)
		panel.SetSizer(root)
		close_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))

	def _refresh_list(self, select_key=None):
		self._account_entries = []
		self.accounts_list.Clear()
		for provider in apikeymanager.AVAILABLE_PROVIDERS:
			manager = apikeymanager.get(provider)
			active_id = manager.get_active_account_id()
			for acc in manager.list_accounts(include_env=True):
				entry = {
					"provider": provider,
					"id": acc["id"],
					"name": acc.get("name") or _("Account"),
					"api_key": acc.get("api_key", ""),
					"base_url": acc.get("base_url") or "",
					"org_name": acc.get("org_name", ""),
					"org_key": acc.get("org_key", ""),
				}
				entry["key"] = f"{provider}/{entry['id']}"
				label = f"{provider} / {entry['name']}"
				if provider in ("CustomOpenAI", "Ollama") and entry["base_url"]:
					label = f"{label} - {entry['base_url']}"
				if entry["id"] == active_id:
					label = f"{label} ({_('default')})"
				self._account_entries.append(entry)
				self.accounts_list.Append(label)
		if self._account_entries:
			target = select_key
			if not target:
				for i, entry in enumerate(self._account_entries):
					manager = apikeymanager.get(entry["provider"])
					if manager.get_active_account_id() == entry["id"]:
						self.accounts_list.SetSelection(i)
						break
				else:
					self.accounts_list.SetSelection(0)
			else:
				for i, entry in enumerate(self._account_entries):
					if entry["key"] == target:
						self.accounts_list.SetSelection(i)
						break
				else:
					self.accounts_list.SetSelection(0)

	def _get_selected_entry(self):
		idx = self.accounts_list.GetSelection()
		if idx == wx.NOT_FOUND:
			return None
		if idx < 0 or idx >= len(self._account_entries):
			return None
		return self._account_entries[idx]

	def on_add(self, evt):
		dlg = AccountDialog(self, _("Add account"))
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return
		data = dlg.getData()
		dlg.Destroy()
		if data["provider"] == "CustomOpenAI":
			if not data["base_url"]:
				gui.messageBox(_("Custom base URL is required for CustomOpenAI accounts."), _("AI-Hub"), wx.OK | wx.ICON_ERROR)
				return
		elif data["provider"] == "Ollama":
			pass
		elif not data["api_key"]:
			gui.messageBox(_("API key is required."), _("AI-Hub"), wx.OK | wx.ICON_ERROR)
			return
		manager = apikeymanager.get(data["provider"])
		acc_id = manager.add_account(
			name=data["name"] or _("Account"),
			api_key=data["api_key"],
			base_url=data.get("base_url", ""),
			org_name=data["org_name"],
			org_key=data["org_key"],
			set_active=True,
		)
		self._refresh_list(select_key=f"{data['provider']}/{acc_id}")

	def on_edit(self, evt):
		entry = self._get_selected_entry()
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
				gui.messageBox(_("Custom base URL is required for CustomOpenAI accounts."), _("AI-Hub"), wx.OK | wx.ICON_ERROR)
				return
		elif updated["provider"] == "Ollama":
			pass
		elif not updated["api_key"]:
			gui.messageBox(_("API key is required."), _("AI-Hub"), wx.OK | wx.ICON_ERROR)
			return
		if updated["provider"] == entry["provider"]:
			manager = apikeymanager.get(entry["provider"])
			manager.update_account(
				entry["id"],
				name=updated["name"] or _("Account"),
				api_key=updated["api_key"],
				base_url=updated.get("base_url", ""),
				org_name=updated["org_name"],
				org_key=updated["org_key"],
			)
			manager.set_active_account(entry["id"])
			self._refresh_list(select_key=f"{entry['provider']}/{entry['id']}")
			return
		old_manager = apikeymanager.get(entry["provider"])
		new_manager = apikeymanager.get(updated["provider"])
		new_id = new_manager.add_account(
			name=updated["name"] or _("Account"),
			api_key=updated["api_key"],
			base_url=updated.get("base_url", ""),
			org_name=updated["org_name"],
			org_key=updated["org_key"],
			set_active=True,
		)
		old_manager.remove_account(entry["id"])
		self._refresh_list(select_key=f"{updated['provider']}/{new_id}")

	def on_remove(self, evt):
		entry = self._get_selected_entry()
		if not entry:
			return
		res = gui.messageBox(
			_("Remove account {name} from provider {provider}?").format(**{
				"name": entry["name"],
				"provider": entry["provider"],
			}),
			_("Remove account"),
			wx.YES_NO | wx.ICON_QUESTION,
		)
		if res != wx.YES:
			return
		manager = apikeymanager.get(entry["provider"])
		manager.remove_account(entry["id"])
		self._refresh_list()


def show_accounts_management(parent=None):
	"""Show the API accounts dialog modally. ``parent`` defaults to the NVDA main frame."""
	parent = parent or gui.mainFrame
	dlg = AccountsManagementDialog(parent)
	dlg.ShowModal()
	dlg.Destroy()
