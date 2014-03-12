import wx
from cIdentitiesListBox import cIdentitiesListBox
#from cEnum importeIdentityParse
from cConstants import cInstitutionsConstants, cOptionsAgentConstants


# This is the panel where you define the interactants
class cOptionsAgentPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)


        wx.StaticText(self, -1, "Identities", pos=(10, 10))
        self.m_IdentityListBox = cIdentitiesListBox(self, pos=(10, 40), size=(190, 468))


        wx.StaticText(self, -1, "Gender", pos=(210, 35))
        self.m_GenderChoice = wx.Choice(self, -1, pos=(210, 65), size=(106, 20),
                                             choices=cInstitutionsConstants.m_Gender,
                                             style=wx.CHOICEDLG_STYLE)
        self.m_GenderChoice.Bind(wx.EVT_CHOICE, self.onSelectInstitution)


        wx.StaticText(self, -1, "Institution", pos=(210, 135))
        self.m_InstitutionChoice = wx.Choice(self, -1, pos=(210, 165), size=(106, 20),
                                             choices=cInstitutionsConstants.m_Institution,
                                             style=wx.CHOICEDLG_STYLE)
        self.m_InstitutionChoice.Bind(wx.EVT_CHOICE, self.onSelectInstitution)

        # To have a choice between being a confuser or not
        if (True == cOptionsAgentConstants.m_ClientMultipleIdentity):
            wx.StaticText(self, -1, "Client Identites", pos=(420, 10))
            self.m_ClientIdentityListBox = wx.ListBox(self, -1, pos=(420, 40), size=(190, 250),
                                                      choices=[],
                                                      style=wx.LB_SINGLE)
            self.m_AddClientIdentityButton = wx.Button(self, label="Add Identity", pos=(412, 290), size=(190, 20))
            self.m_DeleteClientIdentityButton = wx.Button(self, label="Delete Identity", pos=(412, 320), size=(190, 20))

            self.m_AddClientIdentityButton.Bind(wx.EVT_BUTTON, self.onAddClientIdentity)
            self.m_DeleteClientIdentityButton.Bind(wx.EVT_BUTTON, self.onDeleteClientIdentity)

        else:
            wx.StaticText(self, -1, "Client Identity", pos=(420, 10))
            self.m_ClientIdentityTextBox = wx.TextCtrl(self, pos=(420, 40), size=(190, 22),
                                                      style=wx.TE_READONLY)
            self.m_SetClientIdentityButton = wx.Button(self, label="Set Identity", pos=(412, 70), size=(190, 20))

            self.m_SetClientIdentityButton.Bind(wx.EVT_BUTTON, self.onSetClient)


        wx.StaticText(self, -1, "Agent Identity", pos=(420, 420))
        self.m_AgentIdentityTextBox = wx.TextCtrl(self, pos=(418,450), size=(190, 22),
                                                  style=wx.TE_READONLY)
        self.m_SetAgentIdentityButton = wx.Button(self, label="Set Identity", pos=(412, 480), size=(190, 20))
        self.m_SetAgentIdentityButton.Bind(wx.EVT_BUTTON, self.onSetAgent)




    # Adds to client identity, you only use this when the client can have more than one identity, for now we'll only allow one
    def onAddClientIdentity(self, iEvent):
        index = self.m_ClientIdentityListBox.GetSelection()
        identity = self.m_IdentityListBox.GetStringSelection()

        if ("" == identity):
            return

        # Check for duplicates
        if (identity in self.m_ClientIdentityListBox.GetItems()):
            return

        # If nothing is selected on the client identity list box, insert to end, else insert after whatever is selected
        if (-1 == index):
            self.m_ClientIdentityListBox.InsertItems(items=[identity], pos=self.m_ClientIdentityListBox.GetCount())
        else:
            self.m_ClientIdentityListBox.InsertItems(items=[identity], pos=index+1)


    def onDeleteClientIdentity(self, iEvent):
        index = self.m_ClientIdentityListBox.GetSelection()
        currentItems = self.m_ClientIdentityListBox.GetItems()

        if (0 == len(currentItems)):
            return

        currentItems.pop(index)
        self.m_ClientIdentityListBox.SetItems(currentItems)


    def onSetClient(self, iEvent):
        identity = self.m_IdentityListBox.GetStringSelection()
        self.m_ClientIdentityTextBox.SetValue(identity)


    def onSetAgent(self, iEvent):
        identity = self.m_IdentityListBox.GetStringSelection()
        self.m_AgentIdentityTextBox.SetValue(identity)


    def onSelectInstitution(self, iEvent):
        self.m_IdentityListBox.filterInstitution(self.m_GenderChoice.GetSelection(),
                                                 self.m_InstitutionChoice.GetSelection())


class cDefaultFrame(wx.Frame):
    def __init__(self, parent, **kwargs):
        wx.Frame.__init__(self, parent, **kwargs)
        self.setAgentPanel1 = cOptionsAgentPanel(self, style=wx.NO_BORDER, pos=(0, 0), size=(1000, 700))

if __name__ == "__main__":
    app = wx.App(redirect=False)
    frame = cDefaultFrame(None, title="Title", size=(1000, 700))
    frame.Show()
    app.MainLoop()
