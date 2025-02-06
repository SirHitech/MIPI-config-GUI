import os
import wx
import xml.etree.ElementTree as ET


class MIPITextCtrl(wx.TextCtrl):

    def __init__(self, *args, **kw):
        self.description = kw.pop("description")
        super().__init__(*args, **kw)

class MIPIConfigFrame(wx.Frame):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.xml_tree = None
        self.build()

    def build(self):
        """Create each of the components that live in the Frame"""

        self.build_menu()
        self.build_status_bar()

    def build_menu(self):
        """
        Constructs the top menu bar that allows for user actions,
        and binds those actions to corresponding events
        """
        file_menu= wx.Menu()

        open_menu_item = file_menu.Append(wx.ID_OPEN, "&Open"," Open a config file")  # TODO what is this & for? keyboard shortcut? (does not seem to work)
        file_menu.AppendSeparator()
        about_menu_item = file_menu.Append(wx.ID_ABOUT, "&About"," Information about this program")  # TODO what is this & for? keyboard shortcut? (does not seem to work)
        exit_menu_item = file_menu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")  # TODO what is this & for? keyboard shortcut? (does not seem to work)

        menuBar = wx.MenuBar()
        menuBar.Append(file_menu,"&File")  # TODO what is this & for? keyboard shortcut? (does not seem to work)
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.on_open, open_menu_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_menu_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_menu_item)

    def build_status_bar(self):
        """
        Constructs the bottom status bar that displays status messages to the user
        """
        self.CreateStatusBar()

    def build_grid(self):

        # xml tree should have been set by opening a file first
        if not self.xml_tree:
            return

        ROW_HEIGHT = 20

        main_box_sizer = wx.BoxSizer(wx.VERTICAL)
        config_grid = wx.GridBagSizer(hgap=0, vgap=0)
        horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # blank space top left
        config_grid.Add(wx.TextCtrl(self, size=(20, ROW_HEIGHT), style=wx.TE_READONLY), pos=(0, 0))

        # headers
        self.header1 = wx.TextCtrl(self, value="Property Name", size=(240, ROW_HEIGHT), style=wx.TE_READONLY)
        config_grid.Add(self.header1, pos=(0, 1))
        self.header2 = wx.TextCtrl(self, value="Data Type", size=(140, ROW_HEIGHT), style=wx.TE_READONLY)
        config_grid.Add(self.header2, pos=(0, 2))
        self.header3 = wx.TextCtrl(self, value="Value", size=(140, ROW_HEIGHT), style=wx.TE_READONLY)
        config_grid.Add(self.header3, pos=(0, 3))

        # rows TODO make this dynamic based on loaded XML
        # TODO make this look prettier (centered text, more grid-like)
        root = self.xml_tree.getroot()
        row_index = 1
        for property in root.iter("Property"):
            row_label = wx.TextCtrl(self, value=str(row_index), size=(20, ROW_HEIGHT), style=wx.TE_READONLY)
            config_grid.Add(row_label, pos=(row_index, 0))
            name_cell = MIPITextCtrl(self, value=property.find("Name").text, size=(240, ROW_HEIGHT), style=wx.TE_READONLY, description=property.find("Description").text)
            datatype_cell =MIPITextCtrl(self, value=property.find("DataType").text, size=(140, ROW_HEIGHT), style=wx.TE_READONLY, description=property.find("Description").text)
            value_cell = MIPITextCtrl(self, value=property.find("Value").text, size=(140, ROW_HEIGHT), description=property.find("Description").text)
            config_grid.Add(name_cell, pos=(row_index, 1))
            config_grid.Add(datatype_cell, pos=(row_index, 2))
            config_grid.Add(value_cell, pos=(row_index, 3))

            name_cell.Bind(wx.EVT_ENTER_WINDOW, self.on_hover)
            name_cell.Bind(wx.EVT_LEAVE_WINDOW, self.on_unhover)
            datatype_cell.Bind(wx.EVT_ENTER_WINDOW, self.on_hover)
            datatype_cell.Bind(wx.EVT_LEAVE_WINDOW, self.on_unhover)
            value_cell.Bind(wx.EVT_ENTER_WINDOW, self.on_hover)
            value_cell.Bind(wx.EVT_LEAVE_WINDOW, self.on_unhover)

            row_index += 1

        # description box on the right
        self.description_box = wx.TextCtrl(self, size=(200,300), style=wx.TE_MULTILINE | wx.TE_READONLY)

        horizontal_sizer.Add(config_grid, 0, wx.ALL, 5)
        horizontal_sizer.Add(self.description_box)
        main_box_sizer.Add(horizontal_sizer, 0, wx.ALL, 5)
        self.SetSizerAndFit(main_box_sizer)

    ### Events

    def on_open(self, event):
        """Open a file"""
        self.dir_name = ''
        file_dialogue = wx.FileDialog(self, "Choose a file", self.dir_name, "", "*.xml", wx.FD_OPEN)
        if file_dialogue.ShowModal() == wx.ID_OK:
            self.filename = file_dialogue.GetFilename()
            self.dir_name = file_dialogue.GetDirectory()
            self.xml_tree = ET.parse(os.path.join(self.dir_name, self.filename))  # TODO does this need to be in a try block?
        file_dialogue.Destroy()

        self.build_grid()

    def on_about(self, event):
        """A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets"""
        dlg = wx.MessageDialog(self, f"MIPI coding sample test\nAuthor: Keith Carriere", "About MIPI configuration editor", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def on_hover(self, event):
        self.description_box.SetLabelText(event.EventObject.description)
        event.Skip()

    def on_unhover(self, event):
        self.description_box.SetLabelText(wx.EmptyString)
        event.Skip()

    def on_exit(self, event):
        self.Close(True)

if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = MIPIConfigFrame(None, title="MIPI configuration editor")
    frm.Show()
    app.MainLoop()