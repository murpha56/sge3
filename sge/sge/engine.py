import random
import sys
import copy
import itertools
import numpy as np
import sge.grammar as grammar
import sge.logger as logger
from datetime import datetime
from tqdm import tqdm
from sge.operators.recombination import crossover, context_aware_crossover, single_point_crossover
from sge.operators.mutation import mutate, shrinkmutate
from sge.operators.selection import tournament, doubletournamentsmall, doubletournamentlarge, samesizeind, roulette_wheel_selection, lexicase_selection
from sge.parameters import (
    params,
    set_parameters,
    load_parameters
)

#hybrid optimisation
from scipy import optimize


def generate_random_individual_grow():
    #creates empty template
    genotype = [[] for key in grammar.get_non_terminals()]
    #finds tree depth and populates template with codons
    tree_depth = grammar.recursive_individual_creation_grow(genotype, grammar.start_rule()[0], 0)
    return {'genotype': genotype, 'fitness': None, 'tree_depth' : tree_depth}

def generate_random_individual_full():
    #creates empty template
    genotype = [[] for key in grammar.get_non_terminals()]
    #finds tree depth and populates template with codons
    tree_depth = grammar.recursive_individual_creation_full(genotype, grammar.start_rule()[0], 0)
    return {'genotype': genotype, 'fitness': None, 'tree_depth' : tree_depth}

def generate_random_individual_ptc2():
    #creates empty template
    genotype = [[] for key in grammar.get_non_terminals()]
    init_tree_depth  = grammar.recursive_individual_creation_ptc2(genotype, grammar.start_rule()[0], 0, 0)
    return {'genotype': genotype, 'fitness': None, 'init_tree_depth' : init_tree_depth}


def make_initial_population():
    if params['INITIALISATION'] == "grow":
        for i in range(params['POPSIZE']):
            yield generate_random_individual_grow()
    elif params['INITIALISATION'] == "full":
        for i in range(params['POPSIZE']):
            yield generate_random_individual_full()
    elif params['INITIALISATION'] == "sensible":
        for i in range(params['POPSIZE']):
            if i < (params['POPSIZE']/2):
                yield generate_random_individual_grow()
            else:
                yield generate_random_individual_full()
    elif params['INITIALISATION'] == "ptc2":
        for i in range(params['POPSIZE']):
            yield generate_random_individual_ptc2()
    elif params['INITIALISATION'] == "test":
        for i in range(params['POPSIZE']):
            yield add_seeded_individual()
    else:
        print("Error, selection method invalid")


def add_seeded_individual():
    genotype = [[0],[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0], [0], [0], [0], [0], [0], [0], [0]]
    tree_depth = 9
    return {'genotype': genotype, 'fitness': None, 'tree_depth' : tree_depth}



def evaluate(ind, eval_func):
    mapping_values = [0 for i in ind['genotype']]
    #print(mapping_values)
    #print(ind['genotype'])

    #only return expansions when using PTC2
    phen, tree_depth = grammar.mapping(ind['genotype'], mapping_values)
    #print(eval(phen))
    #print(tree_depth)
    quality, test_error_1, test_error_2, other_info = eval_func.evaluate(phen)
    #use with lexicase
    #quality, caseQuality, other_info = eval_func.evaluate(phen, "training")
    #test_quality, test_caseQuality, other_test_info = eval_func.evaluate(phen, "test")


# For POET
#    print("Mapped Ind...")
#    print(phen)
#    print(len(phen))

#    phensplit = phen.split()
#    print(len(phensplit))
    #print(f'List of Words ={phen.split()}')
#    print(phensplit[0])
#    print(float(phensplit[1]))
#    num_rules = int(len(phensplit)/2)
#    for i in range(num_rules):
#        myrule = phensplit[i*2]
#        print(myrule)
#        print("A" in myrule)

    ind['phenotype'] = phen
    ind['fitness'] = quality
    ind['test_fitness1'] = test_error_1
    ind['test_fitness2'] = test_error_2
    ind['other_info'] = other_info
    ind['mapping_values'] = mapping_values
    ind['tree_depth'] = tree_depth



