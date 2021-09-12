
import numpy as np
import pandas as pd

# Numpy code:

a = np.array([1,3,5,7])
# array([1, 3, 5, 7])
b = np.arange(4)
# array([0, 1, 2, 3])
np.arange(2,10,1)
# array([2, 3, 4, 5, 6, 7, 8, 9])
np.linspace(0,10,6)
# array([ 0.,  2.,  4.,  6.,  8., 10.])

c = np.array([[1,2,3],[4,5,6]])
# array([[1, 2, 3],
#       [4, 5, 6]])

d = np.zeros((2,3))
# array([[0., 0., 0.],
#       [0., 0., 0.]])

d = np.ones((2,3))
# array([[1., 1., 1.],
#       [1., 1., 1.]])

np.random.random((2,3))
# array([[0.16868203, 0.31090109, 0.7210469 ],
#       [0.0750029 , 0.08401428, 0.96992496]])


a+b
# array([ 1,  4,  7, 10])

c+d
# array([[2., 3., 4.],
#       [5., 6., 7.]])

c**2
# array([[ 1,  4,  9],
#       [16, 25, 36]])

c.shape
# (2, 3)

c.T
# array([[1, 4],
#       [2, 5],
#       [3, 6]])
c > 3
# array([[False, False, False],
#       [ True,  True,  True]])

a[2:]
# array([5, 7])
c[:1]
# array([[1, 2, 3]])
c[:1,1:]
# array([[2, 3]])
for x in c:
    print (x)
    for y in x:
        print(y)
# [4 5 6]
# 1
# 2
# 3
# [4 5 6]
# 4
# 5
# 6
for x in c.flat:
    print(x)
# 1
# 2
# 3
# 4
# 5
# 6
[x for x in c if x[1] < 3]
# [array([1, 2, 3])]


x = np.random.random((3,5))
x
# array([[0.43391468, 0.73430824, 0.92759808, 0.23966575, 0.16112573],
#       [0.85501039, 0.67383523, 0.45245038, 0.26001489, 0.86884395],
#       [0.17991555, 0.96628615, 0.22680872, 0.92979024, 0.52796391]])
print(x.sum())
print(x.min())
print(x.max())
print(x.mean())
# 8.437531894577779
# 0.1611257283125176
# 0.9662861490415007
# 0.5625021263051853

one_dim = np.array([1,2,3,4])


two_dim = np.array([[100, 200, 50, 400], [50, 0, 0, 100], [350, 100, 50, 200]])

print("len: " + str(len(two_dim)))      # len tu nie rozumiem
print("shape: " + str(two_dim.shape))  # rozmiar, kształt tablicy
print("ndim: " + str(two_dim.ndim))   #ilość wymiarów
print("size: " + str(two_dim.size))  #ilość elementów
print("bajt-size: " + str(two_dim.itemsize))


# numpy jaka jest roznica pomiedzy dot/matmul/mul, jakie sa przewagi , do czego sie uzywa, ja zmienic ksztalt
#( reshape/view ), jak utworzyc losowe tablice o rozmiarze jakims, jak same jedynki utworzyc (zeros/once),
# generacja randomowych liczb, np.where(...),

# 1. stwórz array na 2 sposoby w kilku wymiarach (3,4 tablice),
# stwórz jedną losową z użyciem where,
# użyj np.linspace(0,10,6),
# stwórz zerowa i jedynkową tablicę

# 2. pokaż ilość wymiarów i rozmiar tablicy

# 3.  policz ilość elemntów i ich sumę

# 4. pokaż indeksem elementy tablicy

# 5. zmień rozmiar tablicy

# 6. stwórz matrix, pokaż indeksy po matriksie

# 7 zmień wymiar i rozmiar tablicy (reshape, view)

# 8. numpy jaka jest roznica pomiedzy dot/matmul/mul - zastosuj