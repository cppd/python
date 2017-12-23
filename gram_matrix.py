# -*- coding: utf-8 -*-

# Определение линейной зависимости векторов с помощью матрицы Грама.
# Целочисленные координаты векторов.
# Сравнение непосредственных вычислений и NumPy.

# Titu Andreescu.
# Essential Linear Algebra with Applications. A Problem-Solving Approach.
# Birkhäuser, 2014.
# 10.3 Bilinear Forms and Matrices.

import sys
import unittest
import numpy as np

if sys.version_info < (3, 6):
        sys.exit("Python >= 3.6 is required.")

INTEGER_TYPE = np.int64
INTEGER_MIN = np.iinfo(INTEGER_TYPE).min
INTEGER_MAX = np.iinfo(INTEGER_TYPE).max

def dot(vector_a, vector_b):

        assert isinstance(vector_a, np.ndarray)
        assert isinstance(vector_b, np.ndarray)
        assert np.ndim(vector_a) == 1
        assert np.ndim(vector_b) == 1
        assert vector_a.shape[0] == vector_b.shape[0]
        assert vector_a.dtype == INTEGER_TYPE
        assert vector_b.dtype == INTEGER_TYPE

        dot_product = 0

        for i in range(0, vector_a.shape[0]):
                dot_product += int(vector_a[i]) * int(vector_b[i])

        return dot_product

def gram_matrix(vectors):

        assert isinstance(vectors, np.ndarray)
        assert np.ndim(vectors) == 2
        assert vectors.dtype == INTEGER_TYPE

        vector_count = vectors.shape[0]

        matrix = np.empty([vector_count, vector_count], dtype = INTEGER_TYPE)

        for row in range(0, vector_count):
                for col in range(0, vector_count):
                        dot_product = dot(vectors[row], vectors[col])
                        assert INTEGER_MIN <= dot_product <= INTEGER_MAX
                        matrix[row][col] = dot_product

        return matrix

def determinant(matrix):

        assert isinstance(matrix, np.ndarray)
        assert np.ndim(matrix) == 2
        assert matrix.shape[0] == matrix.shape[1]
        assert matrix.dtype == INTEGER_TYPE

        size = matrix.shape[0]

        if size == 1:
                entry = matrix[0][0]
                return int(entry)

        # удалить строку 0
        matrix_2 = np.delete(matrix, 0, 0)

        det = 0

        for i in range(0, size):

                entry = matrix[0][i]

                # удалить столбец i
                submatrix = np.delete(matrix_2, i, 1)

                minor = determinant(submatrix)

                cofactor = ((-1) ** i) * minor

                det += int(entry) * cofactor

        return det

def list_of_lists_to_matrix(list_of_lists):

        assert isinstance(list_of_lists, list)
        for i in range(0, len(list_of_lists)):
                assert isinstance(list_of_lists[i], list)
                if i > 0:
                        assert len(list_of_lists[i]) == len(list_of_lists[i - 1])
                assert len(list_of_lists) <= len(list_of_lists[i])
                for j in range(0, len(list_of_lists[i])):
                        assert isinstance(list_of_lists[i][j], int)
                        assert INTEGER_MIN <= list_of_lists[i][j] <= INTEGER_MAX

        return np.array(list_of_lists, dtype = INTEGER_TYPE)


def print_computation_result(gram, det_gram):
        print("Gram matrix:\n{0}".format(gram))
        print("Determinant:\n{0}".format(det_gram))
        print("Linearly independent" if det_gram != 0 else "Linearly dependent")

def integer_computation(matrix):
        gram = gram_matrix(matrix)
        det_gram = determinant(gram)
        return (gram, det_gram)

def numpy_computation(matrix):
        gram = np.matmul(matrix, np.transpose(matrix))
        det_gram = np.linalg.det(gram)
        return (gram, det_gram)

def compute_and_print(list_of_lists):

        matrix = list_of_lists_to_matrix(list_of_lists)

        print("---Integer---")
        print_computation_result(*integer_computation(matrix))

        print()

        print("---NumPy---")
        print_computation_result(*numpy_computation(matrix))

class GramMatrixTestCase(unittest.TestCase):

        def test_integer_independent(self):
                v0 = [1, 1, 1]
                v1 = [1, 1, 2]
                det = integer_computation(list_of_lists_to_matrix([v0, v1]))[1]
                self.assertNotEqual(det, 0, "Integer computation failed: "
                                            "vectors {0} and {1} are linearly independent".format(v0, v1))
        def test_integer_dependent(self):
                v0 = [1, 1, 1]
                v1 = [2, 2, 2]
                det = integer_computation(list_of_lists_to_matrix([v0, v1]))[1]
                self.assertEqual(det, 0, "Integer computation failed: "
                                         "vectors {0} and {1} are linearly dependent".format(v0, v1))
        def test_numpy_independent(self):
                v0 = [1, 1, 1]
                v1 = [1, 1, 2]
                det = numpy_computation(list_of_lists_to_matrix([v0, v1]))[1]
                self.assertNotEqual(det, 0, "NumPy computation failed: "
                                            "vectors {0} and {1} are linearly independent".format(v0, v1))
        def test_numpy_dependent(self):
                v0 = [1, 1, 1]
                v1 = [2, 2, 2]
                det = numpy_computation(list_of_lists_to_matrix([v0, v1]))[1]
                self.assertEqual(det, 0, "NumPy computation failed: "
                                         "vectors {0} and {1} are linearly dependent".format(v0, v1))

def test():

        vectors = []

        # Большие числа для проверки NumPy
        vectors.append([1, 1, 1, 1_000_000, 1_000_000, 1_000_000_000])
        vectors.append([2, 1, 1, 1_000_000, 1_000_000, 1_000_000_000])
        vectors.append([1, 2, 1, 1_000_000, 1_000_000, 1_000_000_000])
        vectors.append([1, 1, 2, 1_000_000, 1_000_000, 1_000_000_000])
        vectors.append([1, 1, 1, 2_000_000, 1_000_000, 1_000_000_000])

        compute_and_print(vectors)

if __name__ == "__main__":

        unittest.main()

        test()
