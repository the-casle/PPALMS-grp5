import os
import wx

# Basic annotation class, used in other classes
class Annotation(object):
    def __init__(self):
        super().__init__()

        # Properties of the object
        self.included_lines = []
        self.line_tuple_groups = []
        self.tuple_flags = []
        self.number_of_lines = 0
        self.number_of_groups = 0
        self.source_code_path = ""


# Abstract class so that the page controller knows that each view_controller has a view
class AnnotateViewControllerAbstract(object):
    def __init__(self):
        self.view = None

    def set_view(self, view: wx.Panel):
        self._view = view

    def get_view(self):
        return self._view

    def update_with_annotation(self, annotation: Annotation):
        pass

    def reset(self):
        pass

    view = property(get_view, set_view)

# annotation page
class SelectLineView(wx.Panel):
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

        self.clear_button = wx.Button(self, label='Clear Selection')
        button_sizer.Add(self.clear_button, 0, wx.ALL | wx.LEFT, 20)

        description = wx.StaticText(self, label="Selecting lines for inclusion or exclusion")
        main_sizer.Add(description, 0, wx.LEFT, 10)
        main_sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER)

        self.SetSizer(main_sizer)

# annotation page controller
class SelectLineViewController(AnnotateViewControllerAbstract):
    def __init__(self, view_parent):
        super().__init__()
        self.annotation = None
        self.view = SelectLineView(view_parent)
        self.include_mode = False

        # Binding the buttons of the view with the handlers in controller
        self.view.include_mode_button.Bind(wx.EVT_BUTTON, self.on_include_mode)
        self.view.clear_button.Bind(wx.EVT_BUTTON, self.clear_color)
        self.view.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.item_selected)

        self.view.Show()

    # Setting the self.view to be of AnnotateView type instead of just wx.panel
    def set_view(self, view: SelectLineView):
        self._view = view

    def get_view(self):
        return self._view

    view = property(get_view, set_view)

    def reset(self):
        self.annotation = None
        self.view.list_ctrl.DeleteAllItems()

    def update_with_annotation(self, annotation: Annotation):
        self.annotation = annotation
        self.load_content(self.annotation.source_code_path)
        self.update_color()

    def swap_color(self, item_ind: int):
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

    def update_color(self):
        for item_ind in range(self.annotation.number_of_lines):
            if self.include_mode:
                if self.annotation.included_lines[item_ind]:
                    self.view.list_ctrl.SetItemTextColour(item_ind, wx.Colour(0, 150, 0))
                else:
                    self.view.list_ctrl.SetItemTextColour(item_ind, wx.Colour(0, 0, 0))
            else:
                if self.annotation.included_lines[item_ind]:
                    self.view.list_ctrl.SetItemTextColour(item_ind, wx.Colour(0, 0, 0))
                else:
                    self.view.list_ctrl.SetItemTextColour(item_ind, wx.Colour(255, 0, 0))

    def load_content(self, path):
        self.include_mode = False
        self.view.include_mode_button.SetLabel("Switch to Inclusion")
        if os.path.exists(path):
            with open(path) as fobj:
                self.view.list_ctrl.DeleteAllItems()
                i = 0
                # removes new line characters from each line
                lines = [s.strip() for s in fobj.readlines()]
                for line in lines:
                    if line != "":
                        # Adding indexes to first column
                        self.view.list_ctrl.InsertItem(i, "%i " % i)

                        # Adding lines to the second column
                        self.view.list_ctrl.SetItem(i, 1, line)
                        i += 1
                self.annotation.number_of_lines = i

                # Creating an array of boolean values to represent if included or not
                if len(self.annotation.included_lines) != i:
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

    def clear_color(self, event):
        for index in range(self.annotation.number_of_lines):
            self.view.list_ctrl.SetItemTextColour(index, wx.Colour(0, 0, 0))
            self.annotation.included_lines[index] = ~self.include_mode  # Setting default

    def item_selected(self, event):
        item_ind = event.GetIndex()
        self.view.list_ctrl.Select(item_ind, False)  # Hide the blue highlight for selection
        self.swap_color(item_ind)

