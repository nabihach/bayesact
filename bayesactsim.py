"""------------------------------------------------------------------------------------------
Bayesian Affect Control Theory
Simulator Test Code
Author: Jesse Hoey  jhoey@cs.uwaterloo.ca   http://www.cs.uwaterloo.ca/~jhoey
September 2013
Use for research purposes only.
Please do not re-distribute without written permission from the author
Any commerical uses strictly forbidden.
Code is provided without any guarantees.
Research sponsored by the Natural Sciences and Engineering Council of Canada (NSERC).
use python2.6
see README for details
----------------------------------------------------------------------------------------------"""

from bayesact import *
import getopt
import cProfile
import sys
import threading
sys.path.append("./gui/")
from cBayesactSimGui import cBayesactSimGui
from cEnum import eTurn

def bayesactsim(argv, plotter=None, verbose=False):
    #NP.set_printoptions(precision=5)
    #NP.set_printoptions(suppress=True)
    NP.set_printoptions(linewidth=10000)


    #get some key parameters from the command line
    num_samples=1000

    #agent knowledge of client id:
    #0 : nothing
    #1 : one of a selection of  num_confusers+1 randoms
    #2 : exactly
    #3 : same as 0 but also agent does not know its own id
    agent_knowledge=0
    #client knowledge of agent id:
    client_knowledge=0

    agent_id_label=""
    client_id_label=""

    agent_gender="male"
    client_gender="male"

    #used only for label extraction if the user enters a label they want to use for simulations
    identities_filename="fidentities.dat"

    behaviours_filenmae="fbehaviours.dat"   #not used

    #uniform draws - if true will draw client IDs uniformly over -4.3,4.3.
    #If false, drawn from Normal distribution of the client ids in the database
    uniform_draws=False

    gamma_value=1.0

    #if>0, add a small amount of roughening noise to the client identities
    roughening_noise=-1.0


    #environment noise: this will corrupt the transmission of the actions with zero-mean Gaussian noise with this variance
    env_noise=0.0

    max_horizon=50

    num_trials=20
    num_experiments=10

    get_full_id_rate=20

    learn_init_turn="agent"
    simul_init_turn="client"

    helpstring="Bayesact simulator (2 agents) usage:\n bayesactsim.py\n\t -t <number of trials (default 20)>\n\t -x <number of experiments per trial (default 10)>\n\t -n <number of samples (default 1000)>\n\t -c <client knowledge (0,1,2) (default 2)>\n\t -a <agent knowledge (0,1,2) (Default 0)>\n\t -u (if specified - do uniform draws)\n\t -d <max horizon - default 50>\n\t -r <roughening noise: default n^(-1/3) - to use no roughening ('full' method), specify 0>\n\t -e <environment noise (default 0.0)>\n\t -g <gamma_value (default 1.0)>\n\t -i <agent id label: default randomly chosen>\n\t  -j <client id label: default randomly chosen>\n\t -k <agent gender (default: male) - only works if agent_id is specified with -i>\n\t -l (client gender (default: male) only works if client_id is specified with -j>"

    try:
        opts, args = getopt.getopt(argv[1:],"huvon:t:x:a:c:d:r:e:g:i:j:k:l:",["help","n=","t=","x=","c=","a=","u=","d=","r=","e=","g=","i=","j=","k=","l="])
    except getopt.GetoptError:
        print helpstring
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print helpstring
            sys.exit()
        elif opt in ("-n", "--numsamples"):
            num_samples = int(arg)
        elif opt in ("-t", "--numtrials"):
            num_trials = int(arg)
        elif opt in ("-x", "--numexperiments"):
            num_experiments = int(arg)
        elif opt in ("-c", "--clientknowledge"):
            client_knowledge = int(arg)
        elif opt in ("-a", "--agentknowledge"):
            agent_knowledge = int(arg)
        elif opt in ("-d", "--horizon"):
            max_horizon = int(arg)
        elif opt in ("-u", "--uniformdraws"):
            uniform_draws=True
        elif opt in ("-r", "--roughen"):
            roughening_noise=float(arg)
        elif opt in ("-e", "--enoise"):
            env_noise=float(arg)
        elif opt in ("-g", "--gamma"):
            gamma_value=float(arg)
        elif opt in ("-i", "--agentid"):
            agent_id_label=arg
        elif opt in ("-j", "--clientid"):
            client_id_label=arg
        elif opt in ("-k", "--agentgender"):
            agent_gender=arg
        elif opt in ("-l", "--clientgender"):
            client_gender=arg


    if roughening_noise<0.0:
        #default
        roughening_noise=num_samples**(-1.0/3.0)


    print "num trials: ",num_trials
    print "num experiments: ",num_experiments
    print "num samples: ",num_samples
    print "client knowledge: ",client_knowledge
    print "agent knowledge: ",agent_knowledge
    print "uniform draws: ",uniform_draws
    print "max horizon: ",max_horizon
    print "roughening noise: ",roughening_noise
    print "environment noise: ",env_noise
    print "gamma value: ",gamma_value
    print "client id label: ",client_id_label
    print "agent id label: ",agent_id_label
    print "agent gender: ",agent_gender
    print "client gender: ",client_gender

    #-----------------------------------------------------------------------------------------------------------------------------
    #simulation start
    #-----------------------------------------------------------------------------------------------------------------------------

    num_agent_confusers=3
    num_client_confusers=3



    #to roughen, not use proposal  - for any unknown identity
    learn_agent_rough=0.0
    learn_client_rough=0.0

    if (agent_knowledge==0 or agent_knowledge==3) and roughening_noise>0:
        learn_client_rough=roughening_noise
        if agent_knowledge==3:
            learn_agent_rough=roughening_noise

    simul_agent_rough=0.0
    simul_client_rough=0.0
    if (client_knowledge==0 or client_knowledge==3) and roughening_noise>0:
        simul_client_rough=roughening_noise
        if client_knowledge==3:
            simul_agent_rough=roughening_noise



    simul_verbose=verbose
    learn_verbose=verbose

    meanlearndefl =[]
    meansimuldefl = []
    meanlearnddvo = []
    meansimulddvo = []

    #the mean and covariance of IDs for male agents as taken from the databases
    #should do this automatically in python based on actual genders of client/agent....
    mean_ids=NP.array([0.40760,0.40548,0.45564])
    cov_ids=NP.array([[2.10735,1.01121, 0.48442],[1.01121,1.22836,0.55593],[0.48442,0.55593,0.77040]])


    randseeds=[373044980,27171222,156288614]

    #to make it consistent across different trials
    #NP.random.seed(1)



    for trial in range(num_trials):

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
        if client_id_label=="":
            client_id = NP.asarray([NP.random.multivariate_normal(mean_ids,cov_ids)]).transpose()
        else:
            client_id = NP.asarray([getIdentity(identities_filename,client_id_label,client_gender)]).transpose()
        if agent_id_label=="":
            agent_id =  NP.asarray([NP.random.multivariate_normal(mean_ids,cov_ids)]).transpose()
        else:
            agent_id = NP.asarray([getIdentity(identities_filename,agent_id_label,agent_gender)]).transpose()

        print "agent id: ",agent_id
        print "client id: ",client_id

        #these are uniformly distributed which will generate waaay too many extreme ids
        #client_id = NP.dot(NP.random.random([3,1]),8.6)-4.3
        #agent_id = NP.dot(NP.random.random([3,1]),8.6)-4.3
        #simulation agent knows client and agent ids (it is the client)
        (learn_tau_init,learn_prop_init,learn_beta_client_init,learn_beta_agent_init)=init_id(agent_knowledge,agent_id,client_id,mean_ids,num_agent_confusers)
        (simul_tau_init,simul_prop_init,simul_beta_client_init,simul_beta_agent_init)=init_id(client_knowledge,client_id,agent_id,mean_ids,num_client_confusers)

        learn_initx=learn_init_turn
        simul_initx=simul_init_turn

        #this version has the agents more flexible about their identities....
        #simul_agent=TutoringAgent(N=num_samples,alpha_value=1.0,initx=learn_initx,goalx=learn_goalx,gamma_value=1.0,beta_value_agent=0.05,beta_value_client=0.05,beta_value_client_init=simul_beta_init)
        #learn_agent=TutoringAgent(N=num_samples,alpha_value=1.0,initx=simul_initx,goalx=simul_goalx,gamma_value=1.0,beta_value_agent=0.05,beta_value_client=0.05,beta_value_client_init=learn_beta_init)
        simul_agent=Agent(N=num_samples,alpha_value=0.1,gamma_value=gamma_value,beta_value_agent=0.005,beta_value_client=0.005,beta_value_client_init=simul_beta_client_init,beta_value_agent_init=simul_beta_agent_init,agent_rough=simul_agent_rough,client_rough=simul_client_rough,identities_file=identities_filename,init_turn=learn_init_turn)
        learn_agent=Agent(N=num_samples,alpha_value=0.1,gamma_value=gamma_value,beta_value_agent=0.005,beta_value_client=0.005,beta_value_client_init=learn_beta_client_init,beta_value_agent_init=learn_beta_agent_init,agent_rough=learn_agent_rough,client_rough=learn_client_rough,identities_file=identities_filename,init_turn=simul_init_turn)

        print 100*"$"
        print "trial number: ",trial
        print 100*"$"
        print 10*"-","simulation agent parameters: "
        simul_agent.print_params()
        print "simulator init tau: ",simul_tau_init
        print "simulator prop init: ",simul_prop_init
        print "simulator beta client init: ",simul_beta_client_init
        print "simulator beta agent init: ",simul_beta_agent_init

        print 10*"-","learning agent parameters: "
        learn_agent.print_params()
        print "learner init tau: ",learn_tau_init
        print "learner prop init: ",learn_prop_init
        print "learner beta client init: ",learn_beta_client_init
        print "learner beta agent init: ",learn_beta_agent_init

        learn_ddvo=[]
        learn_defl=[]
        simul_ddvo=[]
        simul_defl=[]


        for exper in range(num_experiments):
            print 100*"$"
            print "experiment number: ",exper
            print 100*"$"
            learn_avgs=learn_agent.initialise_array(learn_tau_init,learn_prop_init,learn_initx)
            simul_avgs=simul_agent.initialise_array(simul_tau_init,simul_prop_init,simul_initx)

            print "simulator average: "
            simul_avgs.print_val()

            print "learner average f: "
            learn_avgs.print_val()


            learn_turn="agent"
            simul_turn="client"

            for iter in range(max_horizon):
                print "learner turn: ",learn_turn
                print "simulator turn: ",simul_turn

                observ=[]
                print 10*"-d","iter ",iter,80*"-"
                #In fact, both agents should update on every turn now, so
                #we should be able to always call get_next_action for both agents here?

                #like this:
                (learn_aab,learn_paab)=learn_agent.get_next_action(learn_avgs)
                print "agent action/client observ: ",learn_aab
                simul_observ=learn_aab

                (simul_aab,simul_paab)=simul_agent.get_next_action(simul_avgs)
                print "client action/agent observ: ",simul_aab
                learn_observ=simul_aab

                #add environmental noise here if it is being used
                if env_noise>0.0:
                    learn_observ=map(lambda fv: NP.random.normal(fv,env_noise), learn_observ)
                    simul_observ=map(lambda fv: NP.random.normal(fv,env_noise), simul_observ)

                print "learn observ: ",learn_observ
                print "simul observ: ",simul_observ

                learn_xobserv=[State.turnnames.index(invert_turn(learn_turn))]
                simul_xobserv=[State.turnnames.index(invert_turn(simul_turn))]



                #learn_avgs=cProfile.run('learn_agent.propagate_forward(learn_turn,learn_aab,learn_observ,verb=learn_verbose)')
                learn_avgs=learn_agent.propagate_forward(learn_aab,learn_observ,learn_xobserv,verb=learn_verbose,plotter=plotter,agent=eTurn.learner)
                simul_avgs=simul_agent.propagate_forward(simul_aab,simul_observ,simul_xobserv,verb=simul_verbose,plotter=plotter,agent=eTurn.simulator)

                print "learner f is: "
                learn_avgs.print_val()

                print "simulator f is: "
                simul_avgs.print_val()

                #To plot data
                if (None != plotter):
                    plotter.plot3D()


                #I think these should be based on fundamentals, not transients
                (aid,cid)=learn_agent.get_avg_ids(learn_avgs.f)
                print "learner agent id:",aid
                print "learner client id:",cid

                (aid,cid)=simul_agent.get_avg_ids(simul_avgs.f)
                print "simul agent id:",aid
                print "simul client id:",cid


                if get_full_id_rate>0 and (iter+1)%get_full_id_rate==0:
                    (cnt_ags,cnt_cls)=learn_agent.get_all_ids()
                    print "top ten ids for agent (learner perspective):"
                    print cnt_ags[0:10]
                    print "top ten ids for client (learner perspective):"
                    print cnt_cls[0:10]
                    (cnt_ags,cnt_cls)=simul_agent.get_all_ids()
                    print "top ten ids for agent (simulator perspective):"
                    print cnt_ags[0:10]
                    print "top ten ids for client (simulator perspective):"
                    print cnt_cls[0:10]

                print "current deflection of averages: ",learn_agent.deflection_avg

                learn_d=learn_agent.compute_deflection()
                print "current deflection (learner perspective): ",learn_d
                simul_d=simul_agent.compute_deflection()
                print "current deflection (simulator perspective): ",simul_d

                if learn_turn=="client":
                    learn_turn="agent"
                    simul_turn="client"
                else:
                    learn_turn="client"
                    simul_turn="agent"



            print 10*"+","EXPERIMENT ",exper," RESULTS",10*"+"
            print "final deflection (learner): ",learn_d
            learn_defl.append(learn_d)
            print "final learned client id: "
            print learn_avgs.f[6:9]
            print "actual client id: "
            print client_id.transpose()
            dvo= client_id.transpose()-learn_avgs.f[6:9]
            #changed from sqrt(dot(...)) here on April 4th, 2013
            learn_ddvo.append(NP.dot(dvo,dvo.transpose()))
            print "sum of squared differences between agent learned and client true id:"
            print learn_ddvo[-1]
            print "final deflection (simulator): ",simul_d
            simul_defl.append(simul_d)
            print "final learned agent id: "
            print simul_avgs.f[6:9]
            print "actual agent id: "
            print agent_id.transpose()
            dvo = agent_id.transpose()-simul_avgs.f[6:9]
            #changed from sqrt(dot(...)) here on April 4th, 2013
            simul_ddvo.append(NP.dot(dvo,dvo.transpose()))
            print "sum of squared differences between simul learned and agent true id:"
            print simul_ddvo[-1]
            print 30*"+"

        meanlearndefl.append(NP.mean(learn_defl))
        meansimuldefl.append(NP.mean(simul_defl))
        meanlearnddvo.append(NP.mean(learn_ddvo))
        meansimulddvo.append(NP.mean(simul_ddvo))

        stdlearndefl = NP.std(learn_defl)
        stdsimuldefl = NP.std(simul_defl)
        stdlearnddvo = NP.std(learn_ddvo)
        stdsimulddvo = NP.std(simul_ddvo)

        print 10*"*","TRIAL ",trial," RESULTS",10*"*"
        print "mean deflection (learner): ",meanlearndefl[-1]," +/- ",stdlearndefl
        print "mean deflection (simulator): ",meansimuldefl[-1]," +/- ",stdsimuldefl
        print "mean difference in id sentiments (learner): ",meanlearnddvo[-1]," +/- ",stdlearnddvo
        print "mean differnece in id sentiments (simulator): ",meansimulddvo[-1]," +/- ",stdsimulddvo
        print 30*"*"



    stdlearndefl = NP.std(meanlearndefl)
    stdsimuldefl = NP.std(meansimuldefl)
    stdlearnddvo = NP.std(meanlearnddvo)
    stdsimulddvo = NP.std(meansimulddvo)

    print 10*"*","OVERALL RESULTS",10*"*"
    print "mean deflection (learner): ",NP.mean(meanlearndefl)," +/- ",stdlearndefl
    print "mean deflection (simulator): ",NP.mean(meansimuldefl)," +/- ",stdsimuldefl
    print "mean difference in id sentiments (learner): ",NP.mean(meanlearnddvo)," +/- ",stdlearnddvo
    print "mean differnece in id sentiments (simulator): ",NP.mean(meansimulddvo)," +/- ",stdsimulddvo
    print 30*"*"


