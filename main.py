import os
import wx

class Annotation(object):
    def __init__(self):
        super().__init__()
        self.included_lines = []
        self.tuple_groups = []
        self.tuple_flags = []
        self.number_of_lines = 0
        self.source_code_path = ""


class AnnotateView(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.list_ctrl = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.list_ctrl.InsertColumn(0, ' ', format=wx.LIST_FORMAT_RIGHT, width=wx.LIST_AUTOSIZE)
        self.list_ctrl.InsertColumn(1, 'Lines', format=wx.LIST_FORMAT_LEFT, width=wx.LIST_AUTOSIZE)
        main_sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 5)

        self.edit_button = wx.Button(self, label='Select Source File')
        button_sizer.Add(self.edit_button, 0, wx.ALL | wx.LEFT, 20)

        self.include_mode_button = wx.Button(self, label='Switch to Inclusion')
        button_sizer.Add(self.include_mode_button, 0, wx.ALL | wx.RIGHT, 20)

        main_sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER)

        self.SetSizer(main_sizer)


class AnnotateViewControllerAbstract(object):
    def set_view(self, view: wx.Panel):
        self._view = view
    def get_view(self):
        return self._view
    def set_annotation(self, annotation: Annotation):
        pass

    view = property(get_view, set_view)
class RequestViewController(AnnotateViewControllerAbstract):
    def __init__(self, view_parent):
        super().__init__()
        self.view = RequestView(view_parent)
        #self.view.edit_button.Bind(wx.EVT_BUTTON, self.on_edit)

    def on_edit(self, event):
        dialog = wx.FileDialog(self.view, "Open Source File",
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_CANCEL:
            return

        path = dialog.GetPath()


class RequestView(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.edit_button = wx.Button(self, label='Select Source File')
        button_sizer.Add(self.edit_button, 0, wx.ALL | wx.LEFT, 20)

        main_sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER)

        self.SetSizer(main_sizer)

class AnnotateViewController(AnnotateViewControllerAbstract):
    def __init__(self, view_parent, path):
        super().__init__()
        self.view = AnnotateView(view_parent)
        self.annotation = Annotation()
        self.include_mode = False

        self.view.include_mode_button.Bind(wx.EVT_BUTTON, self.on_include_mode)
        self.view.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.item_selected)

        self.view.Show()

        self.load_content(path)

    def set_view(self, view: AnnotateView):
        self._view = view
    def get_view(self):
        return self._view

    view = property(get_view, set_view)
    def setAnnotation(self, annotation: Annotation):
        self.annotation = annotation

    def update_color(self):
        for index in range(self.annotation.number_of_lines):
            self.view.list_ctrl.SetItemTextColour(index, wx.Colour(0, 0, 0))
            self.annotation.included_lines[index] = ~self.include_mode  # Setting default

    def load_content(self, path):
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

    def on_include_mode(self, event):
        self.include_mode = ~self.include_mode
        self.update_color()
        if self.include_mode:
            self.view.include_mode_button.SetLabel("Switch to Exclusion")
        else:
            self.view.include_mode_button.SetLabel("Switch to Inclusion")

    def item_selected(self, event):
        item_ind = event.GetIndex()
        self.view.list_ctrl.Select(item_ind, False)  # Hide the blue highlight for selection
        if self.include_mode:
            if self.annotation.included_lines[item_ind]:
                self.view.list_ctrl.SetItemTextColour(item_ind, wx.Colour(0, 0, 0))
                self.annotation.included_lines[item_ind] = False

            else:
                self.view.list_ctrl.SetItemTextColour(item_ind, wx.Colour(0, 150, 0))
                self.annotation.included_lines[item_ind] = True
        else:
            if self.annotation.included_lines[item_ind]:
                self.view.list_ctrl.SetItemTextColour(item_ind, wx.Colour(255, 0, 0))
                self.annotation.included_lines[item_ind] = False
            else:
                self.view.list_ctrl.SetItemTextColour(item_ind, wx.Colour(0, 0, 0))
                self.annotation.included_lines[item_ind] = True



class WizardPage(wx.Panel):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, title=None):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        if title:
            title = wx.StaticText(self, -1, title)
            title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
            sizer.Add(title, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
            sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 5)


class AnnotationPagesViewController(object):
    def __init__(self, view_parent):
        super().__init__()
        self.view = AnnotationPagesView(view_parent)

        self.pages = []
        self.page_num = 0
        self.annotation = Annotation()

        self.view.prevBtn.Bind(wx.EVT_BUTTON, self.onPrev)
        self.view.nextBtn.Bind(wx.EVT_BUTTON, self.onNext)

    def page(self, index):
        # NEED TO check if valid index still
        return self.pages[index]

    def addPage(self, title_controller: AnnotateViewControllerAbstract, title=None,):

        title_controller.set_annotation(self.annotation)
        self.view.panelSizer.Add(title_controller.view, 2, wx.EXPAND)
        self.pages.append(title_controller.view)
        if len(self.pages) > 1:
            # hide all panels after the first one
            title_controller.view.Hide()
            self.view.Layout()
    def onNext(self, event):
        pageCount = len(self.pages)
        if pageCount - 1 != self.page_num:
            self.pages[self.page_num].Hide()
            self.annotation = self.pages[self.page_num].annotation
            self.page_num += 1
            self.pages[self.page_num].Show()
            self.pages[self.page_num].annotation = self.annotation
            self.view.panelSizer.Layout()
        else:
            print("End of pages!")

        if self.view.nextBtn.GetLabel() == "Finish":
            # close the app
            self.view.GetParent().Close()

        if pageCount == self.page_num + 1:
            # change label
            self.view.nextBtn.SetLabel("Finish")

    # ----------------------------------------------------------------------
    def onPrev(self, event):
        """"""
        pageCount = len(self.pages)
        if self.page_num - 1 != -1:
            self.pages[self.page_num].Hide()
            self.page_num -= 1
            self.pages[self.page_num].Show()
            self.view.panelSizer.Layout()
        else:
            print("You're already on the first page!")
class AnnotationPagesView(wx.Panel):
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        # add prev/next buttons
        self.prevBtn = wx.Button(self, label="Previous")

        btnSizer.Add(self.prevBtn, 0, wx.ALL, 5)

        self.nextBtn = wx.Button(self, label="Next")
        btnSizer.Add(self.nextBtn, 0, wx.ALL, 5)

        # finish layout
        self.mainSizer.Add(self.panelSizer, 1, wx.EXPAND)
        self.mainSizer.Add(btnSizer, 0, wx.ALIGN_RIGHT)
        self.SetSizer(self.mainSizer)

class ApplicationViewController(object):
    def __init__(self):
        super().__init__()
        self.view = AppFrame()

        self.panel_controller = AnnotationPagesViewController(self.view)

        annotate_view_controller = AnnotateViewController(view_parent=self.panel_controller.view, path="path")
        self.panel_controller.addPage(annotate_view_controller, title="Creating New Annotation")
        self.view.Layout()

        self.view.Show()


class AppFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title='Annotation', size=(800,600))


if __name__ == '__main__':
    app = wx.App(False)
    app_controller = ApplicationViewController()
    app.MainLoop()