# tuple page
class SelectTupleView(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        code_sizer = wx.BoxSizer(wx.HORIZONTAL)
        group_sizer = wx.BoxSizer(wx.VERTICAL)

        # The table list
        self.list_ctrl = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.list_ctrl.InsertColumn(0, ' ', format=wx.LIST_FORMAT_RIGHT, width=wx.LIST_AUTOSIZE)
        self.list_ctrl.InsertColumn(1, 'Lines', format=wx.LIST_FORMAT_LEFT, width=wx.LIST_AUTOSIZE)
        code_sizer.Add(self.list_ctrl, 1, wx.ALL | wx.BOTTOM | wx.EXPAND, 5)

        self.group_list_ctrl = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.BORDER_SUNKEN | wx.LC_SINGLE_SEL
        )
        self.group_list_ctrl.InsertColumn(0, 'Groups', format=wx.LIST_FORMAT_CENTER, width=wx.LIST_AUTOSIZE)
        group_sizer.Add(self.group_list_ctrl, 0, wx.EXPAND, 5)

        self.add_group_button = wx.Button(self, label='Add Group')
        group_sizer.Add(self.add_group_button, 0, wx.ALL, 5)

        description = wx.StaticText(self, label="Selecting tuple groups")
        code_sizer.Add(group_sizer, 0, wx.ALL | wx.EXPAND, 20)
        main_sizer.Add(code_sizer, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(description, 0, wx.ALL | wx.EXPAND, 10)

        self.SetSizer(main_sizer)

# tuple controller
class SelectTupleViewController(AnnotateViewControllerAbstract):
    def __init__(self, view_parent):
        super().__init__()
        self.annotation = None
        self.view = SelectTupleView(view_parent)

        self.line_at_index = []

        self.current_color = wx.Colour("green")

        self.group_color = []
        self.selected_group = None

        # Binding the buttons of the view with the handlers in controller
        self.view.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.item_selected)
        self.view.group_list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.group_item_selected)
        self.view.add_group_button.Bind(wx.EVT_BUTTON, self.on_add_group)

        self.view.Show()

    # Setting the self.view to be of AnnotateView type instead of just wx.panel
    def set_view(self, view: SelectTupleView):
        self._view = view

    def get_view(self):
        return self._view

    view = property(get_view, set_view)

    def reset(self):
        self.annotation = None
        self.view.group_list_ctrl.DeleteAllItems()
        self.view.list_ctrl.DeleteAllItems()

    def update_with_annotation(self, annotation: Annotation):
        self.annotation = annotation
        self.annotation.line_tuple_groups = [None] * self.annotation.number_of_lines
        self.load_content(self.annotation.source_code_path)

    def load_content(self, path):
        if os.path.exists(path):
            with open(path) as fobj:
                self.view.list_ctrl.DeleteAllItems()
                # This needs more work, or maybe a better idea to make sure it shows only the lines selected
                i = 0
                j = 0
                self.line_at_index = []
                lines = [s.strip() for s in fobj.readlines()]
                for line in lines:
                    if line != "":
                        if self.annotation.included_lines[i]:
                            # Adding indexes to first column
                            self.view.list_ctrl.InsertItem(j, "%i " % i)

                            # Adding lines to the second column
                            self.view.list_ctrl.SetItem(j, 1, line)
                            self.line_at_index.append(i)
                            j += 1
                        i += 1
                self.annotation.number_of_lines = i

        self.view.list_ctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.view.list_ctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)

    def new_color(self):
        r = self.current_color.GetRed()
        b = self.current_color.GetBlue()
        g = self.current_color.GetGreen()
        r = (r + 213) % 255
        g = (g + 113) % 255
        b = (b + 53) % 255
        self.current_color = wx.Colour(r, g, b)

    # Handling add group button press
    def on_add_group(self, event):
        self.annotation.number_of_groups += 1
        self.view.group_list_ctrl.InsertItem(self.annotation.number_of_groups - 1,
                                             "Group %i" % self.annotation.number_of_groups)
        self.new_color()
        self.group_color.append(self.current_color)
        self.view.group_list_ctrl.SetItemTextColour(self.annotation.number_of_groups - 1, self.current_color)
        self.view.group_list_ctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)

        if self.selected_group is None:
            self.selected_group = 0

    def item_selected(self, event):
        item_ind = event.GetIndex()
        line_num = self.line_at_index[item_ind]
        self.view.list_ctrl.Select(item_ind, False)  # Hide the blue highlight for selection
        if self.annotation.number_of_groups > 0:
            self.view.list_ctrl.SetItemTextColour(item_ind, self.group_color[self.selected_group])
            self.annotation.line_tuple_groups[line_num] = self.selected_group
        else:
            print("Need to add group")

    def group_item_selected(self, event):
        item_ind = event.GetIndex()
        self.selected_group = item_ind

