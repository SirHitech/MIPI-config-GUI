import os
import wx


class MIPIConfigFrame(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(MIPIConfigFrame, self).__init__(*args, **kwargs)
        self.build()

    def build(self):
        """Create each of the components that live in the Frame"""

        self.build_menu()
        self.build_status_bar()
        self.build_grid()

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

        ROW_HEIGHT = 18

        main_box_sizer = wx.BoxSizer(wx.VERTICAL)
        config_grid = wx.GridBagSizer(hgap=0, vgap=0)
        horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # blank space top left
        config_grid.Add((10, ROW_HEIGHT), pos=(0, 0))

        # headers
        self.header1 = wx.StaticText(self, label="Property Name")
        config_grid.Add(self.header1, pos=(0, 1))
        self.header2 = wx.StaticText(self, label="Data Type")
        config_grid.Add(self.header2, pos=(0, 2))
        self.header3 = wx.StaticText(self, label="Value")
        config_grid.Add(self.header3, pos=(0, 3))

        # rows TODO make this dynamic based on loaded XML
        # TODO make this look prettier (centered text, more grid-like)
        for row_index in range(1, 4):
            row_label = wx.StaticText(self, label=str(row_index), size=(20, ROW_HEIGHT))
            config_grid.Add(row_label, pos=(row_index, 0))
            name_cell = wx.TextCtrl(self, size=(240, ROW_HEIGHT))
            datatype_cell = wx.TextCtrl(self, size=(140, ROW_HEIGHT))
            value_cell = wx.TextCtrl(self, size=(140, ROW_HEIGHT))
            config_grid.Add(name_cell, pos=(row_index, 1))
            config_grid.Add(datatype_cell, pos=(row_index, 2))
            config_grid.Add(value_cell, pos=(row_index, 3))

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
        file_dialogue = wx.FileDialog(self, "Choose a file", self.dir_name, "", "*.*", wx.FD_OPEN)
        if file_dialogue.ShowModal() == wx.ID_OK:
            self.filename = file_dialogue.GetFilename()
            self.dir_name = file_dialogue.GetDirectory()
            with open(os.path.join(self.dir_name, self.filename), 'r') as file:
                pass  # TODO do something
        file_dialogue.Destroy()

    def on_about(self, event):
        """A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets"""
        dlg = wx.MessageDialog(self, f"MIPI coding sample test\nAuthor: Keith Carriere", "About MIPI configuration editor", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def on_exit(self, event):
        self.Close(True)

if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = MIPIConfigFrame(None, title="MIPI configuration editor")
    frm.Show()
    app.MainLoop()