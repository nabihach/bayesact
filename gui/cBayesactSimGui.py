import sys
sys.path.append("../")
from cConstants import cOptionSimConstants, cBayesactSimConstants
from cEnum import eEPA
import string
import unicodedata
import threading
from bayesactsim import cBayesactSim
import wx
import cPlotEPA2D
from cPlotBayesactThread import cPlotBayesactThread



class cBayesactSimGuiPanel(wx.Panel):
    # The parent here is the cGuiTabs, which holds the gui itself and the options too
    def __init__(self, parent, iOptionsAgentPanel, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        self.m_InteractantsPanel = iOptionsAgentPanel

        self.argv = [cBayesactSimConstants.m_BayesactSimFileName]
        self.m_BayesactSim = None
        self.m_BayesactSimThread = None


        # These are for all the options you can fill into the simulation
        ########################################################################################

        wx.StaticText(self, -1, cOptionSimConstants.m_NumberOfSamples, pos=(10, 10))
        self.m_NumberOfSamplesTextBox = wx.TextCtrl(self, -1, pos=(170, 8), size=(106, 20),
                                               value=str(cOptionSimConstants.m_NumberOfSamplesDefault),
                                               validator=cNumericValidator(iDecimals=False, iNegative=False))


        wx.StaticText(self, -1, cOptionSimConstants.m_NumberOfTrials, pos=(10, 40))
        self.m_NumberOfTrialsTextBox = wx.TextCtrl(self, -1, pos=(170, 38), size=(106, 20),
                                                   value=str(cOptionSimConstants.m_NumberOfTrialsDefault),
                                                   validator=cNumericValidator(iDecimals=False, iNegative=False))


        wx.StaticText(self, -1, cOptionSimConstants.m_NumberOfExperiments, pos=(10, 70))
        self.m_NumberOfExperimentsTextBox = wx.TextCtrl(self, -1, pos=(170, 68), size=(106, 20),
                                                        value=str(cOptionSimConstants.m_NumberOfExperimentsDefault),
                                                        validator=cNumericValidator(iDecimals=False, iNegative=False))


        wx.StaticText(self, -1, cOptionSimConstants.m_ClientKnowledge, pos=(10, 100))
        self.m_ClientKnowledgeChoice = wx.Choice(self, -1, pos=(170, 98), size=(106, 20),
                                                 choices=cOptionSimConstants.m_KnowledgeChoices,
                                                 style=wx.CHOICEDLG_STYLE)
        self.m_ClientKnowledgeChoice.SetStringSelection(cOptionSimConstants.m_ClientKnowledgeDefault)


        wx.StaticText(self, -1, cOptionSimConstants.m_AgentKnowledge, pos=(10, 130))
        self.m_AgentKnowledgeChoice = wx.Choice(self, -1, pos=(170, 128), size=(106, 20),
                                                choices=cOptionSimConstants.m_KnowledgeChoices,
                                                style=wx.CHOICEDLG_STYLE)
        self.m_AgentKnowledgeChoice.SetStringSelection(cOptionSimConstants.m_AgentKnowledgeDefault)


        wx.StaticText(self, -1, cOptionSimConstants.m_MaxHorizon, pos=(10, 160))
        self.m_MaxHorizonTextBox = wx.TextCtrl(self, -1, pos=(170, 158), size=(106, 20),
                                               value=str(cOptionSimConstants.m_MaxHorizonDefault),
                                               validator=cNumericValidator(iDecimals=False, iNegative=False))


        wx.StaticText(self, -1, cOptionSimConstants.m_UniformDraws, pos=(10, 190))
        self.m_UniformDrawsChoice = wx.Choice(self, -1, pos=(170, 188), size=(106, 20),
                                              choices=cOptionSimConstants.m_UniformDrawsChoices,
                                              style=wx.CHOICEDLG_STYLE)
        self.m_UniformDrawsChoice.SetStringSelection(cOptionSimConstants.m_UniformDrawsDefault)


        wx.StaticText(self, -1, cOptionSimConstants.m_RougheningNoise, pos=(10, 220))
        self.m_RougheningNoiseTextBox = wx.TextCtrl(self, -1, pos=(170, 218), size=(106, 20),
                                                    value=str(cOptionSimConstants.m_RougheningNoiseDefault),
                                                    validator=cNumericValidator(iDecimals=True, iNegative=True))


        wx.StaticText(self, -1, cOptionSimConstants.m_EnvironmentNoise, pos=(10, 250))
        self.m_EnvironmentNoiseTextBox = wx.TextCtrl(self, -1, pos=(170, 248), size=(106, 20),
                                                     value=str(cOptionSimConstants.m_RougheningNoiseDefault),
                                                     validator=cNumericValidator(iDecimals=True, iNegative=True))


        wx.StaticText(self, -1, cOptionSimConstants.m_GammaValue, pos=(10, 280))
        self.m_GammaValueTextBox = wx.TextCtrl(self, -1, pos=(170, 278), size=(106, 20),
                                               value=str(cOptionSimConstants.m_RougheningNoiseDefault),
                                               validator=cNumericValidator(iDecimals=True, iNegative=True))


        wx.StaticText(self, -1, cOptionSimConstants.m_ClientGender, pos=(10, 310))
        self.m_ClientGenderChoice = wx.Choice(self, -1, pos=(170, 308), size=(106, 20),
                                              choices=cOptionSimConstants.m_GenderChoices,
                                              style=wx.CHOICEDLG_STYLE)
        self.m_ClientGenderChoice.SetStringSelection(cOptionSimConstants.m_ClientGenderDefault)


        wx.StaticText(self, -1, cOptionSimConstants.m_AgentGender, pos=(10, 340))
        self.m_AgentGenderChoice = wx.Choice(self, -1, pos=(170, 338), size=(106, 20),
                                             choices=cOptionSimConstants.m_GenderChoices,
                                             style=wx.CHOICEDLG_STYLE)
        self.m_AgentGenderChoice.SetStringSelection(cOptionSimConstants.m_AgentGenderDefault)


        ########################################################################################


        self.m_StartButton = wx.Button(self, -1, label="Start", pos=(10, 370), size=(190, 20))
        self.m_StartButton.Bind(wx.EVT_BUTTON, self.onStartBayesactSim)

        self.m_PlotEPAPanel2D_A = cPlotEPA2D.cPlotPanel(self,
                                                        iXAxisItem=eEPA.evaluation,
                                                        iYAxisItem=eEPA.potency,
                                                        pos=(400, 0), size=(500, 300))

        self.m_PlotEPAPanel2D_B = cPlotEPA2D.cPlotPanel(self,
                                                        iXAxisItem=eEPA.activity,
                                                        iYAxisItem=eEPA.potency,
                                                        pos=(400, 350), size=(500, 300))


        self.m_PauseButton = wx.Button(self, -1, label="Pause", pos=(10, 400), size=(190, 20))
        self.m_PauseButton.Bind(wx.EVT_BUTTON, self.onPauseBayesactSim)

        self.m_ResumeButton = wx.Button(self, -1, label="Resume", pos=(10, 430), size=(190, 20))
        self.m_ResumeButton.Bind(wx.EVT_BUTTON, self.onResumeBayesactSim)

        self.m_StopButton = wx.Button(self, -1, label="Stop", pos=(10, 460), size=(190, 20))
        self.m_StopButton.Bind(wx.EVT_BUTTON, self.onCloseThread)


        wx.StaticText(self, -1, "Green:", pos=(10, 500))
        wx.StaticText(self, -1, "What client thinks of themselves", pos=(70, 500))

        wx.StaticText(self, -1, "Pink:", pos=(10, 520))
        wx.StaticText(self, -1, "What client thinks of agent", pos=(70, 520))

        wx.StaticText(self, -1, "Yellow:", pos=(10, 540))
        wx.StaticText(self, -1, "What agent thinks of themselves", pos=(70, 540))

        wx.StaticText(self, -1, "Blue:", pos=(10, 560))
        wx.StaticText(self, -1, "What agent thinks of client", pos=(70, 560))

        self.m_BayesactSim = cBayesactSim(self.argv)
        self.updateSettingsFromBayesact()




    def onValueChange(self, iEvent):
        print iEvent.GetEventObject().GetValue()


    # To set the values of the gui to the values in bayesact
    def updateSettingsFromBayesact(self):
        self.m_NumberOfSamplesTextBox.SetValue(str(self.m_BayesactSim.num_samples))
        self.m_NumberOfTrialsTextBox.SetValue(str(self.m_BayesactSim.num_trials))
        self.m_NumberOfExperimentsTextBox.SetValue(str(self.m_BayesactSim.num_experiments))

        self.m_ClientKnowledgeChoice.SetStringSelection(str(self.m_BayesactSim.client_knowledge))
        self.m_AgentKnowledgeChoice.SetStringSelection(str(self.m_BayesactSim.agent_knowledge))

        self.m_MaxHorizonTextBox.SetValue(str(self.m_BayesactSim.max_horizon))
        self.m_UniformDrawsChoice.SetStringSelection(str(self.m_BayesactSim.uniform_draws))

        self.m_RougheningNoiseTextBox.SetValue(str(self.m_BayesactSim.roughening_noise))
        self.m_EnvironmentNoiseTextBox.SetValue(str(self.m_BayesactSim.env_noise))
        self.m_GammaValueTextBox.SetValue(str(self.m_BayesactSim.gamma_value))

        self.m_ClientGenderChoice.SetStringSelection(self.m_BayesactSim.client_gender)
        self.m_AgentGenderChoice.SetStringSelection(self.m_BayesactSim.agent_gender)


    # To set the values of bayesact to the values in the gui
    def updateBayesactFromSettings(self):
        self.m_BayesactSim.num_samples = int(self.m_NumberOfSamplesTextBox.GetValue())
        self.m_BayesactSim.num_trials = int(self.m_NumberOfTrialsTextBox.GetValue())
        self.m_BayesactSim.num_experiments = int(self.m_NumberOfExperimentsTextBox.GetValue())

        self.m_BayesactSim.client_knowledge = int(self.m_ClientKnowledgeChoice.GetStringSelection())
        self.m_BayesactSim.agent_knowledge = int(self.m_AgentKnowledgeChoice.GetStringSelection())
        self.m_BayesactSim.max_horizon = int(self.m_MaxHorizonTextBox.GetValue())
        self.m_BayesactSim.uniform_draws = bool(self.m_UniformDrawsChoice.GetStringSelection())

        self.m_BayesactSim.roughening_noise = float(self.m_RougheningNoiseTextBox.GetValue())
        self.m_BayesactSim.env_noise = float(self.m_EnvironmentNoiseTextBox.GetValue())
        self.m_BayesactSim.gamma_value = float(self.m_GammaValueTextBox.GetValue())

        self.m_BayesactSim.client_gender = str(self.m_ClientGenderChoice.GetStringSelection())
        self.m_BayesactSim.agent_gender = str(self.m_AgentGenderChoice.GetStringSelection())

        self.m_BayesactSim.client_id_label = str(self.m_InteractantsPanel.m_ClientIdentityTextBox.GetValue())
        self.m_BayesactSim.agent_id_label = str(self.m_InteractantsPanel.m_AgentIdentityTextBox.GetValue())


    # Will disable ability to update number of samples, trials, experiments and max horizon
    # Uniform draws doesn't seem to do anything
    # Knowledge cannot be set again since it is also something initialized at the beginning
    # Cannot update gender after it has been set due to initialization of tdynamic files
    def disableStartingOptions(self):
        self.m_NumberOfSamplesTextBox.Enable(False)
        self.m_NumberOfTrialsTextBox.Enable(False)
        self.m_NumberOfExperimentsTextBox.Enable(False)

        self.m_ClientKnowledgeChoice.Enable(False)
        self.m_AgentKnowledgeChoice.Enable(False)

        self.m_MaxHorizonTextBox.Enable(False)
        self.m_UniformDrawsChoice.Enable(False)

        self.m_ClientGenderChoice.Enable(False)
        self.m_AgentGenderChoice.Enable(False)


    def enableStartingOptions(self):
        self.m_NumberOfSamplesTextBox.Enable(True)
        self.m_NumberOfTrialsTextBox.Enable(True)
        self.m_NumberOfExperimentsTextBox.Enable(True)

        self.m_ClientKnowledgeChoice.Enable(True)
        self.m_AgentKnowledgeChoice.Enable(True)

        self.m_MaxHorizonTextBox.Enable(True)
        self.m_UniformDrawsChoice.Enable(True)

        self.m_RougheningNoiseTextBox.Enable(True)
        self.m_EnvironmentNoiseTextBox.Enable(True)
        self.m_GammaValueTextBox.Enable(True)

        self.m_ClientGenderChoice.Enable(True)
        self.m_AgentGenderChoice.Enable(True)


    def onCloseThread(self, iEvent=None):
        if (None != self.m_BayesactSimThread):
            self.m_BayesactSim.threadEvent.set()
            self.m_BayesactSim.terminateFlag = True
            self.m_BayesactSimThread.join()
            self.m_BayesactSimThread = None
            self.enableStartingOptions()


    def onStartBayesactSim(self, iEvent):
        self.m_StartButton.SetLabel("Restart")
        self.onCloseThread()

        self.disableStartingOptions()

        plotter = cPlotBayesactThread()

        plotter.initPlotBayesactSim(self.m_PlotEPAPanel2D_A)
        plotter.addPanel(self.m_PlotEPAPanel2D_B)

        self.m_BayesactSim.plotter=plotter
        self.m_BayesactSim.terminateFlag = False

        self.m_BayesactSimThread = threading.Thread(target=self.m_BayesactSim.startBayesactSim)

        self.m_BayesactSim.threadEvent = threading.Event()
        self.onResumeBayesactSim()

        plotter.setThread(self.m_BayesactSimThread)
        plotter.startThread()



    def onPauseBayesactSim(self, iEvent=None):
        self.m_RougheningNoiseTextBox.Enable(True)
        self.m_EnvironmentNoiseTextBox.Enable(True)
        self.m_GammaValueTextBox.Enable(True)

        # Queues up a pause event for the thread, the program will pause when it hits its threadEvent.wait()
        self.m_BayesactSim.threadEvent.clear()
        # You can also update alpha and beta values here


    def onResumeBayesactSim(self, iEvent=None):
        self.m_RougheningNoiseTextBox.Enable(False)
        self.m_EnvironmentNoiseTextBox.Enable(False)
        self.m_GammaValueTextBox.Enable(False)

        # Wait until the program finishes whatever it is doing, then update values
        while (not(self.m_BayesactSim.waiting)):
            pass

        self.updateBayesactFromSettings()

        # Will resume thread if it is waiting
        self.m_BayesactSim.threadEvent.set()




class cNumericValidator(wx.PyValidator):
    def __init__(self, iDecimals=True, iNegative=True):
        wx.PyValidator.__init__(self)

        self.m_AllowDecimals = iDecimals
        self.m_AllowNegatives = iNegative

        self.Bind(wx.EVT_CHAR, self.onChar)

    def Clone(self):
        return cNumericValidator(iDecimals=self.m_AllowDecimals, iNegative=self.m_AllowNegatives)

    def Validate(self, win):
        textctrl = self.GetWindow()
        value = textctrl.GetValue()

        if ("" == value):
            return True

        return self.isNumeric(value)


    def onChar(self, iEvent):
        key = iEvent.GetKeyCode()
        value = self.GetWindow().GetValue()
        cursorIndex = self.GetWindow().GetInsertionPoint()

        # Allow spaces and backspaces
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            iEvent.Skip()
            return

        # Allow numbers
        if (chr(key) in string.digits):
            iEvent.Skip()
            return
        # Allow hyphen for negative numbers if cursor is at beginning and no other hyphens exists
        if (self.m_AllowDecimals and (chr(key) == "-") and (0 == cursorIndex) and (not("-" in value))):
            iEvent.Skip()
            return
        # Allow period for decimals if no other periods events
        elif (self.m_AllowNegatives and (chr(key) == ".") and (not("." in value))):
            iEvent.Skip()
            return
        return

    def isNumeric(iString):
        try:
            float(iString)
            return True
        except ValueError:
            pass

        try:
            unicodedata.numeric(iString)
            return True
        except (TypeError, ValueError):
            pass

        return False