def main(argv):
    # This is required as plotting with wx does not allow wx.App.MainLoop to be started as a thread
    # I'm going to use the -o and -v option it can be changed anytime
    plot = False
    verbose = False

    # A hack, should probably be fixed later
    helpstring="Bayesact simulator (2 agents) usage:\n bayesactsim.py\n\t -t <number of trials (default 20)>\n\t -x <number of experiments per trial (default 10)>\n\t -n <number of samples (default 1000)>\n\t -c <client knowledge (0,1,2) (default 2)>\n\t -a <agent knowledge (0,1,2) (Default 0)>\n\t -u (if specified - do uniform draws)\n\t -d <max horizon - default 50>\n\t -r <roughening noise: default n^(-1/3) - to use no roughening ('full' method), specify 0>\n\t -e <environment noise (default 0.0)>\n\t -g <gamma_value (default 1.0)>\n\t -i <agent id label: default randomly chosen>\n\t  -j <client id label: default randomly chosen>\n\t -k <agent gender (default: male) - only works if agent_id is specified with -i>\n\t -l (client gender (default: male) only works if client_id is specified with -j>"

    try:
        opts, args = getopt.getopt(argv[1:],"huvon:t:x:a:c:d:r:e:g:i:j:k:l:",["help","n=","t=","x=","c=","a=","u=","d=","r=","e=","g=","i=","j=","k=","l="])
    except getopt.GetoptError:
        print helpstring
        sys.exit(2)

    for opt, arg in opts:
        if "-o" == opt:
            plot = True
        if "-v" == opt:
            verbose = True

    if (False == plot):
        bayesactsim(argv,None,verbose)
    else:
        print verbose
        plotter = cBayesactSimGui()
        bayesactSimThread = threading.Thread(target=bayesactsim, args=(argv,plotter,verbose))
        plotter.setThread(bayesactSimThread)
        plotter.startApp()


if __name__ == "__main__":
    main(sys.argv)

