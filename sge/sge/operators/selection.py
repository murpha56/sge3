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


def lexicase_selection(population):
    """
    Given an entire population, choose an individualsthat does the best on
    randomly chosen training cases. Allows for selection of 'specialist' individuals
    that do very well on some training cases even if they do poorly on others.
    :param population: A population from which to select individuals.
    :return: A selected individual from lexicase selection -- allows
             repeated individuals
    """
    # Initialise list of lexicase selections
    winner = []

    # Max or min
    #maximise_fitness = params['FITNESS_FUNCTION'].maximise

    # The flag "INVALID_SELECTION" allows for selection of invalid individuals.
    #if params['INVALID_SELECTION']:
    #    available = population
    #else:
    #    available = [i for i in population if not i.fitness == sys.maxsize]

    available = [i for i in population if not i['fitness'] == sys.maxsize]

    # Basic ensure individuals have been tested on same number of test cases, and that there is at least one test case
    assert (len(available[0]['test_case_results']) == len(available[1]['test_case_results']))
    assert (len(available[0]['test_case_results']) > 0)

    #while len(winners) < params['GENERATION_SIZE']:
        # Random ordering of test cases
    random_test_case_list = list(range(len(available[0]['test_case_results'])))
    random.shuffle(random_test_case_list)

        # Only choose from a sample not from the entire available population

    #    if params['LEXICASE_TOURNAMENT']:
    #        candidates = sample(available, params['TOURNAMENT_SIZE'])
    #    else:
    candidates = available
    candidate_size = len(candidates)

    while candidate_size > 0:
        # Calculate best score for chosen test case from candidates
        scores = []
        for ind in candidates:
            scores.append(ind['test_case_results'][random_test_case_list[0]])
        best_score = min(scores)
        #best_score = max(scores)
        #print(best_score)

        #if maximise_fitness:
        #    best_score = max(scores)
        #else:
        #    best_score = min(scores)

        # Only retain individuals who have the best score for the test case
        remaining = []
        candidate_size = 0
        for ind in candidates:
            if ind['test_case_results'][random_test_case_list[0]] == best_score:
                remaining.append(ind)
                candidate_size += 1
        candidates = remaining

            # If only one individual remains, choose that individual
        if len(candidates) == 1:
            winner.append(candidates[0])
            break

            # If this was the last test case, randomly choose an individual from remaining candidates
        elif len(random_test_case_list) == 1:

            # Penalize longer solutions
            #min_nodes = params["MAX_TREE_NODES"] + 1
            #best_ind = None
            #for ind in candidates:
            #    if ind.nodes < min_nodes:
            #        best_ind = ind
            #        min_nodes = ind.nodes
            #winner.append(best_ind)

            # Choose randomly among solutions
            winner.append(random.sample(candidates, 1)[0])
            break

            # Go to next test case and loop
        else:
            random_test_case_list.pop(0)

    # Return the population of lexicase selections.
    return copy.deepcopy(winner[0])