def hybrid_fit(ind, evaluation_function):
    hybrid_pool = []
    evaluate(ind,evaluation_function)
    hybrid_pool.append(ind)


    #for symbolic regression grammar
    chose_prod = 2 + random.randint(0,2)
    a = 4
    b = 5
    #this will change with each problem
    c = 76

    num_of_prods = len(ind['genotype'][chose_prod])

    if chose_prod == 2:
        terms = a
        num_perm = pow(terms,num_of_prods)
    elif chose_prod == 3:
        terms = b
        num_perm = pow(terms,num_of_prods)
    elif chose_prod == 4:
        terms = c
        num_perm = pow(terms,num_of_prods)

    if num_perm < 100:
        for i in range(num_perm):
            res = [ele for ele in itertools.product(range(0, terms), repeat = num_of_prods)]

            permut_ind = copy.deepcopy(ind)
            permut_ind['genotype'][chose_prod] = list(res[i])

            evaluate(permut_ind,evaluation_function)
            hybrid_pool.append(permut_ind)

    else:
        for i in range(100):
            res = list(np.random.randint(low = terms, size=num_of_prods))

            permut_ind = copy.deepcopy(ind)
            permut_ind['genotype'][chose_prod] = res

            evaluate(permut_ind,evaluation_function)
            hybrid_pool.append(permut_ind)


    hybrid_pool.sort(key=lambda i: i['fitness'])

    for a in range(min(10, num_perm)):
        if (hybrid_pool[0]['fitness'] == hybrid_pool[a]['fitness']):
            tie_breaker = a

    return hybrid_pool[random.randint(0,a)]


def setup(parameters_file_path = None):
    if parameters_file_path is not None:
        load_parameters(file_name=parameters_file_path)
    set_parameters(sys.argv[1:])
    if params['SEED'] is None:
        params['SEED'] = int(datetime.now().microsecond)
    logger.prepare_dumps()
    random.seed(params['SEED'])
    grammar.set_path(params['GRAMMAR'])
    grammar.read_grammar()
    grammar.set_max_tree_depth(params['MAX_TREE_DEPTH'])
    grammar.set_min_init_tree_depth(params['MIN_TREE_DEPTH'])


def evolutionary_algorithm(evaluation_function=None):
    setup()
    population = list(make_initial_population())
    it = 0
    #hybrid optimisation
#    for i in population:
#        hybrid_fit(i, evaluation_function)
    while it <= params['GENERATIONS']:
        for i in population:
            if i['fitness'] is None:
                evaluate(i, evaluation_function)
        population.sort(key=lambda x: x['fitness'])

        logger.evolution_progress(it, population)
        new_population = population[:params['ELITISM']]
        while len(new_population) < params['POPSIZE']:
            if random.random() < params['PROB_CROSSOVER']:
                if params['SELECTION_STRATEGY'] == "Lexicase":
                    p1 = lexicase_selection(population)
                    p2 = lexicase_selection(population)
                elif params['SELECTION_STRATEGY'] == "RouletteWheel":
                    p1 = roulette_wheel_selection(population)
                    p2 = roulette_wheel_selection(population)
                elif params['SELECTION_STRATEGY'] == "SameSizeTournament":
                    p1 = tournament(population, params['TSIZE'])
                    p2 = samesizeind(population, params['TSIZE'], p1)
                elif params['SELECTION_STRATEGY'] == "DoubleTournament":
                    if random.random() < params['PROB_CROSSOVER']/2:
                        p1 = doubletournamentsmall(population, params['TSIZE'])
                        p2 = doubletournamentsmall(population, params['TSIZE'])
                    else:
                        p1 = doubletournamentlarge(population, params['TSIZE'])
                        p2 = doubletournamentlarge(population, params['TSIZE'])
                else:
                    p1 = tournament(population, params['TSIZE'])
                    p2 = tournament(population, params['TSIZE'])

                if params['CROSSOVER_STRATEGY'] == "SinglePoint":
                    ni = single_point_crossover(p1, p2)
                elif params['CROSSOVER_STRATEGY'] == "ContextAware":
                    ni = context_aware_crossover(p1, p2, params['PROB_CONTEXT'])
                else:
                    ni = crossover(p1, p2)

            else:
                ni = tournament(population, params['TSIZE'])

            if params['MUTATION_STRATEGY'] == "Shrink":
                ni = shrinkmutate(ni, params['PROB_MUTATION'], it, params['GENERATIONS'])
            elif params['MUTATION_STRATEGY'] == "Alt":
                ni = mutateAlt(ni, params['PROB_MUTATION'])
            else:
                ni = mutate(ni, params['PROB_MUTATION'])

            new_population.append(ni)
        population = new_population
        it += 1
