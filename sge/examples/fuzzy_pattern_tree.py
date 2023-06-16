import random
from sge.parameters import params
from sge.utilities.protected_math import _log_, _div_, _exp_, _inv_, _sqrt_, protdiv, root, WA, OWA, concentrate, dilation, complement
from numpy import cos, sin, savetxt, isnan
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, fbeta_score, matthews_corrcoef, accuracy_score, fowlkes_mallows_score

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
        test = []
        trn_ind = []
        tst_ind = []
        if params['PROBLEM'] == "AusCredit":
            with open('resources/AusCredit/AusCreditFinal', 'r') as dataset_file:
                for line in dataset_file:
                    dataset.append([float(value.strip(" ")) for value in line.split(" ") if value != ""])
        elif params['PROBLEM'] == "Pima":
            with open('resources/Pima/PimaFinal', 'r') as dataset_file:
                for line in dataset_file:
                    dataset.append([float(value.strip(" ")) for value in line.split(" ") if value != ""])
        elif params['PROBLEM'] == "Transfusion":
            with open('resources/Transfusion/TransfusionFinal', 'r') as dataset_file:
                for line in dataset_file:
                    dataset.append([float(value.strip(" ")) for value in line.split(" ") if value != ""])
        elif params['PROBLEM'] == "Heart":
            with open('resources/Heart/HeartFinalSub2', 'r') as dataset_file:
                for line in dataset_file:
                    dataset.append([float(value.strip(" ")) for value in line.split(" ") if value != ""])
        elif params['PROBLEM'] == "Recidivism":
            with open('resources/Recidivism/RecidivismFinal', 'r') as dataset_file:
                for line in dataset_file:
                    dataset.append([float(value.strip(" ")) for value in line.split(" ") if value != ""])
        elif params['PROBLEM'] == "Credit":
            with open('resources/Credit/CreditFinal', 'r') as dataset_file:
                for line in dataset_file:
                    dataset.append([float(value.strip(" ")) for value in line.split(" ") if value != ""])
        elif params['PROBLEM'] == "Census":
            with open('resources/Census/IncomeFinal', 'r') as dataset_file:
                for line in dataset_file:
                    dataset.append([float(value.strip(" ")) for value in line.split(" ") if value != ""])
            with open('resources/Census/IncomeTestFinal', 'r') as test_file:
                for line in test_file:
                    test.append([float(value.strip(" ")) for value in line.split(" ") if value != ""])
        elif params['PROBLEM'] == "Marketing":
            with open('resources/Marketing/MarketingFinal', 'r') as dataset_file:
                for line in dataset_file:
                    dataset.append([float(value.strip(" ")) for value in line.split(" ") if value != ""])
        else:
            print("Not a problem, please pick a valid option")

        #print(len(dataset))
        columns = list(zip(*dataset))
        #print(columns[1])
        #print(columns[-1])

        if params['PROBLEM'] == "Census":
            self.__train_set = dataset
            self.__test_set = test
        else:
            #create traing/test split - stratify so same proportion of c;asses in both
            self.__train_set, self.__test_set = train_test_split(dataset, test_size=0.25, random_state=params['SEED'], stratify=columns[-1])

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
        return pred_error, len(dataset)

    def get_accuracy(self, individual, dataset):
        hits = 0
        for case in dataset:
            target = case[-1]
            try:
#                print("I got here")
                output = eval(individual, globals(), {"x": case[:-1]})
                if ((output[0] >= output[1] and target == 0.0) or (output[0] < output[1] and target == 1.0)):
                    hits += 1
                #pred_error += (target - output)**2
            except (SyntaxError, ValueError, OverflowError, MemoryError, FloatingPointError):
                return 0,
        return hits

    def get_accuracy_metrics(self, individual, dataset):
        outputs = []
        targets = []
        for case in dataset:
            target = case[-1]
            targets.append(target)
            #print("Target is:")
            #print(target)
            try:
                output = eval(individual, globals(), {"x": case[:-1]})
                #print("Output is:")
                #print(output)
                if output[0] >= output[1]:
                    outputs.append(0.0)
                else:
                    outputs.append(1.0)
            except (SyntaxError, ValueError, OverflowError, MemoryError, FloatingPointError):
                return  0, 0, 0, 0, 0,


        try:
            MCC = matthews_corrcoef(targets, outputs)
            accuracy = accuracy_score(targets, outputs)
            F1_score = fbeta_score(targets, outputs, beta=1)
            F2_score = fbeta_score(targets, outputs, beta=2)
            FMS = fowlkes_mallows_score(targets, outputs)

            if isnan(MCC) or isnan(accuracy) or isnan(F1_score) or isnan(F2_score) or isnan(FMS):
                MCC = 0
                accuracy = 0
                F1_score = 0
                F2_score = 0
                FMS = 0
        except (SyntaxError, ValueError, OverflowError, MemoryError, FloatingPointError):
            return 0, 0, 0, 0, 0,

        return MCC, accuracy, F1_score, F2_score, FMS


    def evaluate(self, individual):
        error = 0.0
        test_error = 0.0
        if individual is None:
            return None

        if params['ERROR_METRIC'] == "RMSE":
            RMSE, size = self.get_error(individual, self.__train_set)
            RMSE = _sqrt_(RMSE/(2*size))
            MCC, accuracy, F1_score, F2_score, FMS = self.get_accuracy_metrics(individual, self.__train_set)
            error = RMSE
        elif params['ERROR_METRIC'] == "Accuracy":
            RMSE, size = self.get_error(individual, self.__train_set)
            RMSE = _sqrt_(RMSE/(2*size))
            MCC, accuracy, F1_score, F2_score, FMS = self.get_accuracy_metrics(individual, self.__train_set)
            error = 1 - accuracy
        elif params['ERROR_METRIC'] == "F1Score":
            RMSE, size = self.get_error(individual, self.__train_set)
            RMSE = _sqrt_(RMSE/(2*size))
            MCC, accuracy, F1_score, F2_score, FMS = self.get_accuracy_metrics(individual, self.__train_set)
            error = 1 - F1_score
        elif params['ERROR_METRIC'] == "F2Score":
            RMSE, size = self.get_error(individual, self.__train_set)
            RMSE = _sqrt_(RMSE/(2*size))
            MCC, accuracy, F1_score, F2_score, FMS = self.get_accuracy_metrics(individual, self.__train_set)
            error = 1 - F2_score
        elif params['ERROR_METRIC'] == "MCC":
            RMSE, size = self.get_error(individual, self.__train_set)
            RMSE = _sqrt_(RMSE/(2*size))
            MCC, accuracy, F1_score, F2_score, FMS = self.get_accuracy_metrics(individual, self.__train_set)
            error = 1 - MCC
        elif params['ERROR_METRIC'] == "FMS":
            RMSE, size = self.get_error(individual, self.__train_set)
            RMSE = _sqrt_(RMSE/(2*size))
            MCC, accuracy, F1_score, F2_score, FMS = self.get_accuracy_metrics(individual, self.__train_set)
            error = 1 - FMS
        else:
            print("Not a valid Error Metric")
        #error = _sqrt_( error /self.__RRSE_train_denominator)

        if error is None:
            error = self.__invalid_fitness


        if self.__test_set is not None:
            train_error = 0
            test_error = 0
            train_error = self.get_accuracy(individual, self.__train_set)
            test_error = self.get_accuracy(individual, self.__test_set)
            #test_error = self.get_error(individual, self.__test_set)
            #test_error = _sqrt_(test_error)
            #test_error = _sqrt_( test_error / float(self.__RRSE_test_denominator))

        return error, test_error, {"Hits": train_error, "RMSE":RMSE, "MCC": MCC, "Acc": accuracy, "F1Score": F1_score, "F2Score": F2_score, "FMS": FMS}


if __name__ == "__main__":
    import sge
    sge.setup("parameters/fpt_standard.yml")
    eval_func = FuzzyPatternTree(params['RUN'])
    sge.evolutionary_algorithm(evaluation_function=eval_func)