# flag selection
class SelectFlagsView(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        code_sizer = wx.BoxSizer(wx.HORIZONTAL)
        group_sizer = wx.BoxSizer(wx.VERTICAL)

        # The table list
        self.list_ctrl = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.list_ctrl.InsertColumn(0, ' ', format=wx.LIST_FORMAT_RIGHT, width=wx.LIST_AUTOSIZE)
        self.list_ctrl.InsertColumn(1, 'Lines', format=wx.LIST_FORMAT_LEFT, width=wx.LIST_AUTOSIZE)
        code_sizer.Add(self.list_ctrl, 1, wx.ALL | wx.BOTTOM | wx.EXPAND, 5)

        self.group_list_ctrl = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.BORDER_SUNKEN | wx.LC_SINGLE_SEL
        )
        self.group_list_ctrl.InsertColumn(0, 'Groups', format=wx.LIST_FORMAT_CENTER, width=wx.LIST_AUTOSIZE)
        group_sizer.Add(self.group_list_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        self.flag_list_ctrl = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.BORDER_SUNKEN | wx.LC_SINGLE_SEL
        )
        self.flag_list_ctrl.EnableCheckBoxes()
        self.flag_list_ctrl.InsertColumn(0, 'Flags', format=wx.LIST_FORMAT_LEFT, width=wx.LIST_AUTOSIZE)
        self.flag_list_ctrl.InsertItem(0, "Order")
        self.flag_list_ctrl.InsertItem(1, "Distance")
        self.flag_list_ctrl.InsertItem(2, "Line")
        self.flag_list_ctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        group_sizer.Add(self.flag_list_ctrl, 0, wx.ALL | wx.EXPAND, 5)
        code_sizer.Add(group_sizer, 0, wx.ALL | wx.EXPAND, 10)

        main_sizer.Add(code_sizer, 0, wx.ALL | wx.EXPAND, 5)

        self.flag_detail = wx.StaticText(self, label="Select a flag to view more details")
        main_sizer.Add(self.flag_detail, 0, wx.ALL | wx.EXPAND, 20)

        self.SetSizer(main_sizer)

