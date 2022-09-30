import random
from sge.parameters import params
from sge.utilities.protected_math import _log_, _div_, _exp_, _inv_, _sqrt_, protdiv, root, WA, OWA, concentrate, dilation, complement
from numpy import cos, sin, savetxt
from sklearn.model_selection import train_test_split

def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

class FuzzyPatternTree():
    def __init__(self, run=0, has_test_set=True, invalid_fitness=9999999):
        self.__train_set = []
        self.__test_set = []
        self.__invalid_fitness = invalid_fitness
        self.run = run
        self.has_test_set = has_test_set
        self.read_dataset()
        self.calculate_rrse_denominators()


    def read_dataset(self):
        dataset = []
        trn_ind = []
        tst_ind = []
        if params['PROBLEM'] == "AusCredit":
            with open('resources/AusCredit/AusCreditFinal', 'r') as dataset_file:
                for line in dataset_file:
                    dataset.append([float(value.strip(" ")) for value in line.split(" ") if value != ""])
        elif params['PROBLEM'] == "Pima":
            with open('resources/Pima/Pima', 'r') as dataset_file:
                for line in dataset_file:
                    dataset.append([float(value.strip(" ")) for value in line.split(" ") if value != ""])
        else:
            with open('resources/Transfer/Transfer', 'r') as dataset_file:
                for line in dataset_file:
                    dataset.append([float(value.strip(" ")) for value in line.split(" ") if value != ""])

        #create traing/test split
        self.__train_set, self.__test_set = train_test_split(dataset, test_size=0.25, random_state=params['SEED'])
        #save training and test sets
        savetxt(params['EXPERIMENT_NAME'] + "/run_" + str(params['RUN']) + "/TrainData.csv", self.__train_set, delimiter =", ", fmt ='% s')
        savetxt(params['EXPERIMENT_NAME'] + "/run_" + str(params['RUN']) + "/TestData.csv", self.__test_set, delimiter =", ", fmt ='% s')


    def calculate_rrse_denominators(self):
        self.__RRSE_train_denominator = 0
        self.__RRSE_test_denominator = 0
        train_outputs = [entry[-1] for entry in self.__train_set]
        train_output_mean = float(sum(train_outputs)) / len(train_outputs)
        self.__RRSE_train_denominator = sum([(i - train_output_mean)**2 for i in train_outputs])
        if self.__test_set:
            test_outputs = [entry[-1] for entry in self.__test_set]
            test_output_mean = float(sum(test_outputs)) / len(test_outputs)
            self.__RRSE_test_denominator = sum([(i - test_output_mean)**2 for i in test_outputs])


    def get_error(self, individual, dataset):
        pred_error = 0
        for case in dataset:
            target = case[-1]
            try:
#                print("I got here")
                output = eval(individual, globals(), {"x": case[:-1]})
#                print(output)
                pred_error += ((1-target)-output[0])**2 + (target-output[1])**2
                #pred_error += (target - output)**2
            except (SyntaxError, ValueError, OverflowError, MemoryError, FloatingPointError):
                return self.__invalid_fitness
        return pred_error

    def get_accuracy(self, individual, dataset):
        hits = 0
        for case in dataset:
            target = case[-1]
            try:
#                print("I got here")
                output = eval(individual, globals(), {"x": case[:-1]})
                if ((output[0] >= output[1] and target == 0) or (output[0] < output[1] and target == 1)):
                    hits += 1
                #pred_error += (target - output)**2
            except (SyntaxError, ValueError, OverflowError, MemoryError, FloatingPointError):
                return self.__invalid_fitness
        return hits


    def evaluate(self, individual):
        error = 0.0
        test_error = 0.0
        if individual is None:
            return None

        error = self.get_error(individual, self.__train_set)
        error = _sqrt_(error)
        #error = _sqrt_( error /self.__RRSE_train_denominator)

        if error is None:
            error = self.__invalid_fitness


        if self.__test_set is not None:
            test_error = 0
            test_error = self.get_accuracy(individual, self.__test_set)
            #test_error = self.get_error(individual, self.__test_set)
            #test_error = _sqrt_(test_error)
            #test_error = _sqrt_( test_error / float(self.__RRSE_test_denominator))

        return error, {'generation': 0, "evals": 1, "test_error": test_error}


if __name__ == "__main__":
    import sge
    sge.setup("parameters/fpt_standard.yml")
    eval_func = FuzzyPatternTree(params['RUN'])
    sge.evolutionary_algorithm(evaluation_function=eval_func)
