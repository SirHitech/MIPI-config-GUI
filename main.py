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