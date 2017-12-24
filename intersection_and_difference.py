# -*- coding: utf-8 -*-

# Пересечение и две разности двух множеств за один проход

import sys
import random
import unittest

if sys.version_info < (3, 6):
        sys.exit("Python >= 3.6 is required.")

def intersection_and_difference(data_a, data_b):

        set_a = sorted(set(data_a))
        set_b = sorted(set(data_b))

        intersection = []
        difference_a = []
        difference_b = []

        a = 0
        b = 0

        while True:
                if a == len(set_a):
                        difference_b.extend(set_b[b:])
                        break
                elif b == len(set_b):
                        difference_a.extend(set_a[a:])
                        break
                elif set_a[a] < set_b[b]:
                        difference_a.append(set_a[a])
                        a += 1
                elif set_b[b] < set_a[a]:
                        difference_b.append(set_b[b])
                        b += 1
                else:
                        intersection.append(set_a[a])
                        a += 1
                        b += 1

        return intersection, difference_a, difference_b

class IntersectionAndDifferenceTestCase(unittest.TestCase):

        @staticmethod
        def __error_string(text, data_a, data_b, result, set_result):
                return "{0} failed.\n"\
                       "a: {1}\n"\
                       "b: {2}\n"\
                       "{0} computed: {3}\n"\
                       "{0} set: {4}"\
                       .format(text, data_a, data_b, result, set_result)

        def __test_abc(self, data_a, data_b):

                intersection, difference_a, difference_b = intersection_and_difference(data_a, data_b)

                self.assertTrue(len(intersection) == len(set(intersection)), "intersection elements are not unique")
                self.assertTrue(len(difference_a) == len(set(difference_a)), "difference_a elements are not unique")
                self.assertTrue(len(difference_b) == len(set(difference_b)), "difference_b elements are not unique")

                set_intersection = set(data_a) & set(data_b)
                self.assertSetEqual(set(intersection), set_intersection,
                                    self.__error_string("a & b", data_a, data_b, intersection, set_intersection))

                set_difference_a = set(data_a) - set(data_b)
                self.assertSetEqual(set(difference_a), set_difference_a,
                                    self.__error_string("a - b", data_a, data_b, difference_a, set_difference_a))

                set_difference_b = set(data_b) - set(data_a)
                self.assertSetEqual(set(difference_b), set_difference_b,
                                    self.__error_string("b - a", data_a, data_b, difference_b, set_difference_b))

        def __test_ab(self, data_a, data_b):

                self.__test_abc(data_a, data_b)
                self.__test_abc(data_a * 2, data_b)
                self.__test_abc(data_a, data_b * 2)
                self.__test_abc(data_a * 2, data_b * 2)

        def __test(self, data_a, data_b):

                self.__test_ab(data_a, data_b)
                self.__test_ab(data_b, data_a)

                self.__test_ab(data_a, data_a)
                self.__test_ab(data_b, data_b)

                self.__test_ab(data_a, [])
                self.__test_ab(data_b, [])

                self.__test_ab([], data_a)
                self.__test_ab([], data_b)

        def test_intersection_and_difference(self):

                self.__test([], [])

                data_a = random.sample(range(1, 20), 10)
                data_b = random.sample(range(1, 20), 10)

                self.__test(data_a, data_b)

                for i in range(0, 8):
                        list_a = [1, 3, 4, 6]
                        list_b = [i]
                        self.__test(list_a, list_b)
                        self.__test(tuple(list_a), tuple(list_b))

                for i in range(0, 8):
                        for j in range(1, 8 - i):
                                list_a = [1, 3, 4, 6]
                                list_b = [i, i + j]
                                self.__test(list_a, list_b)
                                self.__test(tuple(list_a), tuple(list_b))

if __name__ == "__main__":

        unittest.main()
