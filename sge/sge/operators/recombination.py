import random
import sge.grammar as grammar


def crossover(p1, p2):
    xover_p_value = 0.5
    gen_size = len(p1['genotype'])
    mask = [random.random() for i in range(gen_size)]
    genotype = []
    for index, prob in enumerate(mask):
        if prob < xover_p_value:
            genotype.append(p1['genotype'][index][:])
        else:
            genotype.append(p2['genotype'][index][:])
    mapping_values = [0] * gen_size
    # compute nem individual
    _, tree_depth = grammar.mapping(genotype, mapping_values)
    return {'genotype': genotype, 'fitness': None, 'mapping_values': mapping_values, 'tree_depth': tree_depth}


def context_aware_crossover(p1, p2, prob):
    #xover_p_value = list(map(lambda x, y: 0.5 / (max(x,y) + 1), p1['mapping_values'], p2['mapping_values']))
    non_terminals = grammar.get_non_terminals()
    non_of_options_by_non_terminal = grammar.count_number_of_options_in_production()
    # xover_p_value = list(map(lambda x , y: (y / sum(p1['mapping_values']))/ non_of_options_by_non_terminal[x], non_terminals, p1['mapping_values']))
    xover_p_value = list(map(lambda x: prob / non_of_options_by_non_terminal[x], non_terminals))
    gen_size = len(p1['genotype'])
    # print(xover_p_value)
    # input()
    mask = [random.random() for i in range(gen_size)]
    genotype = []
    for index, prob in enumerate(mask):
        if prob < xover_p_value[index]:
            genotype.append(p1['genotype'][index][:])
        else:
            genotype.append(p2['genotype'][index][:])
    mapping_values = [0] * gen_size
    # compute nem individual
    _, tree_depth = grammar.mapping(genotype, mapping_values)
    #print(p1['phenotype'])
    #print(p2['phenotype'])
    #print(_)
    #input()
    return {'genotype': genotype, 'fitness': None, 'mapping_values': mapping_values, 'tree_depth': tree_depth}


def single_point_crossover(p1, p2):
    gen_size = len(p1['genotype'])
    cut_point = random.randint(1, gen_size - 1)
    genotype = p1['genotype'][0 : cut_point][:] + p2['genotype'][cut_point : ][:]
    mapping_values = [0] * gen_size
    # compute nem individual
    _, tree_depth = grammar.mapping(genotype, mapping_values)
    return {'genotype': genotype, 'fitness': None, 'mapping_values': mapping_values, 'tree_depth': tree_depth}
