"""Chat history: TextSegment and HistoryBlock for the messages control."""


class TextSegment:
	previous = None
	next = None
	originalText = ""
	start = 0
	end = 0
	owner = None

	def __init__(self, control, text, owner):
		self.control = control
		self.originalText = text
		self.owner = owner
		if not hasattr(control, "lastSegment") or control.lastSegment is None:
			control.firstSegment = self
			control.lastSegment = self
		else:
			control.lastSegment.next = self
			self.previous = control.lastSegment
			control.lastSegment = self
		p = control.GetInsertionPoint()
		control.SetInsertionPointEnd()
		self.start = control.GetInsertionPoint()
		control.AppendText(text)
		self.end = control.GetInsertionPoint()
		control.SetInsertionPoint(p)

	def appendText(self, text):
		if not text:
			return
		ctrl = self.control
		insert_len = len(text)
		caret_pos = ctrl.GetInsertionPoint()
		sel_start, sel_end = ctrl.GetSelection()
		append_at = self.end
		ctrl.SetInsertionPoint(append_at)
		ctrl.AppendText(text)
		self.end = append_at + insert_len
		segment = self.next
		while segment is not None:
			segment.start += insert_len
			segment.end += insert_len
			segment = segment.next
		if sel_start != sel_end:
			new_sel_start = sel_start + insert_len if sel_start >= append_at else sel_start
			new_sel_end = sel_end + insert_len if sel_end >= append_at else sel_end
			ctrl.SetSelection(new_sel_start, new_sel_end)
		if caret_pos >= append_at:
			caret_pos += insert_len
		ctrl.SetInsertionPoint(caret_pos)

	def getText(self):
		return self.control.GetRange(self.start, self.end)

	@staticmethod
	def getCurrentSegment(control):
		p = control.GetInsertionPoint()
		if not hasattr(control, "firstSegment"):
			return None
		segment = control.firstSegment
		while segment is not None:
			if segment.start <= p and segment.end > p:
				return segment
			segment = segment.next
		return control.lastSegment

	def delete(self):
		self.control.Remove(self.start, self.end)
		if self.previous is not None:
			self.previous.next = self.next
		else:
			self.control.firstSegment = self.next
		if self.next is not None:
			self.next.previous = self.previous
		else:
			self.control.lastSegment = self.previous
		segment = self.next
		while segment is not None:
			segment.start -= (self.end - self.start)
			segment.end -= (self.end - self.start)
			segment = segment.next


class HistoryBlock:
	previous = None
	next = None
	prompt = ""
	responseText = ""
	reasoningText = ""
	segmentBreakLine = None
	segmentPromptLabel = None
	segmentPrompt = None
	segmentResponseLabel = None
	segmentResponse = None
	segmentReasoningLabel = None
	segmentReasoning = None
	lastLen = 0
	lastReasoningLen = 0
	model = ""
	temperature = 0
	topP = 0
	seed = None
	topK = None
	stopText = ""
	frequencyPenalty = None
	presencePenalty = None
	displayHeader = True
	focused = False
	responseTerminated = False
	# In-code attribute uses the neutral name; on-disk JSON key is still
	# ``pathList`` for backward compatibility with previously saved conversations.
	filesList = None
	audioPathList = None
	audioTranscriptList = None
	audioPath = None
	usage = None
	timing = None
