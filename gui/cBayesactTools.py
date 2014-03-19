import sys
sys.path.append("../")
from bayesact import *
import getopt
import cProfile
from cEnum import eTurn
from cBayesactSimGui import cBayesactSimGuiPanel

class cBayesactTools(object):
    def __init__(self):
        #NP.set_printoptions(precision=5)
        #NP.set_printoptions(suppress=True)
        NP.set_printoptions(linewidth=10000)


        #get some key parameters from the command line
        self.num_samples=1000

        #agent knowledge of client id:
        #0 : nothing
        #1 : one of a selection of  num_confusers+1 randoms
        #2 : exactly
        #3 : same as 0 but also agent does not know its own id
        self.agent_knowledge=0
        #client knowledge of agent id:
        self.client_knowledge=0

        self.agent_id_label=""
        self.client_id_label=""

        self.agent_gender="male"
        self.client_gender="male"

        #used only for label extraction if the user enters a label they want to use for simulations
        self.identities_filename="fidentities.dat"

        self.behaviours_filenmae="fbehaviours.dat"   #not used

        #uniform draws - if true will draw client IDs uniformly over -4.3,4.3.
        #If false, drawn from Normal distribution of the client ids in the database
        self.uniform_draws=False

        self.gamma_value=1.0

        #if>0, add a small amount of roughening noise to the client identities
        self.roughening_noise=-1.0


        #environment noise: this will corrupt the transmission of the actions with zero-mean Gaussian noise with this variance
        self.env_noise=0.0

        self.max_horizon=50

        self.num_trials=20
        self.num_experiments=10

        self.get_full_id_rate=20

        self.learn_init_turn="agent"
        self.simul_init_turn="client"

        self.verbose=False

        if self.roughening_noise<0.0:
            #default
            self.roughening_noise=self.num_samples**(-1.0/3.0)


        #-----------------------------------------------------------------------------------------------------------------------------
        #simulation start
        #-----------------------------------------------------------------------------------------------------------------------------

        self.num_agent_confusers=3
        self.num_client_confusers=3



        #to roughen, not use proposal  - for any unknown identity
        self.learn_agent_rough=0.0
        self.learn_client_rough=0.0

        if (self.agent_knowledge==0 or self.agent_knowledge==3) and self.roughening_noise>0:
            self.learn_client_rough=self.roughening_noise
            if self.agent_knowledge==3:
                self.learn_agent_rough=self.roughening_noise

        self.simul_agent_rough=0.0
        self.simul_client_rough=0.0
        if (self.client_knowledge==0 or self.client_knowledge==3) and self.roughening_noise>0:
            self.simul_client_rough=self.roughening_noise
            if self.client_knowledge==3:
                self.simul_agent_rough=self.roughening_noise



        self.simul_verbose=self.verbose
        self.learn_verbose=self.verbose

        self.meanlearndefl =[]
        self.meansimuldefl = []
        self.meanlearnddvo = []
        self.meansimulddvo = []

        #the mean and covariance of IDs for male agents as taken from the databases
        #should do this automatically in python based on actual genders of client/agent....
        self.mean_ids=NP.array([0.40760,0.40548,0.45564])
        self.cov_ids=NP.array([[2.10735,1.01121, 0.48442],[1.01121,1.22836,0.55593],[0.48442,0.55593,0.77040]])


        # Does this do anything?
        self.randseeds=[373044980,27171222,156288614]

        #to make it consistent across different trials
        #NP.random.seed(1)

        # alpha beta and gamma values
        self.client_alpha_value = 1.0
        self.client_beta_value_of_client = 0.005
        self.client_beta_value_of_agent = 0.005

        self.agent_alpha_value = 1.0
        self.agent_beta_value_of_client = 0.005
        self.agent_beta_value_of_agent = 0.005



        # from trials block
        self.rseed = None
        self.client_id = None
        self.agent_id = None

        self.learn_tau_init = None
        self.learn_prop_init = None
        self.learn_beta_client_init = None
        self.learn_beta_agent_init = None

        self.simul_tau_init = None
        self.simul_prop_init = None
        self.simul_beta_client_init = None
        self.simul_beta_agent_init = None

        self.learn_initx = None
        self.simul_initx = None

        self.simul_agent = None
        self.learn_agent = None

        self.learn_ddvo = None
        self.learn_defl = None
        self.simul_ddvo = None
        self.simul_defl = None


        # from experiments block
        self.learn_avgs = None
        self.simul_avgs = None
        self.learn_turn = None
        self.simul_turn = None


        # from horizon block
        self.learn_d = None
        self.simul_d = None
        self.total_iterations = 0

        # plotting and for gui
        self.plotter = None
        self.gui_manager = None
        self.thread_event = None
        self.waiting = True
        self.terminate_flag = False

        # for running instructions
        self.update_uniform_draws               = False
        self.update_environment_noise           = False
        self.update_gamma_value                 = False
        self.update_client_alpha                = False

        self.update_client_beta_of_client       = False
        self.update_client_beta_of_agent        = False

        self.update_agent_alpha                 = False

        self.update_agent_beta_of_client        = False
        self.update_agent_beta_of_agent         = False

        self.update_num_steps                   = False


        self.step_bayesact_sim                  = False


        self.num_steps                          = 1


    def startBayesactSim(self):
        self.waiting = False

        print "num trials: ",self.num_trials
        print "num experiments: ",self.num_experiments
        print "num samples: ",self.num_samples
        print "client knowledge: ",self.client_knowledge
        print "agent knowledge: ",self.agent_knowledge
        print "uniform draws: ",self.uniform_draws
        print "max horizon: ",self.max_horizon
        print "roughening noise: ",self.roughening_noise
        print "environment noise: ",self.env_noise
        print "gamma value: ",self.gamma_value
        print "client id label: ",self.client_id_label
        print "agent id label: ",self.agent_id_label
        print "agent gender: ",self.agent_gender
        print "client gender: ",self.client_gender

        self.initBayesactSim()
        self.mainLoop()


    def mainLoop(self):
        while(not(self.terminate_flag)):
            # For some reason, while a thread is waiting, the program will say it is leaking memory sometimes
            self.waiting = True
            # Pause and await instruction
            self.thread_event.clear()
            self.thread_event.wait()
            self.runInstructions()
            self.waiting = False
            #self.plotter.plot()

        self.plotter.clearPlots()


    def runInstructions(self):
        if (isinstance(self.gui_manager, cBayesactSimGuiPanel)):
            #self.checkParams()

            if (self.update_num_steps):
                self.num_steps = int(self.gui_manager.m_NumberOfStepsTextBox.GetValue())
                self.update_num_steps = False
                print 10

            if (self.step_bayesact_sim):
                self.stepBayesactSim(self.num_steps)
                self.step_bayesact_sim = False


    def stepBayesactSim(self, iNumSteps):
        for i in range(iNumSteps):
            self.checkParams()
            self.evaluateStep()
            self.plotter.plot()

            if (self.terminate_flag):
                return


    def checkParams(self):
        recompute_client = False
        recompute_agent = False

        # I don't think uniform_draws currently does anything, probably will need to
        if (self.update_uniform_draws):
            self.uniform_draws = bool(self.gui_manager.m_UniformDrawsChoice.GetStringSelection())
            self.update_uniform_draws = False

        if (self.update_environment_noise):
            self.env_noise = float(self.gui_manager.m_EnvironmentNoiseTextBox.GetValue())
            self.update_environment_noise = False

        if (self.update_gamma_value):
            self.gamma_value = float(self.gui_manager.m_GammaValueTextBox.GetValue())
            self.learn_agent.gamma_value = self.gamma_value
            self.learn_agent.gamma_value = self.gamma_value
            recompute_client = True
            recompute_agent = True
            self.update_gamma_value = False

        if (self.update_client_alpha):
            self.client_alpha_value = float(self.gui_manager.m_ClientAlphaTextBox.GetValue())
            self.learn_agent.alpha_value = self.client_alpha_value
            recompute_client = True
            self.update_client_alpha = False

        if (self.update_client_beta_of_client):
            self.client_beta_value_of_client = float(self.gui_manager.m_ClientBetaOfClientTextBox.GetValue())
            self.learn_agent.beta_value_client = self.client_beta_value_of_client
            recompute_client = True
            self.update_client_beta_of_client = False

        if (self.update_client_beta_of_agent):
            self.client_beta_value_of_agent = float(self.gui_manager.m_ClientBetaOfAgentTextBox.GetValue())
            self.learn_agent.beta_value_agent = self.client_beta_value_of_agent
            recompute_client = True
            self.update_client_beta_of_agent = False

        if (self.update_agent_alpha):
            self.agent_alpha_value = float(self.gui_manager.m_AgentAlphaTextBox.GetValue())
            self.simul_agent.alpha_value = self.agent_alpha_value
            recompute_agent = True
            self.update_agent_alpha = False

        if (self.update_agent_beta_of_client):
            self.agent_beta_value_of_client = float(self.gui_manager.m_AgentBetaOfClientTextBox.GetValue())
            self.simul_agent.beta_value_client = self.agent_beta_value_of_client
            recompute_agent = True
            self.update_agent_beta_of_client = False

        if (self.update_agent_beta_of_agent):
            self.agent_beta_value_of_agent = float(self.gui_manager.m_AgentBetaOfAgentTextBox.GetValue())
            self.simul_agent.beta_value_agent = self.agent_beta_value_of_agent
            recompute_agent = True
            self.update_agent_beta_of_agent = False

        # To be used after updating alpha, beta, and gamma values
        if (recompute_client):
            self.learn_agent.init_covariances()
            recompute_client = False

        if (recompute_agent):
            self.simul_agent.init_covariances()
            recompute_agent = False


    def printResults(self):
        print 10*"+"," RESULTS",10*"+"
        print "final deflection (learner): ",self.learn_d
        self.learn_defl.append(self.learn_d)
        print "final learned client id: "
        print self.learn_avgs.f[6:9]
        print "actual client id: "
        print self.client_id.transpose()
        dvo= self.client_id.transpose()-self.learn_avgs.f[6:9]
        #changed from sqrt(dot(...)) here on April 4th, 2013
        self.learn_ddvo.append(NP.dot(dvo,dvo.transpose()))
        print "sum of squared differences between agent learned and client true id:"
        print self.learn_ddvo[-1]
        print "final deflection (simulator): ",self.simul_d
        self.simul_defl.append(self.simul_d)
        print "final learned agent id: "
        print self.simul_avgs.f[6:9]
        print "actual agent id: "
        print self.agent_id.transpose()
        dvo = self.agent_id.transpose()-self.simul_avgs.f[6:9]
        #changed from sqrt(dot(...)) here on April 4th, 2013
        self.simul_ddvo.append(NP.dot(dvo,dvo.transpose()))
        print "sum of squared differences between simul learned and agent true id:"
        print self.simul_ddvo[-1]
        print 30*"+"

        self.meanlearndefl.append(NP.mean(self.learn_defl))
        self.meansimuldefl.append(NP.mean(self.simul_defl))
        self.meanlearnddvo.append(NP.mean(self.learn_ddvo))
        self.meansimulddvo.append(NP.mean(self.simul_ddvo))

        stdlearndefl = NP.std(self.meanlearndefl)
        stdsimuldefl = NP.std(self.meansimuldefl)
        stdlearnddvo = NP.std(self.meanlearnddvo)
        stdsimulddvo = NP.std(self.meansimulddvo)

        print 10*"*","OVERALL RESULTS",10*"*"
        print "mean deflection (learner): ",NP.mean(self.meanlearndefl)," +/- ",stdlearndefl
        print "mean deflection (simulator): ",NP.mean(self.meansimuldefl)," +/- ",stdsimuldefl
        print "mean difference in id sentiments (learner): ",NP.mean(self.meanlearnddvo)," +/- ",stdlearnddvo
        print "mean differnece in id sentiments (simulator): ",NP.mean(self.meansimulddvo)," +/- ",stdsimulddvo
        print 30*"*"


    def initBayesactSim(self):
        rseed = NP.random.randint(0,382948932)

        #this was moved from below the client_id agent_id generation
        #on March 22nd at 11:52am
        #for repeatability
        rseed = NP.random.randint(0,382948932)
        #rseed=randseeds[trial]
        #rseed = 373044980  #lady and shoplifter
        #rseed = 156288614  #hero and insider
        #rseed=60890393
        #rseed=120534679
        print "random seeed is : ",rseed

        NP.random.seed(rseed)

        #the actual (true) ids drawn from the distribution over ids
        if self.client_id_label=="":
            self.client_id = NP.asarray([NP.random.multivariate_normal(self.mean_ids,self.cov_ids)]).transpose()
        else:
            self.client_id = NP.asarray([getIdentity(self.identities_filename,self.client_id_label,self.client_gender)]).transpose()
        if self.agent_id_label=="":
            self.agent_id =  NP.asarray([NP.random.multivariate_normal(self.mean_ids,self.cov_ids)]).transpose()
        else:
            self.agent_id = NP.asarray([getIdentity(self.identities_filename,self.agent_id_label,self.agent_gender)]).transpose()

        print "agent id: ",self.agent_id
        print "client id: ",self.client_id

        (self.learn_tau_init,self.learn_prop_init,self.learn_beta_client_init,self.learn_beta_agent_init)=init_id(self.agent_knowledge,self.agent_id,self.client_id,self.mean_ids,self.num_agent_confusers)
        (self.simul_tau_init,self.simul_prop_init,self.simul_beta_client_init,self.simul_beta_agent_init)=init_id(self.client_knowledge,self.client_id,self.agent_id,self.mean_ids,self.num_client_confusers)

        self.learn_initx=self.learn_init_turn
        self.simul_initx=self.simul_init_turn

        self.simul_agent=Agent(N=self.num_samples,alpha_value=self.agent_alpha_value,gamma_value=self.gamma_value,beta_value_agent=self.agent_beta_value_of_agent,beta_value_client=self.agent_beta_value_of_client,beta_value_client_init=self.simul_beta_client_init,beta_value_agent_init=self.simul_beta_agent_init,agent_rough=self.simul_agent_rough,client_rough=self.simul_client_rough,identities_file=self.identities_filename,init_turn=self.learn_init_turn)
        self.learn_agent=Agent(N=self.num_samples,alpha_value=self.client_alpha_value,gamma_value=self.gamma_value,beta_value_agent=self.client_beta_value_of_agent,beta_value_client=self.client_beta_value_of_client,beta_value_client_init=self.learn_beta_client_init,beta_value_agent_init=self.learn_beta_agent_init,agent_rough=self.learn_agent_rough,client_rough=self.learn_client_rough,identities_file=self.identities_filename,init_turn=self.simul_init_turn)


        self.simul_agent.print_params()
        print "simulator init tau: ",self.simul_tau_init
        print "simulator prop init: ",self.simul_prop_init
        print "simulator beta client init: ",self.simul_beta_client_init
        print "simulator beta agent init: ",self.simul_beta_agent_init

        print 10*"-","learning agent parameters: "
        self.learn_agent.print_params()
        print "learner init tau: ",self.learn_tau_init
        print "learner prop init: ",self.learn_prop_init
        print "learner beta client init: ",self.learn_beta_client_init
        print "learner beta agent init: ",self.learn_beta_agent_init

        self.learn_ddvo=[]
        self.learn_defl=[]
        self.simul_ddvo=[]
        self.simul_defl=[]

        self.learn_avgs=self.learn_agent.initialise_array(self.learn_tau_init,self.learn_prop_init,self.learn_initx)
        self.simul_avgs=self.simul_agent.initialise_array(self.simul_tau_init,self.simul_prop_init,self.simul_initx)

        print "simulator average: "
        self.simul_avgs.print_val()

        print "learner average f: "
        self.learn_avgs.print_val()

        self.learn_turn="agent"
        self.simul_turn="client"

        #To plot initial data
        #to send the initial sentiments to the plotter
        self.learn_agent.sendSamplesToPlotter(self.learn_agent.samples,self.plotter,eTurn.learner)
        self.simul_agent.sendSamplesToPlotter(self.simul_agent.samples,self.plotter,eTurn.simulator)
        self.plotter.plot()


    def evaluateStep(self):

        self.total_iterations += 1

        print "learner turn: ",self.learn_turn
        print "simulator turn: ",self.simul_turn

        observ=[]

        print 10*"-d","total iterations ",self.total_iterations,80*"-"

        #In fact, both agents should update on every turn now, so
        #we should be able to always call get_next_action for both agents here?

        #like this:
        (learn_aab,learn_paab)=self.learn_agent.get_next_action(self.learn_avgs)

        print "agent action/client observ: ",learn_aab

        simul_observ=learn_aab

        (simul_aab,simul_paab)=self.simul_agent.get_next_action(self.simul_avgs)

        print "client action/agent observ: ",simul_aab

        learn_observ=simul_aab

        #add environmental noise here if it is being used
        if self.env_noise>0.0:
            learn_observ=map(lambda fv: NP.random.normal(fv,self.env_noise), learn_observ)
            simul_observ=map(lambda fv: NP.random.normal(fv,self.env_noise), simul_observ)


        print "learn observ: ",learn_observ
        print "simul observ: ",simul_observ


        learn_xobserv=[State.turnnames.index(invert_turn(self.learn_turn))]
        simul_xobserv=[State.turnnames.index(invert_turn(self.simul_turn))]


        #learn_avgs=cProfile.run('learn_agent.propagate_forward(learn_turn,learn_aab,learn_observ,verb=learn_verbose)')
        # propagate_forward sends the unweigted data set to the plotter, hence the reason why there isn't a function there isn't an explicit sendSamplesToPlotter function here
        self.learn_avgs=self.learn_agent.propagate_forward(learn_aab,learn_observ,learn_xobserv,verb=self.learn_verbose,plotter=self.plotter,agent=eTurn.learner)
        self.simul_avgs=self.simul_agent.propagate_forward(simul_aab,simul_observ,simul_xobserv,verb=self.simul_verbose,plotter=self.plotter,agent=eTurn.simulator)


        print "learner f is: "
        self.learn_avgs.print_val()

        print "simulator f is: "
        self.simul_avgs.print_val()


        #I think these should be based on fundamentals, not transients
        (aid,cid)=self.learn_agent.get_avg_ids(self.learn_avgs.f)
        print "learner agent id:",aid
        print "learner client id:",cid

        (aid,cid)=self.simul_agent.get_avg_ids(self.simul_avgs.f)
        print "simul agent id:",aid
        print "simul client id:",cid

        '''
        if self.get_full_id_rate>0 and (self.total_iterations+1)%self.get_full_id_rate==0:
            (cnt_ags,cnt_cls)=self.learn_agent.get_all_ids()
            print "top ten ids for agent (learner perspective):"
            print cnt_ags[0:10]
            print "top ten ids for client (learner perspective):"
            print cnt_cls[0:10]
            (cnt_ags,cnt_cls)=simul_agent.get_all_ids()
            print "top ten ids for agent (simulator perspective):"
            print cnt_ags[0:10]
            print "top ten ids for client (simulator perspective):"
            print cnt_cls[0:10]
        '''

        print "current deflection of averages: ",self.learn_agent.deflection_avg

        self.learn_d=self.learn_agent.compute_deflection()
        print "current deflection (learner perspective): ",self.learn_d
        self.simul_d=self.simul_agent.compute_deflection()
        print "current deflection (simulator perspective): ",self.simul_d


        if self.learn_turn=="client":
            self.learn_turn="agent"
            self.simul_turn="client"
        else:
            self.learn_turn="client"
            self.simul_turn="agent"

        #To plot data
        self.plotter.plot()




def main(argv):
    a = cBayesactTools(argv)
    a.startBayesactSim()
    #a.evaluateTrials(a.num_trials, a.num_experiments, a.max_horizon)
    a.evaluateTrials(1, 1, 1)

if __name__ == "__main__":
    main(sys.argv)