# flags controller
class SelectFlagsViewController(AnnotateViewControllerAbstract):
    def __init__(self, view_parent):
        super().__init__()
        self.annotation = None
        self.view = SelectFlagsView(view_parent)

        self.number_of_flags = 3
        self.line_at_index = []

        self.selected_group = None

        # Binding the buttons of the view with the handlers in controller
        self.view.group_list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.group_item_selected)
        self.view.flag_list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.flag_item_selected)
        self.view.flag_list_ctrl.Bind(wx.EVT_LIST_ITEM_CHECKED, self.flag_item_checked)
        self.view.flag_list_ctrl.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.flag_item_unchecked)

        self.view.Show()

    # Setting the self.view to be of AnnotateView type instead of just wx.panel
    def set_view(self, view: SelectFlagsView):
        self._view = view

    def get_view(self):
        return self._view

    view = property(get_view, set_view)

    def reset(self):
        self.annotation = None
        self.view.flag_detail.SetLabel("Select a flag to view more details")
        self.selected_group = None
        self.view.group_list_ctrl.DeleteAllItems()
        self.view.list_ctrl.DeleteAllItems()
        for index in range(self.number_of_flags):
            self.view.flag_list_ctrl.CheckItem(index, False)

    def update_with_annotation(self, annotation: Annotation):
        self.annotation = annotation
        self.load_content(self.annotation.source_code_path)

    def load_content(self, path):
        self.view.group_list_ctrl.DeleteAllItems()
        for i in range(1, self.annotation.number_of_groups + 1):
            self.view.group_list_ctrl.InsertItem(i, "Group %i" % i)

            self.annotation.tuple_flags.append([False] * self.number_of_flags)

    # Handling add group button press

    def group_item_selected(self, event):
        item_ind = event.GetIndex()
        self.selected_group = item_ind
        for index in range(self.number_of_flags):
            self.view.flag_list_ctrl.CheckItem(index, self.annotation.tuple_flags[self.selected_group][index])

        path = self.annotation.source_code_path
        if os.path.exists(path):
            with open(path) as fobj:
                self.view.list_ctrl.DeleteAllItems()
                # This needs more work, or maybe a better idea to make sure it shows only the lines selected
                i = 0
                j = 0
                self.line_at_index = []
                lines = [s.strip() for s in fobj.readlines()]
                for line in lines:
                    if line != "":
                        if self.annotation.line_tuple_groups[i] == self.selected_group:
                            # Adding indexes to first column
                            self.view.list_ctrl.InsertItem(j, "%i " % i)

                            # Adding lines to the second column
                            self.view.list_ctrl.SetItem(j, 1, line)
                            self.line_at_index.append(i)
                            j += 1
                        i += 1
                self.annotation.number_of_lines = i

        self.view.list_ctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.view.list_ctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)

    def flag_item_selected(self, event):
        index = event.GetIndex()
        self.view.flag_list_ctrl.Select(index, True)
        if index == 0:
            self.view.flag_detail.SetLabel("The lines of code must remain in the same relative order in the solution")
        elif index == 1:
            self.view.flag_detail.SetLabel(
                "The lines of code must remain the same distance from each other (measured in number of lines)")
        else:
            self.view.flag_detail.SetLabel("The lines of code must have the same index in the solution")

    def flag_item_checked(self, event):
        if self.selected_group is None:
            print("select a groups")
        else:
            index = event.GetIndex()
            self.view.flag_list_ctrl.Select(index, True)
            self.annotation.tuple_flags[self.selected_group][index] = True

    def flag_item_unchecked(self, event):
        if self.selected_group is None:
            print("select a groups")
        else:
            index = event.GetIndex()
            self.view.flag_list_ctrl.Select(index, True)
            self.annotation.tuple_flags[self.selected_group][index] = False


# The view that holds the pages, includes navigation between pages
class AnnotationNavigationView(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY, "Annotation", size=(900, 500))

        # Creating the sizers
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # add restart/prev/next buttons
        self.restart_btn = wx.Button(self, label="Exit")
        btn_sizer.Add(self.restart_btn, 0, wx.ALL, 10)

        self.prev_btn = wx.Button(self, label="Previous")

        btn_sizer.Add(self.prev_btn, 0, wx.ALL, 10)

        self.next_btn = wx.Button(self, label="Next")
        btn_sizer.Add(self.next_btn, 0, wx.ALL, 10)

        # finish layout
        self.mainSizer.Add(self.panelSizer, 1, wx.EXPAND)
        self.mainSizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT)
        self.SetSizer(self.mainSizer)


