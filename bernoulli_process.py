# -*- coding: utf-8 -*-

# Jay L. Devore.
# Probability and Statistics for Engineering and the Sciences, Ninth Edition.
# Cengage Learning, 2016.
# 3.4 The Binomial Probability Distribution.

import sys
import decimal
from decimal import Decimal

if sys.version_info[0:2] < (3, 6):
        sys.exit("Python >= 3.6 is required.")

class BernoulliProcessException(Exception):
        pass

class BernoulliProcess:

        __cache = [Decimal(1), Decimal(1)]

        def __error(self, message):
                raise BernoulliProcessException(message)

        def max_factorial_argument(self):
                return 100000

        def factorial(self, n):

                if not n >= 0:
                        self.__error("Error factorial argument {0}".format(n))

                if n < len(self.__cache):
                        return self.__cache[n]

                if n > self.max_factorial_argument():
                        self.__error("Factorial argument {0} is too large (max = {1})"
                                     .format(n, self.max_factorial_argument()))

                for i in range(len(self.__cache), n + 1):
                        self.__cache.append(Decimal(i) * self.__cache[i - 1])

                return self.__cache[n]

        def binomial(self, n, m):

                if not (m <= n and n >= 1 and m >= 0):
                        self.__error("Error binomial ({0}, {1})".format(n, m))

                return self.factorial(n) / (self.factorial(m) * self.factorial(n - m))

        # Вероятность того, что из n испытаний будет m успешных
        # испытаний при вероятности успеха испытания p
        def probability(self, n, m, p):

                if not (p > 0 and p < 1):
                        self.__error("Error probability {0}".format(p))

                return self.binomial(n, m) * (Decimal(p) ** (m)) * (Decimal(1 - p) ** (n - m))

        # Вероятность того, что из n испытаний будет от 0 до m
        # успешных испытаний при вероятности успеха испытания p
        def cdf(self, n, m, p):

                probability = Decimal(0)

                for i in range(0, m + 1):
                        probability += self.probability(n, i, p)

                return probability

        # Вероятность того, что из n испытаний будет максимум m
        # успешных испытаний при вероятности успеха испытания p
        def at_most(self, n, m, p):

                return self.cdf(n, m, p)

        # Вероятность того, что из n испытаний будет минимум m
        # успешных испытаний при вероятности успеха испытания p
        def at_least(self, n, m, p):

                # Это равно вероятности того, что будет максимум n - m
                # неуспешных испытаний с их вероятностью 1 - p
                return self.at_most(n, n - m, 1 - p)

        # Для функции find, у которой есть описание
        def __binary_search(self, m, p, success_probability):

                # Вначале надо найти интервал. В зависимости от заданных вероятностей,
                # могут быть лучше предположения об этом интервале, но это программа
                # предназначена для изучения Питона, а не для быстродействия.
                # Нужен первый интервал, на котором имеется требуемая вероятность
                # успеха success_probability.
                interval_length = m
                left = m
                right = left + interval_length
                while self.at_least(right, m, p) < success_probability:
                        left = right
                        right = left + interval_length

                # Интервал найден, теперь двоичный поиск на этом интервале.
                # На этом интервале любая из границ может иметь равенство,
                # в этом случае надо выбрать наименьшую с равенством.
                while right - left > 0:

                        mean = left + (right - left) // 2

                        if self.at_least(mean, m, p) >= success_probability:
                                right = mean
                        else:
                                if mean == left:
                                        break
                                left = mean

                return right

        # # Для функции find, у которой есть описание
        def __sequential_search(self, m, p, success_probability):
                i = m
                while True:
                        if self.at_least(i, m, p) >= success_probability:
                                break
                        else:
                                i += 1
                return i

        # При каком минимальном количестве испытаний будет с вероятностью
        # равной или превышающей success_probability как минимум m успешных
        # испытаний при вероятности успеха испытания p
        def find(self, m, p, success_probability):

                if not (success_probability > 0 and success_probability < 1):
                        self.__error("Success probability {0} is out of range (0, 1)".format(success_probability))
                if not isinstance(m, int):
                        self.__error("Trial count {0} is not integer".format(m))
                if not m > 0:
                        self.__error("Trial count {0} must be positive".format(m))

                # Имеется только одно решение, поэтому его можно найти двоичным поиском
                trial_count = self.__binary_search(m, p, success_probability)

                # Проверка результата последовательным поиском
                #trial_count_s = self.__sequential_search(m, p, success_probability)
                #if trial_count != trial_count_s:
                #        self.__error("Error binary search, found {0} instead of {1}"
                #                     .format(trial_count, trial_count_s))

                return trial_count

if __name__ == "__main__":

        decimal.setcontext(decimal.Context())
        decimal.getcontext().prec = 50
        decimal.getcontext().Emin = -999999
        decimal.getcontext().Emax = 999999

        try:

                bp = BernoulliProcess()

                test_count = bp.find(1000, p = 0.75, success_probability = 0.9)

                if not test_count == 1361:
                        sys.exit("Error BernoulliProcess: trial count = {0} instead of 1361"
                                 " (prec = {1}, Emin = {2}, Emax = {3})."
                                 .format(test_count, decimal.getcontext().prec,
                                         decimal.getcontext().Emin, decimal.getcontext().Emax))

                for success_count in range(1, 1001):
                        all_count = bp.find(success_count, p = 0.75, success_probability = 0.9)
                        print("{0}: {1}".format(success_count, all_count))

        except Exception as e:

                sys.exit("{0}".format(e))
