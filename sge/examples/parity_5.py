"""
Lots of code taken from deap
"""
from sge.parameters import params
import random

input_names = ['b0', 'b1', 'b2', 'b3', 'b4']

PARITY_FANIN_M = 5
PARITY_SIZE_M = 2**PARITY_FANIN_M

inputs = [None] * PARITY_SIZE_M
outputs = [None] * PARITY_SIZE_M

for i in range(PARITY_SIZE_M):
    inputs[i] = [None] * PARITY_FANIN_M
    value = i
    dividor = PARITY_SIZE_M
    parity = 1
    for j in range(PARITY_FANIN_M):
        dividor /= 2
        if value >= dividor:
            inputs[i][j] = 1
            parity = int(not parity)
            value -= dividor
        else:
            inputs[i][j] = 0
    outputs[i] = parity

class Parity5():
    def __init__(self, run=0):
        self.run = run

    def evaluate(self, individual):
        error = PARITY_SIZE_M
        for i, inpt in enumerate(inputs):
            res = eval(individual, dict(zip(input_names, inpt)))
            if res == outputs[i]:
                error -= 1
        return error, error, {}

if __name__ == "__main__":
    import sge
    sge.setup("parameters/parity.yml")
    eval_func = Parity5(params['RUN'])
    sge.evolutionary_algorithm(evaluation_function=eval_func)
