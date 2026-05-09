"""Shared UI helpers for attachment list controls (files and audio)."""

import wx


class AttachmentListUIMixin:
	"""Attachment list UI helpers."""

	def _sync_attachments_section_header(self):
		try:
			page = self.get_active_page()
		except Exception:
			return
		lbl = getattr(page, "attachmentsSectionLabel", None)
		if lbl is None:
			return
		if page.pathList or page.audioPathList:
			lbl.Show()
		else:
			lbl.Hide()

	def _attachment_list_end_refresh(self, list_ctrl, *, focus_prompt_if_empty=True):
		self.Layout()
		if list_ctrl.GetItemCount() == 0:
			if focus_prompt_if_empty:
				self.promptTextCtrl.SetFocus()
			return
		list_ctrl.SetItemState(0, wx.LIST_STATE_FOCUSED, wx.LIST_STATE_FOCUSED)

	def _list_ctrl_selected_indices(self, list_ctrl):
		out = []
		i = list_ctrl.GetFirstSelected()
		while i != wx.NOT_FOUND:
			out.append(i)
			i = list_ctrl.GetNextSelected(i)
		return out
