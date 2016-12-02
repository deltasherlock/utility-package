# DeltaSherlock. See README.md for usage. See LICENSE for MIT/X11 license info.
# pylint: disable=
"""
DeltaSherlock server training module. Contains code for creating trained machine
learning models from training fingerprints
"""
from enum import Enum, unique
import numpy as np
from sklearn import svm, tree, preprocessing
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, \
    GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from deltasherlock.common.fingerprinting import Fingerprint

@unique
class MLAlgorithm(Enum):
    """
    An enumerated type containing representations of each supported machine
    learning algorithm
    """
    undefined = 0
    logistic_regression = 1
    decision_tree = 2
    random_forest = 3
    svm_rbf = 4
    svm_linear = 5
    adaboost = 6
    gradient_boosting = 7

class MLModel(object):
    """
    Container for items needed to machine learn
    """
    def __init__(self, fingerprints: list, algorithm: MLAlgorithm):
        """
        Initialize and train the model with a list of Fingerprints using the
        specified MLAlgorithm
        """
        self.algorithm = algorithm
        if self.algorithm == MLAlgorithm.logistic_regression:
            self.model = LogisticRegression(C=10000)
        elif self.algorithm == MLAlgorithm.decision_tree:
            self.model = tree.DecisionTreeClassifier()
        elif self.algorithm == MLAlgorithm.random_forest:
            self.model = RandomForestClassifier(n_estimators=100)
        elif self.algorithm == MLAlgorithm.svm_rbf:
            self.model = svm.SVC(C=500, gamma=1, probability=True)
        elif self.algorithm == MLAlgorithm.svm_linear:
            self.model = svm.LinearSVC(C=500)
        elif self.algorithm == MLAlgorithm.adaboost:
            self.model = AdaBoostClassifier()
        elif self.algorithm == MLAlgorithm.gradient_boosting:
            self.model = GradientBoostingClassifier(learning_rate=0.1, n_estimators=40,
                                                    max_depth=3)
        else:
            raise ValueError("Invalid MLAlgorithm specified")

        #Setup ML Resources
        self.classifier = OneVsRestClassifier(self.model)
        self.binarizer = preprocessing.MultiLabelBinarizer()

        #Creates list of labels, in order
        self.labels = []
        for fingerprint in fingerprints:
            self.labels.append(fingerprint.labels)

        X = np.nan_to_num(np.array(fingerprints))
        y = self.binarizer.fit_transform(self.labels)
        self.classifier.fit(X, y)

    def predict(self, fingerprint: Fingerprint):
        prediction = None

        # get the class probabilities
        probabilities = self.classifier.predict_proba(fingerprint.reshape(1, -1))

        # Prevent wild quantity predictions from breaking everything
        #TODO Don't hardcode 50
        if fingerprint.predicted_quantity > 0 and fingerprint.predicted_quantity <= 50:
            # get top n class probabilities
            topNClasses = np.argpartition(probabilities[0], -fingerprint.predicted_quantity)[-fingerprint.predicted_quantity:]

            # create a sparse array of 1's and 0's marking the label indices
            prediction = np.zeros((1, self.classifier.classes_.shape[0]))
            for index in topNClasses:
                prediction[0][index] = 1
        else:
            # Fall back to regular old prediction
            prediction = self.classifier.predict(fingerprint.reshape(1, -1))

        return self.binarizer.inverse_transform(prediction)[0]
