import argparse
import logging
import os
import wx
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description="Set the logging level via command line")
parser.add_argument('--log', default='WARNING', help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
args = parser.parse_args()

numeric_level = getattr(logging, args.log.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % args.log)
logging.basicConfig(level=numeric_level, format='%(levelname)s: %(message)s')


class MIPITextCtrl(wx.TextCtrl):
    """wx.TextCtrl extension to allow storing a description that will display on mouseover"""

    def __init__(self, *args, **kw):
        self.description = kw.pop("description")
        super().__init__(*args, **kw)

class MIPIConfigFrame(wx.Frame):
    """
    wx.Frame that houses various wx components to display information about loaded xml configs
    TODO support editing and saving configurations
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.xmlTree = None
        self.mainGrid = None
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

        openMenuItem = fileMenu.Append(wx.ID_OPEN, "&Open\tCtrl+O"," Open a config file")
        fileMenu.AppendSeparator()
        aboutMenuItem = fileMenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        exitMenuItem = fileMenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu,"&File")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnOpen, openMenuItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutMenuItem)
        self.Bind(wx.EVT_MENU, self.OnExit, exitMenuItem)

    def BuildStatusBar(self):
        """Constructs the bottom status bar that displays status messages to the user"""

        self.CreateStatusBar()
        self.SetStatusText("Open a config file to begin")

    def BuildGrid(self):
        """
        Construct the main grid that displays the loaded configuration to the user
        Removes old grid, if present
        """

        if self.mainGrid:
            self.mainGrid.Clear(True)
            self.mainGrid.Layout()
            self.horizontalSizer.Clear(True)
            self.horizontalSizer.Layout()
            self.Refresh()

        # xml tree should have been set by opening a file first
        if not self.xmlTree:
            logging.debug("BuildGrid attempted without an xmlTree, aborting")
            return

        ROW_HEIGHT = 20

        self.mainGrid = wx.GridBagSizer(hgap=0, vgap=0)

        # blank space top left
        self.mainGrid.Add(wx.TextCtrl(self, size=(20, ROW_HEIGHT), style=wx.TE_READONLY), pos=(0, 0))

        # headers
        nameHeader = wx.TextCtrl(self, value="Property Name", size=(240, ROW_HEIGHT), style=wx.TE_READONLY)
        self.mainGrid.Add(nameHeader, pos=(0, 1))
        datatypeHeader = wx.TextCtrl(self, value="Data Type", size=(140, ROW_HEIGHT), style=wx.TE_READONLY)
        self.mainGrid.Add(datatypeHeader, pos=(0, 2))
        valueHeader = wx.TextCtrl(self, value="Value", size=(140, ROW_HEIGHT), style=wx.TE_READONLY)
        self.mainGrid.Add(valueHeader, pos=(0, 3))

        # TODO make this look prettier (centered text, more grid-like)
        # one row per property from the loaded xml configuration
        rowIndex = 1
        root = self.xmlTree.getroot()
        for property in root.iter("Property"):
            rowLabel = wx.TextCtrl(self, value=str(rowIndex), size=(20, ROW_HEIGHT), style=wx.TE_READONLY)
            self.mainGrid.Add(rowLabel, pos=(rowIndex, 0))

            description = getattr(property.find("Description"), "text", "") or "(no description provided)"

            nameCell = MIPITextCtrl(
                self,
                value=getattr(property.find("Name"), "text", "") or "",
                size=(240, ROW_HEIGHT),
                style=wx.TE_READONLY,
                description=description,
            )
            datatypeCell = MIPITextCtrl(
                self,
                value=getattr(property.find("DataType"), "text", "") or "",
                size=(140, ROW_HEIGHT),
                style=wx.TE_READONLY,
                description=description,
            )
            valueCell = MIPITextCtrl(
                self,
                value=getattr(property.find("Value"), "text", "") or "",
                size=(140, ROW_HEIGHT),
                description=description,
            )

            self.mainGrid.Add(nameCell, pos=(rowIndex, 1))
            self.mainGrid.Add(datatypeCell, pos=(rowIndex, 2))
            self.mainGrid.Add(valueCell, pos=(rowIndex, 3))

            nameCell.Bind(wx.EVT_ENTER_WINDOW, self.OnHoverCellWithDescription)
            nameCell.Bind(wx.EVT_LEAVE_WINDOW, self.OnUnhoverCellWithDescription)
            datatypeCell.Bind(wx.EVT_ENTER_WINDOW, self.OnHoverCellWithDescription)
            datatypeCell.Bind(wx.EVT_LEAVE_WINDOW, self.OnUnhoverCellWithDescription)
            valueCell.Bind(wx.EVT_ENTER_WINDOW, self.OnHoverCellWithDescription)
            valueCell.Bind(wx.EVT_LEAVE_WINDOW, self.OnUnhoverCellWithDescription)

            rowIndex += 1

        # description box on the right
        self.descriptionBox = wx.TextCtrl(self, size=(200, 200), style=wx.TE_MULTILINE | wx.TE_READONLY)

        self.horizontalSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.horizontalSizer.Add(self.mainGrid, 0, wx.ALL, 5)
        self.horizontalSizer.Add(self.descriptionBox)
        self.SetSizerAndFit(self.horizontalSizer)

        self.Layout()

    def _OpenAndStoreXMLFile(self):
        """Open the file selection modal, and read the file into an XML tree"""

        self.directoryName = ''
        fileDialogue = wx.FileDialog(self, "Choose a file", self.directoryName, "", "*.xml", wx.FD_OPEN)

        if fileDialogue.ShowModal() == wx.ID_OK:
            self.filename = fileDialogue.GetFilename()
            self.directoryName = fileDialogue.GetDirectory()
            filePath = os.path.join(self.directoryName, self.filename)

            logging.info(f"Starting parse of file: {filePath}")
            try:
                self.xmlTree = ET.parse(filePath)
            except ET.ParseError as parseError:
                errorMessage = f"ParseError occurred while reading XML file {filePath}: {parseError.msg}"
                logging.debug(errorMessage)
                self.SetStatusText(errorMessage)
                errorDialogue = wx.MessageDialog(self, errorMessage, "Error", wx.OK)
                errorDialogue.ShowModal()
                errorDialogue.Destroy()
                fileDialogue.Destroy()
                return

            logging.info(f"File parsing complete")
            self.SetStatusText(f"Loaded file {self.filename}")
        fileDialogue.Destroy()

    ### Events

    def OnOpen(self, event):
        """
        Prompt the user to select an XML file, store the contents, and build the grid display
        Triggered when the app is initially run, or from the 'Open' menu option
        """

        self._OpenAndStoreXMLFile()
        self.BuildGrid()

    def OnAbout(self, event):
        """
        Display a message dialog box with some info about the app
        Triggered from the 'About' menu option
        """

        messageDialogue = wx.MessageDialog(self, "MIPI coding sample test by Keith Carriere", "About MIPI configuration editor", wx.OK)
        messageDialogue.ShowModal()
        messageDialogue.Destroy()

    def OnHoverCellWithDescription(self, event):
        """Display the Property's description on the box to the right of the grid"""

        if event.EventObject and not hasattr(event.EventObject, "description"):
            logging.debug(f"EventObject {event.EventObject.__class__.__name__} bound to OnHoverCellWithDescription without a description")
            event.Skip()
            return
        self.descriptionBox.SetLabelText(event.EventObject.description)
        event.Skip()

    def OnUnhoverCellWithDescription(self, event):
        """Clear out the description on the box to the right of the grid"""

        self.descriptionBox.SetLabelText(wx.EmptyString)
        event.Skip()

    def OnExit(self, event):
        """
        Terminate the application
        Triggered from the 'Exit' menu option
        """

        self.Close(True)

if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop
    app = wx.App()
    frm = MIPIConfigFrame(None, title="MIPI configuration editor")
    frm.Show()
    app.MainLoop()