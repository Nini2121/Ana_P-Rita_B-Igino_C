#para os argumentos iniciais dos limites
import argparse
from textwrap import indent
import json
import os
import color_segmenter

#função para a definição dos limites do código e das condições iniciais
def arg():
    parser = argparse.ArgumentParser(description='PSR augmented reality paint') #creates a argumentParser object
    parser.add_argument('-j','--json', default='limits.json', dest="file", type=str, action="store", help='Full path to json file') 
    
    args = parser.parse_args() #parse the , presents the scheme shown whith all the information
    
    #creates a dictionary 
    return vars(args)


def main():
    args = arg()

    if not os.path.exists(args["file"]):
        raise FileNotFoundError

    #--------
    #Initialization
    #---------
    

    #--------
    #Execution
    #---------
  
    #--------
    #Processing 
    #---------

    #--------
    #Visualization 
    #---------

    #--------
    #Termination
    #---------
if __name__ == '__main__':
    main()
