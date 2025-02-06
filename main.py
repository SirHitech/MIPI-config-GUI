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
        self.xmlTree = None
        self.Build()

    def Build(self):
        """Create each of the components that live in the Frame"""

        self.BuildMenu()
        self.BuildStatusBar()

    def BuildMenu(self):
        """
        Constructs the top menu bar that allows for user actions,
        and binds those actions to corresponding events
        """
        fileMenu= wx.Menu()

        openMenuItem = fileMenu.Append(wx.ID_OPEN, "&Open"," Open a config file")  # TODO what is this & for? keyboard shortcut? (does not seem to work)
        fileMenu.AppendSeparator()
        aboutMenuItem = fileMenu.Append(wx.ID_ABOUT, "&About"," Information about this program")  # TODO what is this & for? keyboard shortcut? (does not seem to work)
        exitMenuItem = fileMenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")  # TODO what is this & for? keyboard shortcut? (does not seem to work)

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu,"&File")  # TODO what is this & for? keyboard shortcut? (does not seem to work)
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnOpen, openMenuItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutMenuItem)
        self.Bind(wx.EVT_MENU, self.OnExit, exitMenuItem)

    def BuildStatusBar(self):
        """
        Constructs the bottom status bar that displays status messages to the user
        """
        self.CreateStatusBar()

    def BuildGrid(self):

        # xml tree should have been set by opening a file first
        if not self.xmlTree:
            return

        ROW_HEIGHT = 20

        mainBoxSizer = wx.BoxSizer(wx.VERTICAL)
        configGrid = wx.GridBagSizer(hgap=0, vgap=0)
        horizontalSizer = wx.BoxSizer(wx.HORIZONTAL)

        # blank space top left
        configGrid.Add(wx.TextCtrl(self, size=(20, ROW_HEIGHT), style=wx.TE_READONLY), pos=(0, 0))

        # headers
        self.header1 = wx.TextCtrl(self, value="Property Name", size=(240, ROW_HEIGHT), style=wx.TE_READONLY)
        configGrid.Add(self.header1, pos=(0, 1))
        self.header2 = wx.TextCtrl(self, value="Data Type", size=(140, ROW_HEIGHT), style=wx.TE_READONLY)
        configGrid.Add(self.header2, pos=(0, 2))
        self.header3 = wx.TextCtrl(self, value="Value", size=(140, ROW_HEIGHT), style=wx.TE_READONLY)
        configGrid.Add(self.header3, pos=(0, 3))

        # TODO make this look prettier (centered text, more grid-like)
        root = self.xmlTree.getroot()
        rowIndex = 1
        for property in root.iter("Property"):
            rowLabel = wx.TextCtrl(self, value=str(rowIndex), size=(20, ROW_HEIGHT), style=wx.TE_READONLY)
            configGrid.Add(rowLabel, pos=(rowIndex, 0))
            nameCell = MIPITextCtrl(self, value=property.find("Name").text, size=(240, ROW_HEIGHT), style=wx.TE_READONLY, description=property.find("Description").text)
            datatypeCell = MIPITextCtrl(self, value=property.find("DataType").text, size=(140, ROW_HEIGHT), style=wx.TE_READONLY, description=property.find("Description").text)
            valueCell = MIPITextCtrl(self, value=property.find("Value").text, size=(140, ROW_HEIGHT), description=property.find("Description").text)
            configGrid.Add(nameCell, pos=(rowIndex, 1))
            configGrid.Add(datatypeCell, pos=(rowIndex, 2))
            configGrid.Add(valueCell, pos=(rowIndex, 3))

            nameCell.Bind(wx.EVT_ENTER_WINDOW, self.OnHover)
            nameCell.Bind(wx.EVT_LEAVE_WINDOW, self.OnUnhover)
            datatypeCell.Bind(wx.EVT_ENTER_WINDOW, self.OnHover)
            datatypeCell.Bind(wx.EVT_LEAVE_WINDOW, self.OnUnhover)
            valueCell.Bind(wx.EVT_ENTER_WINDOW, self.OnHover)
            valueCell.Bind(wx.EVT_LEAVE_WINDOW, self.OnUnhover)

            rowIndex += 1

        # description box on the right
        self.descriptionBox = wx.TextCtrl(self, size=(200,300), style=wx.TE_MULTILINE | wx.TE_READONLY)

        horizontalSizer.Add(configGrid, 0, wx.ALL, 5)
        horizontalSizer.Add(self.descriptionBox)
        mainBoxSizer.Add(horizontalSizer, 0, wx.ALL, 5)
        self.SetSizerAndFit(mainBoxSizer)

    ### Events

    def OnOpen(self, event):
        """Open a file"""
        self.directoryName = ''
        fileDialogue = wx.FileDialog(self, "Choose a file", self.directoryName, "", "*.xml", wx.FD_OPEN)
        if fileDialogue.ShowModal() == wx.ID_OK:
            self.filename = fileDialogue.GetFilename()
            self.directoryName = fileDialogue.GetDirectory()
            self.xmlTree = ET.parse(os.path.join(self.directoryName, self.filename))  # TODO does this need to be in a try block?
        fileDialogue.Destroy()

        self.BuildGrid()

    def OnAbout(self, event):
        """A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets"""
        dlg = wx.MessageDialog(self, f"MIPI coding sample test\nAuthor: Keith Carriere", "About MIPI configuration editor", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnHover(self, event):
        self.descriptionBox.SetLabelText(event.EventObject.description)
        event.Skip()

    def OnUnhover(self, event):
        self.descriptionBox.SetLabelText(wx.EmptyString)
        event.Skip()

    def OnExit(self, event):
        self.Close(True)

if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = MIPIConfigFrame(None, title="MIPI configuration editor")
    frm.Show()
    app.MainLoop()