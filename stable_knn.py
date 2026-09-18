"""A small KNN subclass with an explicit rule for equal-distance neighbours."""
import numpy as np
from sklearn.neighbors import KNeighborsRegressor

class StableKNNRegressor(KNeighborsRegressor):
    def predict(self, X):
        # Several listings have identical inputs. Break ties by training-row order
        # so Python and the browser always choose the same three neighbours.
        predictions = []
        for row in np.asarray(X):
            squared_distances = np.sum((self._fit_X - row) ** 2, axis=1)
            rounded_distances = np.round(squared_distances, 12)
            nearest = np.argsort(rounded_distances, kind='stable')[:self.n_neighbors]
            predictions.append(np.mean(self._y[nearest]))
        return np.array(predictions)
