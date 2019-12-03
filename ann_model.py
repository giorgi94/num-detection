import os
import random
import pickle
import numpy as np


def assure_path_exists(path, isfile=True):
    if isfile:
        dir_path = os.path.dirname(path)
    else:
        dir_path = path
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def sigmoid(x, prime=False):
    if prime:
        return sigmoid(x) * (1 - sigmoid(x))
    return 1 / (1 + np.exp(-x))


class ANNetworkBase:

    learning_rate = 0.5

    def activation_prime(self, x):
        return np.diagflat(self.activation(x, prime=True))

    def load_layers(self, layers):
        self.layers = layers
        self.last = len(layers) - 1

    def load_random_weights(self):
        self.biases = []
        self.weights = []

        n0 = self.layers[0]

        for n1 in self.layers[1:]:
            self.weights.append(2 * np.random.random((n1, n0)) - 1)
            self.biases.append(2 * np.random.random((n1, 1)) - 1)
            n0 = n1

    def forward(self, X):
        pass

    def backward(self, Y):
        pass

    def output(self):
        pass

    def check_error_norm(self, Y):
        return np.linalg.norm(Y - self.output())

    def train(self, X, Y):
        self.forward(X)
        self.backward(Y)

    def training(self, table, max_steps, each=1):

        table_data = table[:]

        for step in range(max_steps):
            error = []
            for row in table_data:
                X, Y = row
                self.train(X, Y)
                error.append(self.check_error_norm(Y))

            if step % each == 0:
                print(sum(error) / len(error))

            random.shuffle(table_data)

    def dump(self, path="dump.pkl"):
        path = os.path.abspath(path)
        assure_path_exists(path)

        with open(path, 'wb') as f:
            pickle.dump((self.weights, self.biases), f)

    def load(self, path='dump.pkl'):
        path = os.path.abspath(path)

        with open(path, 'rb') as f:
            self.weights, self.biases = pickle.load(f)


class ANNetwork(ANNetworkBase):

    def forward(self, X):
        self.z = [None]
        self.a = [X]

        layer = 0
        for w, b in zip(self.weights, self.biases):
            layer += 1
            self.z.append(w.dot(self.a[layer - 1]) + b)
            self.a.append(self.activation(self.z[layer]))

    def backward(self, Y):
        delta = self.output() - Y

        for layer in range(self.last, 0, -1):
            b_delta = self.learning_rate * \
                self.activation_prime(self.z[layer]).dot(delta)

            self.biases[layer - 1] -= b_delta
            self.weights[layer - 1] -= b_delta.dot(self.a[layer - 1].T)

            delta = None

            if layer != 1:
                delta = self.weights[layer - 1].T.dot(b_delta)

    def output(self):
        return self.a[-1]
