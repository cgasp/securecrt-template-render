# $language = "Python"
# $interface = "1.0"

# Creator : CGA
# License: MIT
# Description : Small script to generate commands on the fly from template file. 
#               Developped to be integrated in secureCRT. 
#               The script will prompt message box when it discover a variable inside {{ }}
#               Support multivariable should be inside {{ }} and separated by ; 
#               e.g. {{ge0;ge1;ge2;ge3}}

crt.Screen.Synchronous = True
import os
import re
import json

var = { }

def pattern_matching(cmd,func):
    # debug
    
    # Pattern for the variable
    pattern = r"\{\{([^}]*)}\}"
     
    matches = re.finditer(pattern, cmd)
    
    for matchNum, match in enumerate(matches):
        matchNum = matchNum + 1
        
        # Goes over each match
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1

            if func == 'feed_var' and match.group(groupNum) not in var:
                # If the variable is KNOWN
                    var[match.group(groupNum)] = crt.Dialog.Prompt("Variable found : " + match.group(groupNum), "Variable value", "Insert value or cancel to send nothing",False)

            elif func == 'generate_cmds':
                if ';' in var[match.group(groupNum)]:
                    # If there is multiple variable to generate several commands
                    cmds = []
                    # Split the variable in an array
                    variable_list = var[match.group(groupNum)].split(';')
                    # Generate command list by variable list
                    for variable in variable_list:
                        cmds.append(cmd.replace('{{'+ match.group(groupNum) +'}}', ' ' + variable + ' '))
                    return cmds
                else:                
                    return [cmd.replace('{{'+ match.group(groupNum) +'}}', ' ' + var[match.group(groupNum)] + ' ')]


def send_commands(cmd,prompt = ">"):
    crt.Screen.Send(cmd)
    # Expect 
    crt.Screen.WaitForString(prompt,3)    


def main():

    # open the template file
    Filename = crt.Arguments.GetArg(0)
    strScriptPath = __file__
    strScriptFolder = os.path.dirname(__file__)

    # retrieve full path 
    FullPath = "{0}\\templates\{1}".format(strScriptFolder,Filename)

    line_num = 0
    cmds = []
    cmd2send = []

    # Read file line by line - feed Variables
    with open(FullPath, "r") as f:
        for line in f:
            if line_num == 0:
                # First line
                param = json.loads(line)
                # Default value for prompt
                if "prompt" not in param:
                    param["prompt"] = '>'
            else: 
                # Parse line for variable and feed value for variables
                if line[0] != '#' and line[0] != ' ' and line[0] != '' and '{{' in line and '}}' in line:
                    # Feed variable values 
                    pattern_matching(line,'feed_var')
                    # Generate commands and execute them
                    for cmd in pattern_matching(line,'generate_cmds'):
                        send_commands(cmd,param["prompt"])
                else:
                    send_commands(line,param["prompt"])
                # crt.Dialog.MessageBox("Feed var :" + line)
            line_num += 1

main()