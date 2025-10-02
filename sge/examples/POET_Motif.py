import random
import pandas as pd
from sge.parameters import params
from sge.utilities.protected_math import _log_, _div_, _exp_, _inv_, _sqrt_, protdiv
from numpy import cos, sin, corrcoef, isnan
from sklearn.model_selection import train_test_split
from scipy import stats

def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step


class Rule:
	def __init__(self, pattern, weight, status):
		self.pattern = pattern
		self.weight = weight
		self.status = status

class POET_Motif():
    def __init__(self, run=0, has_test_set=True, invalid_fitness=9999999):
        self.__train_set = []
        self.__test_set = None
        self.__invalid_fitness = invalid_fitness
        self.run = run
        self.has_test_set = has_test_set

        self.TT = pd.read_csv('resources/POET/translation/amino_to_amino.csv')

        self.rules = []
        self.usedRules = {}
        self.fitness = 0

        self.ruleSize = 9 #settings.rule_size
        self.maxRuleCount = 100 #settings.maximum_rule_count
        self.minWeight = 0.0 #settings.rule_weight_min
        self.maxWeight = 10.0 #settings.rule_weight_max

        self.read_dataset()
        self.init_pattern()




    def read_dataset(self):
        dataset = []
        test = []

        dataset = pd.read_csv('resources/POET/learnall.csv')
        test = pd.read_csv('resources/POET/mock.csv')

        self.__train_set = dataset
        self.__test_set = test
        #print(dataset)
        #print(test)

        self.rules = []
        self.usedRules = {}
        self.fitness = 0

        Patterns = dataset['sequence']
        Weights = dataset['fitness']



        try:
            tmpStatus = dataset['status']
        except:
            print("Pro-Predictor: model {} does not have status column, putting 0 for all.")
            tmpStatus = [0]*len(Patterns)

        for i in range(0, len(Patterns) - 1):
			# print (str(i) + " " + str(tmpPatterns[i]) + " " + str(tmpWeights[i]))
            rule = Rule(Patterns[i],Weights[i], tmpStatus[i])
            self.rules.append(rule)
            #print(Patterns[i])
            #print(Weights[i])
            #print(tmpStatus[i])
        pass



    def init_pattern(self):
        codes = self.TT['code']
        for i in range(random.randint(1, int(self.maxRuleCount/3))):
            pattern = ""
            weight = round(random.uniform(self.minWeight, self.maxWeight), 2)
                # Add these many rules
            for j in range(random.randint(1, self.ruleSize)):
				# Rule size is calculated randomly, and now we need to select a random combination of codes with a specified size
                code = codes[random.randint(0, codes.size - 1)]
                #print(code)
                randomchar = code[random.randint(0, (len(code) - 1))]
                pattern += randomchar
                #print(pattern)
            rule = Rule(pattern, weight, 0)
            self.rules.append(rule)

        #for i in self.rules:
        #    print(str(i.pattern) + " => " + str(i.weight))

		# print ("\n\n")
        self.bubbleSort()


    def bubbleSort(self):
        n = len(self.rules)
	    # Traverse through all array elements
        for i in range(n):
	        # Last i elements are already in place
            for j in range(0, n-i-1):
	            # traverse the array from 0 to n-i-1
	            # Swap if the element found is greater
	            # than the next element
                if len(self.rules[j].pattern) < len(self.rules[j+1].pattern):
                    self.rules[j], self.rules[j+1] = self.rules[j+1], self.rules[j]



    def eval(self, individual, sequence):
        # This is the starting position of the sequence that we're looking at each time.
        measuredFitness = 0
        individual_list = individual.split()
        num_rules = len(individual_list)/2

        for i in range(num_rules):
            myrule = individual_list[i*2]

            if myrule in sequence:
                measuredFitness += individual_list[(i*2)+1]


        return measuredFitness



    def get_error(self, individual, dataset):
        pred_error = 0
        for case in dataset:
            mysequence = dataset['sequence'][:-1]
            print(mysequence)
            target = dataset['fitness'][:-1]
            print(target)
            try:
                output = eval(individual, mysequence)
                pred_error += (target - output)**2
            except (SyntaxError, ValueError, OverflowError, MemoryError, FloatingPointError, ZeroDivisionError):
                return self.__invalid_fitness
        return pred_error

    def get_test_error(self, individual, dataset, slope, intercept):
        pred_error = 0
        for case in dataset:
            target = case[-1]
            try:
                output = eval(individual, globals(), {"x": case[:-1]})
                scaled_output = intercept + slope*output
                pred_error += (target - scaled_output)**2
            except (SyntaxError, ValueError, OverflowError, MemoryError, FloatingPointError, ZeroDivisionError):
                return self.__invalid_fitness
        return pred_error

    def get_corr_error(self, individual, dataset):
        corr_error = 0
        slope = 0
        intercept = 0
        outputs = []
        targets = []
        for case in dataset:
            target = case[-1]
            try:
                output = eval(individual, globals(), {"x": case[:-1]})
                outputs.append(output)
                targets.append(target)
            except (SyntaxError, ValueError, OverflowError, MemoryError, FloatingPointError, ZeroDivisionError):
                return self.__invalid_fitness, 0, 0

        corr_matrix = corrcoef(targets, outputs)
        try:
            corr_error = 1 - (corr_matrix[0,1]**2)
            if isnan(corr_error):
                corr_error = 1
        except (SyntaxError, ValueError, OverflowError, MemoryError, FloatingPointError, ZeroDivisionError):
            return self.__invalid_fitness, 0, 0

        slope, intercept, r_value, p_value, std_err = stats.linregress(targets, outputs)

        return corr_error, slope, intercept


    def evaluate(self, individual):
        error = 0.0
        test_error = 0.0
        if individual is None:
            return None

        if params['ERROR_METRIC'] == "Correleation":
            error, slope, intercept = self.get_corr_error(individual, self.__train_set)
        else:
            error = self.get_error(individual, self.__train_set)
            error = _sqrt_( error)

        if error is None:
            error = self.__invalid_fitness
        if isnan(error):
            error = self.__invalid_fitness

        if self.__test_set is not None:
            test_error = 0
            if params['ERROR_METRIC'] == "Correleation":
                test_error = self.get_test_error(individual, self.__test_set, slope, intercept)
            else:
                test_error = self.get_error(individual, self.__test_set)

            #test_error = _sqrt_( test_error / float(self.__RRSE_test_denominator))

        return error, test_error, {'generation': 0, "evals": 1, "test_error": test_error}


if __name__ == "__main__":
    import sge
    sge.setup("parameters/POET_Motif.yml")
    eval_func = POET_Motif(params['RUN'])
    sge.evolutionary_algorithm(evaluation_function=eval_func)
