import wx
from cConstants import cInstitutionsConstants, cDataFilesConstants
from cEnum import eIdentityParse, eInstitutions, eAgentListBoxParam
import unicodedata


class cIdentitiesListBox(wx.ListBox):
    def __init__(self, parent, **kwargs):
        self.m_IdentitiesData = []

        self.m_SelectedIdentity = None
        self.m_SelectedMaleSentiment = None
        self.m_SelectedFemaleSentiment = None
        self.m_SelectedInstitutions = None

        # To fill up the self.m_IdentitiesData with fidentities data
        self.initIdentitiesData()

        # LB_SINGLE is to only allow one selection at a time
        wx.ListBox.__init__(self, parent, -1,
                            choices=self.getIdentities(),
                            style=wx.LB_SINGLE, **kwargs)

        self.Bind(wx.EVT_LISTBOX, self.onSelectItem)


    def onSelectItem(self, iEvent):
        identity = str(iEvent.GetEventObject().GetStringSelection())

        selectedData = filter(lambda x : identity == x[eAgentListBoxParam.identity], self.m_IdentitiesData)[0]

        self.m_SelectedIdentity = identity
        self.m_SelectedMaleSentiment = selectedData[eAgentListBoxParam.maleSentiment]
        self.m_SelectedFemaleSentiment = selectedData[eAgentListBoxParam.femaleSentiment]
        self.m_SelectedInstitutions = selectedData[eAgentListBoxParam.institution]


    # Reads and parses fbahaviours and puts it into m_IdentitiesData
    def initIdentitiesData(self):
        stream = open(cDataFilesConstants.m_fidentities, "rU")
        for line in stream:
            line = line.rstrip().split(",")
            identity = line[eIdentityParse.identity]

            maleSentiment = []
            femaleSentiment = []
            # To extract the binary data
            institution = map(lambda x : int(x, 2),
                              filter(lambda x : x != "", line[eIdentityParse.institution].split(" ")))

            # To extract epa
            for i in range(eIdentityParse.maleEvaluation, eIdentityParse.maleActivity+1):
                maleSentiment.append(int(i))
            for i in range(eIdentityParse.femaleEvaluation, eIdentityParse.femaleActivity+1):
                femaleSentiment.append(int(i))

            # [identity, [male_e, male_p, male_a], [female_e, femle_p, female_a], [gender, institution, whatisthis]]
            self.m_IdentitiesData.append([identity, maleSentiment, femaleSentiment, institution])


    # Returns a filtered list from the original data set using a gender key and institution key
    def getFilteredInstitution(self, iGenderKey, iInstitutionKey):
        return filter(lambda x :
                      ((x[eAgentListBoxParam.institution][eInstitutions.gender] & iGenderKey) > 0) and
                      ((x[eAgentListBoxParam.institution][eInstitutions.institution] & iInstitutionKey) > 0),
                      self.m_IdentitiesData)


    # Filters data, then filters out only the identity names and sets it into contents
    def filterInstitution(self, iGenderSelection, iInstitutionSelection):
        self.SetItems(map(lambda x : x[eAgentListBoxParam.identity],
                          self.getFilteredInstitution(cInstitutionsConstants.m_GenderKey[iGenderSelection],
                                                      cInstitutionsConstants.m_InstitutionKey[iInstitutionSelection])))


    # Returns a list of the identities from the data set
    def getIdentities(self):
        return map(lambda x : x[eAgentListBoxParam.identity], self.m_IdentitiesData)

