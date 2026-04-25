import numpy as np
from scipy.stats import multivariate_normal


class CustomQDA:
    def __init__(self, reg_param=0.0):
        self.reg_param = reg_param
        self.priors = None
        self.means = None
        self.covs = None
        self.classes = None
        self.dim = None

    def fit(self, X, y):
        self.classes = np.unique(y)
        self.dim = X.shape[1]
        self.priors = {}
        self.means = {}
        self.covs = {}

        for c in self.classes:
            X_c = X[y == c]
            self.priors[c] = len(X_c) / len(X)
            self.means[c] = np.mean(X_c, axis=0)

            raw_cov = np.cov(X_c, rowvar=False)
            identity_matrix = np.eye(self.dim)
            self.covs[c] = (1 - self.reg_param) * raw_cov + self.reg_param * identity_matrix

        return self

    def predict_proba(self, X):
        n_samples = X.shape[0]
        n_classes = len(self.classes)
        probabilities = np.zeros((n_samples, n_classes))

        for i, c in enumerate(self.classes):
            pdf_values = multivariate_normal.pdf(
                X,
                mean=self.means[c],
                cov=self.covs[c],
                allow_singular=True,
            )
            probabilities[:, i] = pdf_values * self.priors[c]

        sum_probs = np.sum(probabilities, axis=1, keepdims=True)
        normalized_probabilities = np.divide(
            probabilities,
            sum_probs,
            out=np.zeros_like(probabilities),
            where=sum_probs != 0,
        )

        return normalized_probabilities

    def predict(self, X):
        posterior_probs = self.predict_proba(X)
        return self.classes[np.argmax(posterior_probs, axis=1)]
