"""Panel for one notebook page: system prompt, messages, prompt, and attachments."""

import wx

import addonHandler

from .consts import UI_SECTION_SPACING_PX

addonHandler.initTranslation()


class ConversationSessionPanel(wx.Panel):
	"""One session tab page: system prompt, messages, prompt, file/audio lists, and worker slot."""

	def __init__(self, parent, host):
		super().__init__(parent)
		self.host = host
		self.worker = None
		self.stopRequest = None
		self.firstBlock = None
		self.lastBlock = None
		self.pathList = []
		self.audioPathList = []
		self._conversationId = None
		self._historyPath = None
		self.previousPrompt = None
		self.blocks = []
		self.conversationModelHint = ""
		self.conversationAccountKey = ""
		self.conversationSystemText = ""
		self.conversationUiState = {}
		self.session_lazy_load = False

		root = wx.BoxSizer(wx.VERTICAL)

		self.accountLabel = wx.StaticText(self, label=_("&Account:"))
		self.accountListCtrl = wx.ListBox(self, size=(700, 110))
		self.accountListCtrl.Bind(wx.EVT_LISTBOX, host.onAccountChange)
		root.Add(self.accountLabel, 0, wx.LEFT | wx.RIGHT | wx.TOP, UI_SECTION_SPACING_PX)
		root.Add(self.accountListCtrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, UI_SECTION_SPACING_PX)

		self.systemPromptLabel = wx.StaticText(self, label=_("Sy&stem prompt:"))
		self.systemTextCtrl = wx.TextCtrl(self, size=(700, -1), style=wx.TE_MULTILINE)
		self.systemTextCtrl.Bind(wx.EVT_CONTEXT_MENU, host.onSystemContextMenu)
		self.systemTextCtrl.Bind(wx.EVT_TEXT, host._onSystemTextEdited)
		root.Add(self.systemPromptLabel, 0, wx.LEFT | wx.RIGHT | wx.TOP, UI_SECTION_SPACING_PX)
		root.Add(self.systemTextCtrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, UI_SECTION_SPACING_PX)

		exchange_col = wx.BoxSizer(wx.VERTICAL)
		self.messagesLabel = wx.StaticText(self, label=_("Me&ssages:"))
		exchange_col.Add(self.messagesLabel, 0, wx.LEFT | wx.RIGHT | wx.TOP, UI_SECTION_SPACING_PX)
		self.messagesTextCtrl = wx.TextCtrl(
			self,
			style=wx.TE_MULTILINE | wx.TE_READONLY,
			size=(700, -1),
		)
		exchange_col.Add(self.messagesTextCtrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, UI_SECTION_SPACING_PX)

		self.promptLabel = wx.StaticText(self, label=_("&Prompt:"))
		exchange_col.Add(self.promptLabel, 0, wx.LEFT | wx.RIGHT | wx.TOP, UI_SECTION_SPACING_PX)
		self.promptTextCtrl = wx.TextCtrl(
			self,
			size=(700, -1),
			style=wx.TE_MULTILINE,
		)
		exchange_col.Add(self.promptTextCtrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, UI_SECTION_SPACING_PX)

		root.Add(exchange_col, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, UI_SECTION_SPACING_PX)

		self.messagesTextCtrl.Bind(wx.EVT_CONTEXT_MENU, host.onHistoryContextMenu)
		self.messagesTextCtrl.Bind(wx.EVT_KEY_DOWN, host.onMessagesKeyDown)
		self.promptTextCtrl.Bind(wx.EVT_CONTEXT_MENU, host.onPromptContextMenu)
		self.promptTextCtrl.Bind(wx.EVT_KEY_DOWN, host.onPromptKeyDown)
		self.promptTextCtrl.Bind(wx.EVT_TEXT_PASTE, host.onPromptPasteSmart)

		self.modelsLabel = wx.StaticText(self, label=_("M&odel:"))
		self.modelsListCtrl = wx.ListBox(self, size=(700, 200))
		self.modelsListCtrl.Bind(wx.EVT_LISTBOX, host.onModelChange)
		self.modelsListCtrl.Bind(wx.EVT_KEY_DOWN, host.onModelKeyDown)
		self.modelsListCtrl.Bind(wx.EVT_CONTEXT_MENU, host.onModelContextMenu)
		self.modelsListCtrl.Bind(wx.EVT_RIGHT_UP, host.onModelContextMenu)
		root.Add(self.modelsLabel, 0, wx.LEFT | wx.RIGHT | wx.TOP, UI_SECTION_SPACING_PX)
		root.Add(self.modelsListCtrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, UI_SECTION_SPACING_PX)

		att_sz = wx.BoxSizer(wx.VERTICAL)
		self.attachmentsSectionLabel = wx.StaticText(self, label=_("Attachments"))
		att_sz.Add(self.attachmentsSectionLabel, 0, wx.LEFT | wx.RIGHT | wx.TOP, UI_SECTION_SPACING_PX)
		self.imagesLabel = wx.StaticText(
			self,
			label=_("&Files:"),
		)
		self.imagesListCtrl = wx.ListCtrl(
			self,
			style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES,
			size=(700, 200),
		)
		self.imagesListCtrl.InsertColumn(0, _("name"))
		self.imagesListCtrl.InsertColumn(1, _("path"))
		self.imagesListCtrl.InsertColumn(2, _("size"))
		self.imagesListCtrl.InsertColumn(3, _("Dimensions"))
		self.imagesListCtrl.InsertColumn(4, _("description"))
		self.imagesListCtrl.SetColumnWidth(0, 100)
		self.imagesListCtrl.SetColumnWidth(1, 200)
		self.imagesListCtrl.SetColumnWidth(2, 100)
		self.imagesListCtrl.SetColumnWidth(3, 100)
		self.imagesListCtrl.SetColumnWidth(4, 200)
		att_sz.Add(self.imagesLabel, 0, wx.LEFT | wx.RIGHT | wx.TOP, UI_SECTION_SPACING_PX)
		att_sz.Add(self.imagesListCtrl, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, UI_SECTION_SPACING_PX)
		self.imagesListCtrl.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, host.onImageListContextMenu)
		self.imagesListCtrl.Bind(wx.EVT_KEY_DOWN, host.onImageListKeyDown)
		self.imagesListCtrl.Bind(wx.EVT_CONTEXT_MENU, host.onImageListContextMenu)
		self.imagesListCtrl.Bind(wx.EVT_RIGHT_UP, host.onImageListContextMenu)

		self.audioLabel = wx.StaticText(
			self,
			label=_("A&udio files:"),
		)
		self.audioListCtrl = wx.ListCtrl(
			self,
			style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES,
			size=(700, 120),
		)
		self.audioListCtrl.InsertColumn(0, _("File"))
		self.audioListCtrl.InsertColumn(1, _("Path"))
		self.audioListCtrl.SetColumnWidth(0, 150)
		self.audioListCtrl.SetColumnWidth(1, 450)
		att_sz.Add(self.audioLabel, 0, wx.LEFT | wx.RIGHT | wx.TOP, UI_SECTION_SPACING_PX)
		att_sz.Add(self.audioListCtrl, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, UI_SECTION_SPACING_PX)
		self.audioListCtrl.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, host.onAudioListContextMenu)
		self.audioListCtrl.Bind(wx.EVT_CONTEXT_MENU, host.onAudioListContextMenu)
		self.audioListCtrl.Bind(wx.EVT_KEY_DOWN, host.onAudioListKeyDown)

		self.attachmentsSectionLabel.Hide()
		self.imagesLabel.Hide()
		self.imagesListCtrl.Hide()
		self.audioLabel.Hide()
		self.audioListCtrl.Hide()

		root.Add(att_sz, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, UI_SECTION_SPACING_PX)

		self.SetSizer(root)
