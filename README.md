# Multi-Domain-Agent

# Summeay
Multli domain agent, using pddl files.
the agent use siw-then-bfsf planner, Dyna-Q+ and Dyna-Q2 (with mc-control) algorithmes, and more..

for learning phase:

# Running
The Executor runs with the following commands:
<br />for learning phase - python my_executive.py -L <domain_file> <problem_file> <br />
when domain_file and problem_file are pddl files <br />
for execute phase - python my_executive.py -E <domain_file> <problem_file> 
# Config File
## In the config file there are 5 variables:

* GAMMA :
<br /> Determines the importance of future rewards.
A factor of 0 will make the agent short-sighted by only considering current reward.
A factor approaching 1 will make it strive for a long-term high reward. 
* LEARNING_RATE:
<br /> The rate of how often the executor uses previous information- if 0, the executor uses only previous inforamtion, if 1, the executor does not use previous information at all
* K_EPSILON:
<br /> Decay factor of epsilon. Calculated by the number of times the agent has reached a certain state to the power of the epsilon.
* KAPPA:
<br /> Parameter of dynaQ+ designed to give a bonus for exploring states the agent has not visited in a long time.
* PLANNING_STEPS:
<br /> Parameter of dynaQ. After each time the agent selects an action, its simulates a number of transitions to improve the model, this number marks the number of transitions of the agent

# Agent Boot.
I added a Python file that would make it easier to boot the agent to its initial state. All you have to do is run the Clear.py file, all the agent's files will be deleted and the system will return to its original state, as if it had never been used.