# The controlling class for the pages
class AnnotationNavigationController(object):
    def __init__(self, view_parent):
        super().__init__()
        # The controller has an associated view
        self.view = AnnotationNavigationView(view_parent)
        self.view.Show()

        # The array of pages and number of pages in it
        self.pages = []
        self.page_num = 0

        # The annotation object that each page will need to know about/ we are creating
        self.annotation = Annotation()

        # binding the button presses to methods
        self.view.prev_btn.Bind(wx.EVT_BUTTON, self.on_prev)
        self.view.next_btn.Bind(wx.EVT_BUTTON, self.on_next)
        self.view.restart_btn.Bind(wx.EVT_BUTTON, self.on_restart)

    def add_page(self, title_controller: AnnotateViewControllerAbstract):

        # Adding the page controller view to the panel view
        self.view.panelSizer.Add(title_controller.view, 2, wx.EXPAND)
        title_controller.update_with_annotation(self.annotation)

        # Add the controller to the list of pages
        self.pages.append(title_controller)
        self.view.Layout()
        if len(self.pages) > 1:
            # hide all panels after the first one
            title_controller.view.Hide()
            self.view.Layout()

    def on_next(self, event):
        page_count = len(self.pages)
        if page_count - 1 != self.page_num:
            self.pages[self.page_num].view.Hide()
            self.annotation = self.pages[self.page_num].annotation
            self.page_num += 1
            self.pages[self.page_num].view.Show()

            # Setting the annotation of the page controller
            self.pages[self.page_num].update_with_annotation(self.annotation)

            self.view.panelSizer.Layout()
        else:
            print("End of pages!")

        if self.view.next_btn.GetLabel() == "Finish":
            # Getting the final annotation object to be used for problem generation
            self.annotation = self.pages[self.page_num].annotation

            # close the app
            self.view.Close()

        if page_count == self.page_num + 1:
            # change label
            self.view.next_btn.SetLabel("Finish")

    def on_prev(self, event):
        if self.page_num - 1 != -1:
            self.pages[self.page_num].view.Hide()

            self.page_num -= 1
            self.pages[self.page_num].view.Show()
            self.view.panelSizer.Layout()

            # Make sure to set the other button back to next instead of finish
            self.view.next_btn.SetLabel("Next")
        else:
            print("You're already on the first page!")

    def on_restart(self, event):
        for controller in self.pages:
            controller.annotation = None
            controller.reset()
            controller.view.Hide()
            self.pages[0].view.Show()
            self.page_num = 0
            self.view.next_btn.SetLabel("Next")
            self.view.panelSizer.Layout()
            self.view.Close()

