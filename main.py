import os
import wx

class SystemModel(object):
    def __init__(self, currentProblemSet=None):
        self.currentProblemSet = currentProblemSet
    def create_new_problem_set(self):
        self.currentProblemSet = ProblemSet()

class ProblemSet(object):
    def __init__(self, annotation=None):
        self.annotation = Annotation(self)

class Annotation(object):
    def __init__(self, parent):
        super().__init__()
        self.included_lines = []
        self.tuple_groups = []
        self.tuple_flags = []

class UIRequestController(object):
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def request_new_problem_set(self):
        self.model.create_new_problem()


class AnnotatePanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.row_obj_dict = {}
        self.annotation = Annotation(self)
        self.number_of_lines = 0
        self.include_mode = False

        self.list_ctrl = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.list_ctrl.InsertColumn(0, ' ', format = wx.LIST_FORMAT_RIGHT, width = wx.LIST_AUTOSIZE)
        self.list_ctrl.InsertColumn(1, 'Lines', format = wx.LIST_FORMAT_LEFT, width=wx.LIST_AUTOSIZE)
        main_sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 5)

        edit_button = wx.Button(self, label='Select Source File')
        edit_button.Bind(wx.EVT_BUTTON, self.on_edit)
        button_sizer.Add(edit_button, 0, wx.ALL | wx.LEFT, 20)

        self.include_mode_button = wx.Button(self, label='Switch to Inclusion')
        self.include_mode_button.Bind(wx.EVT_BUTTON, self.on_include_mode)
        button_sizer.Add(self.include_mode_button, 0, wx.ALL | wx.RIGHT, 20)

        main_sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER)

        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.item_selected)
        self.SetSizer(main_sizer)

    def on_include_mode(self, event):
        self.include_mode = ~self.include_mode
        self.update_color()
        if self.include_mode:
            self.include_mode_button.SetLabel("Switch to Exclusion")
        else:
            self.include_mode_button.SetLabel("Switch to Inclusion")

    def on_edit(self, event):
        dialog = wx.FileDialog(self, "Open Source File",
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_CANCEL:
            return

        path = dialog.GetPath()

        if os.path.exists(path):
            with open(path) as fobj:
                i = 0
                for line in fobj:
                    self.list_ctrl.InsertItem(i, "%i " % i)
                    self.list_ctrl.SetItem(i, 1, line)
                    i += 1
                self.number_of_lines = i
                self.annotation.included_lines = [True] * i


        self.list_ctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.list_ctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)

    def item_selected(self, event):
        item_ind = event.GetIndex()
        self.list_ctrl.Select(item_ind, False) # Hide the blue highlight for selection
        if self.include_mode:
            if self.annotation.included_lines[item_ind]:
                self.list_ctrl.SetItemTextColour(item_ind, wx.Colour(0, 0, 0))
                self.annotation.included_lines[item_ind] = False

            else:
                self.list_ctrl.SetItemTextColour(item_ind, wx.Colour(0, 150, 0))
                self.annotation.included_lines[item_ind] = True
        else :
            if self.annotation.included_lines[item_ind]:
                self.list_ctrl.SetItemTextColour(item_ind, wx.Colour(255, 0, 0))
                self.annotation.included_lines[item_ind] = False
            else:
                self.list_ctrl.SetItemTextColour(item_ind, wx.Colour(0, 0, 0))
                self.annotation.included_lines[item_ind] = True


    def update_color(self):
        for index in range(self.number_of_lines):
            self.list_ctrl.SetItemTextColour(index, wx.Colour(0, 0, 0))
            self.annotation.included_lines[index] = ~self.include_mode # Setting default

class MyFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title='Annotation')

        panel = AnnotatePanel(self)

        self.Show()

if __name__ == '__main__':
    app = wx.App(False)
    view_controller = UIRequestController(SystemModel(), MyFrame())
    frame = view_controller.view
    app.MainLoop()