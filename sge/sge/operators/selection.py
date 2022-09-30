import random
import copy
import numpy as np

def roulette_wheel_selection(population):
    population_fitness = sum([i['fitness'] for i in population])
    probabilities = [i['fitness']/population_fitness for i in population]
    return np.random.choice(population, p=probabilities)

def tournament(population, tsize=3):
    pool = random.sample(population, tsize)
    pool.sort(key=lambda i: (i['fitness'], i['tree_depth']))
    if (pool[0]['tree_depth'] > pool[1]['tree_depth']) and (1.01*pool[0]['fitness'] > pool[1]['fitness']):
        return copy.deepcopy(pool[1])
    else:
        return copy.deepcopy(pool[0])


def doubletournamentsmall(population, tsize=6):
    pool = random.sample(population, tsize)
    pool.sort(key=lambda i: i['tree_depth'])
    pool = pool[0:round(tsize/2)]
    pool.sort(key=lambda i: i['fitness'])
    return copy.deepcopy(pool[0])

def doubletournamentlarge(population, tsize=6):
    pool = random.sample(population, tsize)
    pool.sort(key=lambda i: i['tree_depth'])
    pool = pool[-round(tsize/2):]
    pool.sort(key=lambda i: i['fitness'])
    return copy.deepcopy(pool[0])

def samesizeind(population, tsize, ind):
    pool = random.sample(population, tsize)
    pool.sort(key=lambda i: i['fitness'])
    if abs(pool[0]['tree_depth'] - ind['tree_depth']) < 3:
        return copy.deepcopy(pool[0])
    elif abs(pool[1]['tree_depth'] - ind['tree_depth']) < 3:
        return copy.deepcopy(pool[1])
    elif abs(pool[2]['tree_depth'] - ind['tree_depth']) < 3:
            return copy.deepcopy(pool[2])
    else:
        return copy.deepcopy(pool[0])