# The default view that shows up when starting the application
class ProblemSetView(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.source_info_sizer = wx.BoxSizer(wx.VERTICAL)

        student_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Adding a text box to input the number of students in the class
        select_file_text = wx.StaticText(self, label="Number of students:")
        self.text_ctrl = wx.TextCtrl(self, size=(100, 25), style=wx.TE_PROCESS_ENTER)
        self.text_ctrl.AppendText("10")
        sl = wx.StaticLine(self, 2, size=(250, 1), style=wx.LI_HORIZONTAL)

        student_sizer.Add(select_file_text, 0, wx.TOP, 2)
        student_sizer.Add(self.text_ctrl, 0, wx.LEFT, 5)
        main_sizer.Add(student_sizer, 0, wx.TOP | wx.LEFT, 10)
        main_sizer.Add(sl, 0, wx.EXPAND | wx.TOP, 10)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.del_btn = wx.Button(self, label="Delete")
        btn_sizer.Add(self.del_btn, 0, wx.ALIGN_LEFT | wx.ALL, 10)

        self.add_btn = wx.Button(self, label="Add")
        btn_sizer.Add(self.add_btn, 0, wx.ALIGN_LEFT | wx.ALL, 10)

        self.gen_btn = wx.Button(self, label="Generate")
        btn_sizer.Add(self.gen_btn, 0, wx.LEFT | wx.ALL, 10)

        main_sizer.Add(self.source_info_sizer, 1, wx.EXPAND)
        main_sizer.Add(btn_sizer, 0, wx.ALL)

        self.SetSizer(main_sizer)

# The landing page for problem set generation view controller
class ProblemSetViewController(object):
    def __init__(self, view_parent):
        super().__init__()
        self.view = ProblemSetView(view_parent)

        self.view.add_btn.Bind(wx.EVT_BUTTON, self.add_source_event)
        self.view.del_btn.Bind(wx.EVT_BUTTON, self.del_source_event)
        self.view.gen_btn.Bind(wx.EVT_BUTTON, self.gen_source_event)

        self.source_btns = []
        self.source_txts = []
        self.source_types = []
        self.source_sizers = []
        self.advance_btns = []
        self.number_of_source_blocks = 0
        self.annotations = []

        self.add_new_source()

    # This method created a new source block to be added to the main landing page
    def add_new_source(self):
        source_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        select_file_text = wx.StaticText(self.view, label="NO FILE SELECTED")
        source_sizer.Add(select_file_text, 0, wx.LEFT, 10)
        select_source_button = wx.Button(self.view, label='Select Source code')
        button_sizer.Add(select_source_button, 0, wx.LEFT, 10)

        options = ['Reordering', 'Multiple Choice', 'Find the Bug']
        choice = wx.Choice(self.view, choices=options)
        choice.Disable()
        button_sizer.Add(choice, 0, wx.LEFT, 10)

        advanced_button = wx.Button(self.view, label='Advanced')
        advanced_button.Disable()
        button_sizer.Add(advanced_button, 0, wx.LEFT, 10)

        source_sizer.Add(button_sizer, 0, wx.TOP, 10)
        self.view.source_info_sizer.Add(source_sizer, 0, wx.TOP, 15)
        self.view.Layout()

        # Binding each button to the same event handler, but passing the index of the button
        i = self.number_of_source_blocks
        select_source_button.Bind(wx.EVT_BUTTON, lambda event: self.select_source(event, i))
        advanced_button.Bind(wx.EVT_BUTTON, lambda event: self.select_advance(event, i))

        self.source_btns.append(select_source_button)
        self.source_txts.append(select_file_text)
        self.source_types.append(choice)
        self.source_sizers.append(source_sizer)
        self.advance_btns.append(advanced_button)
        self.annotations.append(Annotation())
        self.number_of_source_blocks += 1

    def add_source_event(self, event):
        self.add_new_source()

    def del_source_event(self, event):
        # Can't remove a source block when there's only one remaining
        if self.number_of_source_blocks > 1:
            self.number_of_source_blocks -= 1
            i = self.number_of_source_blocks
            self.source_txts.pop().Destroy()
            self.source_btns.pop().Destroy()
            self.source_types.pop().Destroy()
            self.advance_btns.pop().Destroy()
            self.annotations.pop()

            self.view.source_info_sizer.Remove(self.source_sizers.pop())
            self.view.source_info_sizer.Layout()
        else:
            print("Can't remove anymore")

    # Event handler for when the advanced button is selected
    def select_advance(self, event, index):
        title = "Advanced Annotation"
        top_view = wx.GetTopLevelParent(self.view)
        navigation_controller = AnnotationNavigationController(wx.GetTopLevelParent(self.view))

        select_line_view_controller = SelectLineViewController(view_parent=navigation_controller.view)

        select_tuple_view_controller = SelectTupleViewController(view_parent=navigation_controller.view)

        select_flags_view_controller = SelectFlagsViewController(view_parent=navigation_controller.view)

        # This resets the advanced selection each time. Future implementation is viewing old selections.
        navigation_controller.annotation = self.annotations[index]
        source = navigation_controller.annotation.source_code_path
        navigation_controller.annotation = Annotation()
        navigation_controller.annotation.source_code_path = source

        # Adding the view controllers to the panel controller
        navigation_controller.add_page(select_line_view_controller)
        navigation_controller.add_page(select_tuple_view_controller)
        navigation_controller.add_page(select_flags_view_controller)

        wx.GetTopLevelParent(self.view).Layout()

    # The button used to generate the problem set. This functionality has not been added yet, however it
    # Does check if input values are within expected range
    def gen_source_event(self, event):
        for annotation in self.annotations:
            if annotation.source_code_path == "":
                print("Need to specify source")
                return

        if int(self.view.text_ctrl.GetLineText(0)) <= 0:
            print("Invalid students")
            return
        print("Generating Problem Set...")
        exit(0)

    # Select source file
    def select_source(self, event, index):
        # open file explorer, save selected file
        dialog = wx.FileDialog(self.view, "Open Source File",
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_CANCEL:
            return

        # Set the annotation path to the use selected path
        self.annotations[index].source_code_path = dialog.GetPath()

        self.advance_btns[index].Enable()
        self.source_types[index].Enable()

        # display selected file
        self.source_txts[index].SetLabel("SELECTED FILE: " + dialog.GetPath())

    # Setting the controller view to be of RequestView and not just wx.Panel
    def set_view(self, view: ProblemSetView):
        self._view = view

    def get_view(self):
        return self._view

    view = property(get_view, set_view)


# The view controller for the main application.
class ApplicationViewController(wx.App):
    def __init__(self):
        super().__init__()
        self.view = AppFrame()

        problem_set_view_controller = ProblemSetViewController(view_parent=self.view)

        self.view.Layout()
        self.view.Show()


# This is the main frame (or view) of the application
class AppFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title='Creating Problem Set', size=(600, 700))

# Initial start up of the application view controller
if __name__ == '__main__':
    app = ApplicationViewController()
    app.MainLoop()
