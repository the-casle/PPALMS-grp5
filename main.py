import os
import wx

class Mp3Panel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.row_obj_dict = {}

        self.list_ctrl = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.list_ctrl.InsertColumn(0, ' ', format = wx.LIST_FORMAT_RIGHT, width = wx.LIST_AUTOSIZE)
        self.list_ctrl.InsertColumn(1, 'Lines', format = wx.LIST_FORMAT_LEFT, width=wx.LIST_AUTOSIZE)
        main_sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        edit_button = wx.Button(self, label='Edit')
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.item_selected)
        edit_button.Bind(wx.EVT_BUTTON, self.on_edit)
        main_sizer.Add(edit_button, 0, wx.ALL | wx.CENTER, 5)
        self.SetSizer(main_sizer)

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

        self.list_ctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.list_ctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)

    def item_selected(self, event):
        item = event.GetItem()
        item_ind = event.GetIndex()
        item.SetText("Green")
        self.list_ctrl.GetItem(item_ind, 1).SetBackgroundColour(wx.Colour(green = 255, red = 0, blue = 0, alpha= 255))
        print(self.list_ctrl.GetItem(item_ind, 1).GetBackgroundColour())
        print(self.list_ctrl.GetSelectedItemCount())
            #.SetBackgroundColour("green")
        #SetBackgroundColour(wx.Colour(green = 255, red = 0, blue = 0, alpha= 255))

        print("Index: %i" % item_ind)
        if self.list_ctrl.IsSelected(item_ind):
            self.list_ctrl.SetItemState(item_ind, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
            print("Selected")

class MyPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.my_text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        btn = wx.Button(self, label='Open Text File')
        btn.Bind(wx.EVT_BUTTON, self.onOpen)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.my_text, 1, wx.ALL|wx.EXPAND)
        sizer.Add(btn, 0, wx.ALL|wx.CENTER, 5)

        self.SetSizer(sizer)

    def onOpen(self, event):
        dialog = wx.FileDialog(self, "Open Source File",
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_CANCEL:
            return

        path = dialog.GetPath()

        if os.path.exists(path):
            with open(path) as fobj:
                for line in fobj:
                    self.my_text.WriteText(line)


class MyFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title='Annotation')

        panel = Mp3Panel(self)

        self.Show()

if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()