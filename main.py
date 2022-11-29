import os
import wx

class Annotation(object):
    def __init__(self):
        super().__init__()

        # Properties of the object
        self.included_lines = []
        self.tuple_groups = []
        self.tuple_flags = []
        self.number_of_lines = 0
        self.source_code_path = ""

# Abstract class so that the page controller knows that each view_controller has a view
class AnnotateViewControllerAbstract(object):
    def set_view(self, view: wx.Panel):
        self._view = view
    def get_view(self):
        return self._view
    def set_annotation(self, annotation: Annotation):
        pass

    view = property(get_view, set_view)

class RequestView(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Adding buttons the the request view
        self.edit_button = wx.Button(self, label='Select Source File')
        button_sizer.Add(self.edit_button, 0, wx.ALL | wx.LEFT, 20)

        main_sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER)

        self.SetSizer(main_sizer)

class RequestViewController(AnnotateViewControllerAbstract):
    def __init__(self, view_parent):
        super().__init__()
        self.view = RequestView(view_parent)
        self.view.edit_button.Bind(wx.EVT_BUTTON, self.on_edit)

        # Creating the initial Annotation maybe implement better so that more clear it
        # shouldn't be None
        self.annotation = Annotation()

    def on_edit(self, event):
        dialog = wx.FileDialog(self.view, "Open Source File",
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_CANCEL:
            return

        # Set the annotation path to the use selected path
        self.annotation.source_code_path = dialog.GetPath()

    # Setting the controller view to be of RequestView and not just wx.Panel
    def set_view(self, view: RequestView):
        self._view = view
    def get_view(self):
        return self._view

    view = property(get_view, set_view)

class AnnotateView(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The table list
        self.list_ctrl = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.list_ctrl.InsertColumn(0, ' ', format=wx.LIST_FORMAT_RIGHT, width=wx.LIST_AUTOSIZE)
        self.list_ctrl.InsertColumn(1, 'Lines', format=wx.LIST_FORMAT_LEFT, width=wx.LIST_AUTOSIZE)
        main_sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 5)

        # Formatting buttons
        self.include_mode_button = wx.Button(self, label='Switch to Inclusion')
        button_sizer.Add(self.include_mode_button, 0, wx.ALL | wx.RIGHT, 20)

        main_sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER)

        self.SetSizer(main_sizer)


class AnnotateViewController(AnnotateViewControllerAbstract):
    def __init__(self, view_parent):
        super().__init__()
        self.annotation = None
        self.view = AnnotateView(view_parent)
        self.include_mode = False

        # Binding the buttons of the view with the handlers in controller
        self.view.include_mode_button.Bind(wx.EVT_BUTTON, self.on_include_mode)
        self.view.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.item_selected)

        self.view.Show()

    # Setting the self.view to be of AnnotateView type instead of just wx.panel
    def set_view(self, view: AnnotateView):
        self._view = view
    def get_view(self):
        return self._view

    view = property(get_view, set_view)
    def set_annotation(self, annotation: Annotation):
        self.annotation = annotation
        self.load_content(self.annotation.source_code_path)
        print("Loading content")

    def update_color(self):
        for index in range(self.annotation.number_of_lines):
            self.view.list_ctrl.SetItemTextColour(index, wx.Colour(0, 0, 0))
            self.annotation.included_lines[index] = ~self.include_mode  # Setting default

    def load_content(self, path):
        if os.path.exists(path):
            with open(path) as fobj:
                i = 0
                for line in fobj:
                    # Adding indexes to first column
                    self.view.list_ctrl.InsertItem(i, "%i " % i)

                    # Adding lines to the second column
                    self.view.list_ctrl.SetItem(i, 1, line)
                    i += 1
                self.annotation.number_of_lines = i

                # Creating an array of boolean values to represent if included or not
                self.annotation.included_lines = [True] * i

        self.view.list_ctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.view.list_ctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)

    # Handling include_mode button press
    def on_include_mode(self, event):
        # Swap the include mode to not include mode (exclude_mode)
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

# The controlling class for the pages
class AnnotationPagesViewController(object):
    def __init__(self, view_parent):
        super().__init__()
        # The controller has an associated view
        self.view = AnnotationPagesView(view_parent)

        # The array of pages and number of pages in it
        self.pages = []
        self.page_num = 0

        # The annotation object that each page will need to know about/ we are creating
        self.annotation = Annotation()

        # binding the button presses to methods
        self.view.prevBtn.Bind(wx.EVT_BUTTON, self.onPrev)
        self.view.nextBtn.Bind(wx.EVT_BUTTON, self.onNext)

    def addPage(self, title_controller: AnnotateViewControllerAbstract, title=None,):

        # Adding the page controller view to the panel view
        self.view.panelSizer.Add(title_controller.view, 2, wx.EXPAND)

        # Add the controller to the list of pages
        self.pages.append(title_controller)
        if len(self.pages) > 1:
            # hide all panels after the first one
            title_controller.view.Hide()
            self.view.Layout()
    def onNext(self, event):
        pageCount = len(self.pages)
        if pageCount - 1 != self.page_num:
            self.pages[self.page_num].view.Hide()
            self.annotation = self.pages[self.page_num].annotation
            self.page_num += 1
            self.pages[self.page_num].view.Show()

            # Setting the annotation of the page controller
            self.pages[self.page_num].set_annotation(self.annotation)

            self.view.panelSizer.Layout()
        else:
            print("End of pages!")

        if self.view.nextBtn.GetLabel() == "Finish":
            # close the app
            self.view.GetParent().Close()

        if pageCount == self.page_num + 1:
            # change label
            self.view.nextBtn.SetLabel("Finish")

    def onPrev(self, event):
        pageCount = len(self.pages)
        if self.page_num - 1 != -1:
            self.pages[self.page_num].view.Hide()
            self.page_num -= 1
            self.pages[self.page_num].view.Show()
            self.view.panelSizer.Layout()

            # Make sure to set the other button back to next instead of finish
            self.view.nextBtn.SetLabel("Next")
        else:
            print("You're already on the first page!")

# The view that holds the pages, includes navigation between pages
class AnnotationPagesView(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        #Creating the sizers
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # add prev/next buttons
        self.prevBtn = wx.Button(self, label="Previous")

        btn_sizer.Add(self.prevBtn, 0, wx.ALL, 5)

        self.nextBtn = wx.Button(self, label="Next")
        btn_sizer.Add(self.nextBtn, 0, wx.ALL, 5)

        # finish layout
        self.mainSizer.Add(self.panelSizer, 1, wx.EXPAND)
        self.mainSizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT)
        self.SetSizer(self.mainSizer)

# The view controller for the main application.
class ApplicationViewController(object):
    def __init__(self):
        super().__init__()
        self.view = AppFrame()

        # The controller of the panels of the application
        self.panel_controller = AnnotationPagesViewController(self.view)

        # Creating a request view controller
        request_view_controller = RequestViewController(view_parent=self.panel_controller.view)

        # Creating an annotation view controller (this will be changed to included/exclude class that
        # inherits from AnnotateViewController
        annotate_view_controller2 = AnnotateViewController(view_parent=self.panel_controller.view)

        # Adding the view controllers to the panel controller
        self.panel_controller.addPage(request_view_controller, title="Selecting New Annotation")
        self.panel_controller.addPage(annotate_view_controller2, title="Creating New Annotation")
        self.view.Layout()

        self.view.Show()


# This is the main frame (or view) of the application
class AppFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title='Annotation', size=(800,600))

# Initial start up of the application view controller
if __name__ == '__main__':
    app = wx.App(False)
    app_controller = ApplicationViewController()
    app.MainLoop()
