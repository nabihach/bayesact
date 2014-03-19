import wx
from cConstants import cBayesactSimConstants, cOptionSimConstants
from cNumericValidatorTextBox import cNumericValidatorTextBox



from cPlotBayesactThread import cPlotBayesactThread

class cOptionsBayesactSimPanel(wx.Panel):
    # The parent here is the cGuiTabs, which holds the gui itself and the options too
    def __init__(self, parent, iBayesactSim, iOptionsAgentPanel, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        self.m_BayesactSim = iBayesactSim
        self.m_OptionsAgentPanel = iOptionsAgentPanel

        self.m_BayesactSimThread = None


        # These are for all the options you can fill into the simulation
        ########################################################################################
        self.m_TextBoxSize = wx.DefaultSize
        self.m_ComboBoxSize = wx.DefaultSize


        wx.StaticText(self, -1, cOptionSimConstants.m_NumberOfSamples, pos=(10, 10))
        self.m_NumberOfSamplesTextBox = wx.TextCtrl(self, -1, pos=(170, 8), size=self.m_TextBoxSize,
                                                   value=str(cOptionSimConstants.m_NumberOfSamplesDefault),
                                                   validator=cNumericValidatorTextBox(iDecimals=False, iNegative=False))


        wx.StaticText(self, -1, cOptionSimConstants.m_NumberOfTrials, pos=(10, 40))
        self.m_NumberOfTrialsTextBox = wx.TextCtrl(self, -1, pos=(170, 38), size=self.m_TextBoxSize,
                                                   value=str(cOptionSimConstants.m_NumberOfTrialsDefault),
                                                   validator=cNumericValidatorTextBox(iDecimals=False, iNegative=False))


        wx.StaticText(self, -1, cOptionSimConstants.m_NumberOfExperiments, pos=(10, 70))
        self.m_NumberOfExperimentsTextBox = wx.TextCtrl(self, -1, pos=(170, 68), size=self.m_TextBoxSize,
                                                        value=str(cOptionSimConstants.m_NumberOfExperimentsDefault),
                                                        validator=cNumericValidatorTextBox(iDecimals=False, iNegative=False))


        wx.StaticText(self, -1, cOptionSimConstants.m_ClientKnowledge, pos=(10, 100))
        self.m_ClientKnowledgeChoice = wx.ComboBox(self, -1, pos=(170, 98), size=self.m_ComboBoxSize,
                                                   choices=cOptionSimConstants.m_KnowledgeChoices,
                                                   style=wx.CHOICEDLG_STYLE)
        self.m_ClientKnowledgeChoice.SetStringSelection(cOptionSimConstants.m_ClientKnowledgeDefault)


        wx.StaticText(self, -1, cOptionSimConstants.m_AgentKnowledge, pos=(10, 130))
        self.m_AgentKnowledgeChoice = wx.ComboBox(self, -1, pos=(170, 128), size=self.m_ComboBoxSize,
                                                  choices=cOptionSimConstants.m_KnowledgeChoices,
                                                  style=wx.CHOICEDLG_STYLE)
        self.m_AgentKnowledgeChoice.SetStringSelection(cOptionSimConstants.m_AgentKnowledgeDefault)


        wx.StaticText(self, -1, cOptionSimConstants.m_MaxHorizon, pos=(10, 160))
        self.m_MaxHorizonTextBox = wx.TextCtrl(self, -1, pos=(170, 158), size=self.m_TextBoxSize,
                                               value=str(cOptionSimConstants.m_MaxHorizonDefault),
                                               validator=cNumericValidatorTextBox(iDecimals=False, iNegative=False))


        wx.StaticText(self, -1, cOptionSimConstants.m_RougheningNoise, pos=(10, 220))
        self.m_RougheningNoiseTextBox = wx.TextCtrl(self, -1, pos=(170, 218), size=self.m_TextBoxSize,
                                                    value=str(cOptionSimConstants.m_RougheningNoiseDefault),
                                                    validator=cNumericValidatorTextBox(iDecimals=True, iNegative=True))


        ########################################################################################


    # To set the values of the gui to the values in bayesact
    def updateSettingsFromBayesact(self):
        self.m_NumberOfSamplesTextBox.SetValue(str(self.m_BayesactSim.num_samples))
        self.m_NumberOfTrialsTextBox.SetValue(str(self.m_BayesactSim.num_trials))
        self.m_NumberOfExperimentsTextBox.SetValue(str(self.m_BayesactSim.num_experiments))

        self.m_ClientKnowledgeChoice.SetStringSelection(str(self.m_BayesactSim.client_knowledge))
        self.m_AgentKnowledgeChoice.SetStringSelection(str(self.m_BayesactSim.agent_knowledge))

        self.m_MaxHorizonTextBox.SetValue(str(self.m_BayesactSim.max_horizon))

        self.m_RougheningNoiseTextBox.SetValue(str(self.m_BayesactSim.roughening_noise))


    # To set the values of bayesact to the values in the gui
    # Should only be used to initialize
    def updateBayesactFromSettings(self):
        self.m_BayesactSim.num_samples = int(self.m_NumberOfSamplesTextBox.GetValue())
        self.m_BayesactSim.num_trials = int(self.m_NumberOfTrialsTextBox.GetValue())
        self.m_BayesactSim.num_experiments = int(self.m_NumberOfExperimentsTextBox.GetValue())

        self.m_BayesactSim.client_knowledge = int(self.m_ClientKnowledgeChoice.GetStringSelection())
        self.m_BayesactSim.agent_knowledge = int(self.m_AgentKnowledgeChoice.GetStringSelection())

        self.m_BayesactSim.max_horizon = int(self.m_MaxHorizonTextBox.GetValue())

        self.m_BayesactSim.roughening_noise = float(self.m_RougheningNoiseTextBox.GetValue())


    def disableStartingOptions(self):
        self.m_NumberOfSamplesTextBox.Enable(False)
        self.m_NumberOfTrialsTextBox.Enable(False)
        self.m_NumberOfExperimentsTextBox.Enable(False)

        self.m_ClientKnowledgeChoice.Enable(False)
        self.m_AgentKnowledgeChoice.Enable(False)

        self.m_MaxHorizonTextBox.Enable(False)

        self.m_RougheningNoiseTextBox.Enable(False)


    def enableStartingOptions(self):
        self.m_NumberOfSamplesTextBox.Enable(True)
        self.m_NumberOfTrialsTextBox.Enable(True)
        self.m_NumberOfExperimentsTextBox.Enable(True)

        self.m_ClientKnowledgeChoice.Enable(True)
        self.m_AgentKnowledgeChoice.Enable(True)

        self.m_MaxHorizonTextBox.Enable(True)

        self.m_RougheningNoiseTextBox.Enable(True)
