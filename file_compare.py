
import shutil
import os
import filecmp
from time import time
from probabilistic_to_determenistic_parser import parser

def find_current_files(domain,problem):
    new_domain= True
    new_problem = True
    path = os.getcwd()
    domains_path = os.path.join(path, "domains")
    problems_path = os.path.join(path, "problems")
    now = str(int(time()))
    domain_name = "domain_"+now+".pddl"
    domain_name_deterministic = "domain_"+now+"_deterministic.pddl"
    problem_name ="problem_"+now+".pddl"
    this_domain = os.path.join(domains_path,domain_name)
    this_domain_deterministic = os.path.join(domains_path,domain_name_deterministic)
    this_problem = os.path.join(problems_path,problem_name)
    determenistic_domain = "temp.pddl"
    with open(determenistic_domain,'w') as f:
        f.writelines(parser(domain))

    for f in os.listdir(domains_path):
        file = os.path.join(domains_path,f)

        if "deterministic" in file.title() and os.path.getsize(file) == os.path.getsize(determenistic_domain):
            if filecmp.cmp(file,determenistic_domain,shallow=False):
                new_domain = False
                this_domain = file
                domain_name = f
                break
    if new_domain:
        shutil.copy(determenistic_domain, this_domain_deterministic)
        shutil.copy(domain, this_domain)
        shutil.copy(problem,this_problem)
    else:

        for f in os.listdir(problems_path):
            file = os.path.join(problems_path,f)
            if os.path.getsize(file) == os.path.getsize(problem):
                if filecmp.cmp(file,problem,shallow=False):
                    new_problem = False
                    this_problem = file
                    problem_name = f
                    break
        if new_problem:
            shutil.copy(problem,this_problem)
    os.remove(determenistic_domain)
    return {"domain_name":domain_name,"domain_path": this_domain,"problem_path": this_problem,
            "problem_name":problem_name,"new_domain": new_domain, "new_problem": new_problem}






