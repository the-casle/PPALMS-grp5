import os
import wx

#test comment2

class Annotation(object):
    def __init__(self, parent):
        super().__init__()
        self.included_lines = []
        self.tuple_groups = []
        self.tuple_flags = []
        self.number_of_lines = 0

class AnnotateViewController(object):
    def __init__(self,view_parent):
        super().__init__()
        self.view = AnnotateView(view_parent)
        self.annotation = Annotation(self)
        self.include_mode = False

        self.view.edit_button.Bind(wx.EVT_BUTTON, self.on_edit)
        self.view.include_mode_button.Bind(wx.EVT_BUTTON, self.on_include_mode)
        self.view.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.item_selected)

        self.view.Show()
    def update_color(self):
        for index in range(self.annotation.number_of_lines):
            self.view.list_ctrl.SetItemTextColour(index, wx.Colour(0, 0, 0))
            self.annotation.included_lines[index] = ~self.include_mode # Setting default

    def on_include_mode(self, event):
        self.include_mode = ~self.include_mode
        self.update_color()
        if self.include_mode:
            self.view.include_mode_button.SetLabel("Switch to Exclusion")
        else:
            self.view.include_mode_button.SetLabel("Switch to Inclusion")

    def on_edit(self, event):
        dialog = wx.FileDialog(self.view, "Open Source File",
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_CANCEL:
            return

        path = dialog.GetPath()

        if os.path.exists(path):
            with open(path) as fobj:
                i = 0
                for line in fobj:
                    self.view.list_ctrl.InsertItem(i, "%i " % i)
                    self.view.list_ctrl.SetItem(i, 1, line)
                    i += 1
                self.annotation.number_of_lines = i
                self.annotation.included_lines = [True] * i


        self.view.list_ctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.view.list_ctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)


    def item_selected(self, event):
        item_ind = event.GetIndex()
        self.view.list_ctrl.Select(item_ind, False) # Hide the blue highlight for selection
        if self.include_mode:
            if self.annotation.included_lines[item_ind]:
                self.view.list_ctrl.SetItemTextColour(item_ind, wx.Colour(0, 0, 0))
                self.annotation.included_lines[item_ind] = False

            else:
                self.view.list_ctrl.SetItemTextColour(item_ind, wx.Colour(0, 150, 0))
                self.annotation.included_lines[item_ind] = True
        else :
            if self.annotation.included_lines[item_ind]:
                self.view.list_ctrl.SetItemTextColour(item_ind, wx.Colour(255, 0, 0))
                self.annotation.included_lines[item_ind] = False
            else:
                self.view.list_ctrl.SetItemTextColour(item_ind, wx.Colour(0, 0, 0))
                self.annotation.included_lines[item_ind] = True

class AnnotateView(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.list_ctrl = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.list_ctrl.InsertColumn(0, ' ', format = wx.LIST_FORMAT_RIGHT, width = wx.LIST_AUTOSIZE)
        self.list_ctrl.InsertColumn(1, 'Lines', format = wx.LIST_FORMAT_LEFT, width=wx.LIST_AUTOSIZE)
        main_sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 5)

        self.edit_button = wx.Button(self, label='Select Source File')
        button_sizer.Add(self.edit_button, 0, wx.ALL | wx.LEFT, 20)

        self.include_mode_button = wx.Button(self, label='Switch to Inclusion')
        button_sizer.Add(self.include_mode_button, 0, wx.ALL | wx.RIGHT, 20)

        main_sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER)

        self.SetSizer(main_sizer)

class ApplicationViewController(object):
    def __init__(self):
        super().__init__()
        self.view = AppFrame()
        annotate_view_controller = AnnotateViewController(view_parent=self.view)
        self.view.Layout()

class AppFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title='Annotation')

if __name__ == '__main__':
    app = wx.App(False)
    app_controller = ApplicationViewController()
    app_controller.view.Show()
    app.MainLoop()
