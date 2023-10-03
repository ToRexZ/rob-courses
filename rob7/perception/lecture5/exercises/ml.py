from sklearn.datasets import load_iris
from sklearn import neighbors, datasets
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt
import numpy as np

iris = load_iris()

# The shape of the data is (150, 4)
print(iris.data.shape)
# Where
n_samples, n_features = iris.data.shape


# Information about the class is stored in the target attribute of the dataset.
print(iris.target)

# Where the names of the taget class is stored in the target_names attribute of the class.
print(iris.target_names)

# Note that the data is 4 dimensional, but we can visualize 2 dimensions at a time using a scatter plot.
x_index = 0
y_index = 1

formatter = plt.FuncFormatter(lambda i, *args: iris.target_names[int(i)])
plt.figure(figsize=(5, 4))
plt.scatter(iris.data[:, x_index], iris.data[:, y_index], c=iris.target)
plt.colorbar(ticks=[0, 1, 2], format=formatter)
plt.xlabel(iris.feature_names[x_index])
plt.ylabel(iris.feature_names[y_index])
plt.tight_layout()
# Use this to show the plot if neccessary.
# plt.show()

knn = neighbors.KNeighborsClassifier(n_neighbors=1)

# Every algorithm is exposed in scikit-learn via an estimator object.

# Then the estimator parameters can be set when installed.
model = LinearRegression(n_jobs=1)
# model = LinearRegression(n_jobs=1, normalize=True) <--- Deprecated Sckit.learn v0.18

print(model)

# Lets try to fit on data:
x = np.array([0, 1, 2])
y = np.array([0, 1, 2])
X = x[
    :, np.newaxis
]  # The input data for sklearn is 2D: (samples == 3 x features == 1) (3x1) matrix
print(X)


# Fit the model to the data.
model.fit(X, y)
print(model.coef_)

# Supervised learning can be classified into two different categories: Classification and Regression.
# Classification has discrete labels
# Regression has continuous labels, i.e. it is not classifying directly into boxes, but rater on continuous axis. e.g. the age of an object, because the age is a continuous quantity.


# A classic in Classification is kNN (k- Nearest Neighbors)

iris = datasets.load_iris()

X, y = iris.data, iris.target

knn = neighbors.KNeighborsClassifier(n_neighbors=1)
knn.fit(X, y)

# What kind of iris has 3cm x 5cm sepal and 4cm x 2cm petal?
print(iris.target_names[knn.predict([[3, 5, 4, 2]])])

# Now lets do some Regression:
# x from 0 to 30
x = 30 * np.random.random((20, 1))
# y = a*x + b with noise
y = 0.5 * x + 1.0 + np.random.normal(size=x.shape)
# Create the linear regression model
model = LinearRegression()
model.fit(x, y)

# predict y from the data
x_new = np.linspace(0, 30, 100)
y_new = model.predict(x_new[:, np.newaxis])

print(x_new)
print(y_new)

# Regularization
# The idea of regularization is to prefer simpler models for a certain defintion of simpler, even if they lead to more errors on the trai set. E.g. fitting a lower order polynomial to data, which is then not overfitted.
