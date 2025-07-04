import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.gen_genesis_funcs import gen_genesis
from utils.gen_validators_funcs import gen_validators

PWD = os.getcwd()

#print pwd
print(PWD)

if __name__ == "__main__":

    #generate genesis
    gen_genesis(PWD)

    #generate validators
    gen_validators(PWD)

    #run blockchain

