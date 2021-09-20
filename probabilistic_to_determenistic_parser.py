import re
import sys


def parser1(domain):
    with open(domain, 'r') as f:
        content = f.read()
        content_new = re.sub('probabilistic *0.\d', '', content)
        content_new = re.sub(' *0.\d.*', '', content_new)
        f.close()
        return content_new


def parser(domain):
    new_lines = []
    with open(domain, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if 'probabilistic' in line:
                line = re.sub('\(probabilistic *0.\d*', '', line)
                index = line.rfind(')')
                line = line[0:index] + line[index + 1::]
            else:
                line = re.sub(' *0.\d.*', '', line)
            new_lines.append(line)
    return new_lines


if __name__ == '__main__':
    with open("blabla.pddl", 'w') as f:
        f.writelines(parser1(sys.argv[1]))
