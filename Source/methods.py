from enum import Enum
from sys import argv
from subprocess import run
from json import loads

class Executions():
    def execute_system(data): #MAIN THREAD KILLS METHODS AFTER 3 SECONDS NO MATTER WHAT. MAYBE FOR THINGS like running python command (infinite time length) we run inside another cmd and timeout that process?
        data = loads("".join(str(data).replace("'", '"')))
        process = run(data["command"],
        shell=True,
        capture_output=True,
        text=True)
        #Freezes right here until process finishes?
        print({"stdout": process.stdout, "stderr": process.stderr})
    def help(data):
        print(str({'enums': DecodeToMethod._member_names_}).replace("'", '"'))
    def unknown():
        print({"stdout": "", "stderr": "Method does not exist"})

        
        
        
#Enum referencing to functions
class DecodeToMethod(Enum):
    EXECUTE_SYS = Executions.execute_system.__name__
    HELP = Executions.help.__name__
    

if __name__ == "__main__":
    arguments = loads(" ".join(argv[1::]).replace("'", '"'))
    
    try:
        #Do some magic fuckery to extract JSON data from arguments given at execution to turn it into an Enum reference.
        #Hate using exec, how hacky >:(
        exec(f'Executions.{DecodeToMethod[arguments["execution"]].value}({arguments["executionData"]})')
    except KeyError:
        Executions.unknown()
        
