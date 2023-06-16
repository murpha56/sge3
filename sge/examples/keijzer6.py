import random
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

class Keijzer6():
    def __init__(self, run=0, has_test_set=True, invalid_fitness=9999999):
        self.__train_set = []
        self.__test_set = None
        self.__invalid_fitness = invalid_fitness
        self.run = run
        self.has_test_set = has_test_set
        self.read_dataset()
        self.calculate_rrse_denominators()


    def read_dataset(self):

        def keijzer6(inp):
            return sum([1.0/i for i in range(1,inp+1,1)])

        train_range = list(drange(1,51,1))

        #function = eval(self.function)
        y_train = map(keijzer6,train_range)
        self.__train_set = list(zip(train_range, y_train))
        self.__number_of_variables = 1
        self.training_set_size = len(self.__train_set)

        test_range = list(drange(51,121,1))

        y_test = map(keijzer6,test_range)
        self.__test_set = list(zip(test_range, y_test))
        self.test_set_size = len(self.__test_set)


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
                output = eval(individual, globals(), {"x": case[:-1]})
                pred_error += (target - output)**2
            except (SyntaxError, ValueError, OverflowError, MemoryError, FloatingPointError):
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
            except (SyntaxError, ValueError, OverflowError, MemoryError, FloatingPointError):
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
            except (SyntaxError, ValueError, OverflowError, MemoryError, FloatingPointError):
                return self.__invalid_fitness, 0, 0

        corr_matrix = corrcoef(targets, outputs)
        try:
            corr_error = 1 - (corr_matrix[0,1]**2)
            if isnan(corr_error):
                corr_error = 1
        except (SyntaxError, ValueError, OverflowError, MemoryError, FloatingPointError):
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
            error = _sqrt_( error /self.__RRSE_train_denominator)

        if error is None:
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
    sge.setup("parameters/keijzer6.yml")
    eval_func = Keijzer6(params['RUN'])
    sge.evolutionary_algorithm(evaluation_function=eval_func)
