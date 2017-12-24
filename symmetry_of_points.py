# -*- coding: utf-8 -*-

#
# Симметричность точек с целочисленными координатами на плоскости относительно Y.
#
# Точки симметричны, если выполняется 2 условия:
#  1. Уникальные координаты X, симметричные по своим номерам по возрастанию X,
#    также симметричны по своим координатам X.
#  2. Равны множества значений Y, соответствующие симметричным X. В зависимости
#    от потребности, они равны по std::sort или по std::sort с std::unique.
#
# Пусть X(n) — уникальный и отсортированный по возрастанию список координат X.
# Пусть Y(n) — множество координат Y для X(n).
# Пусть l и r — номера симметричных элементов из X, то есть первый и последний
# элемент, второй и предпоследний и т.д.
# Пусть min и max — минимальная и максимальная координата по X.
# Тогда для симметрии требуется для всех l <= r выполнение 2 условий:
#  1.
#    (min + max) / 2 - X(l) == X(r) - (min + max) / 2   (1.1)
#    (min + max) / 2 + (min + max) / 2 == X(r) + X(l)   (1.2)
#    min + max == X(r) + X(l)                           (1.3)
#    X(l) - min == max - X(r)                           (1.4)
#
#    Уравнение 1.1 — целочисленное деление на 2, также возможно целочисленное переполнение.
#    Уравнение 1.2 — целочисленное деление на 2, также возможно целочисленное переполнение.
#    Уравнение 1.3 — возможно целочисленное переполнение.
#    Уравнение 1.4 — всё в порядке с целыми числами, если они неотрицательные.
#  2.
#    Y(l) == Y(r) с равенством как описано выше.
#

import sys
import operator
import matplotlib.pyplot as plt

if sys.version_info < (3, 6):
        sys.exit("Python >= 3.6 is required.")

def annotate(x, y, count):
        plt.annotate("{0} points".format(count), xy = (x, y), xytext = (15, 15),
                     textcoords = 'offset points', ha = 'left', va = 'center',
                     bbox = dict(boxstyle = 'round', alpha = 0.2),
                     arrowprops = dict(arrowstyle = '->'))

# points — это как бы std::vector<std::array<int, 2>>
def show_points(points, window_title, title):

        if len(points) == 0:
                raise Exception('No points to show')

        count_xy = dict()

        min_x = max_x = points[0][0]
        min_y = max_y = points[0][1]

        for x, y in points:
                min_x = min(x, min_x)
                max_x = max(x, max_x)
                min_y = min(y, min_y)
                max_y = max(y, max_y)

                if (x, y) in count_xy:
                        count_xy[(x, y)] += 1
                else:
                        count_xy[(x, y)] = 1

        mean_x = min_x + 0.5 * (max_x - min_x)

        increase_y = 0.1 * (max_y - min_y)
        if increase_y == 0:
                increase_y = 0.1 * (max_x - min_x)
                # Если тут increase_y == 0, то тогда пусть будет 0

        for key, count in count_xy.items():
                if count > 1:
                        annotate(key[0], key[1], count)

        plt.gcf().canvas.set_window_title(window_title)
        plt.title(title)
        plt.scatter(*zip(*points))
        plt.plot([mean_x, mean_x], [min_y - increase_y, max_y + increase_y])
        plt.show()

# Простой вариант без оптимизаций.
# points — это как бы std::vector<std::array<int, 2>>
def symmetrical(points, use_unique_points):

        data = dict()
        for x, y in points:
                if x in data:
                        data[x].append(y)
                else:
                        data[x] = [y]
        data = sorted(data.items(), key = operator.itemgetter(0))

        assert len(data) > 0
        assert all(isinstance(x, int) for x, y in data)
        assert all(data[i][0] < data[i + 1][0] for i in range(len(data) - 1))

        min_x = data[0][0]
        max_x = data[-1][0]

        l = 0
        r = len(data) - 1

        while l <= r:

                if (data[l][0] - min_x) != (max_x - data[r][0]):
                        return False

                if use_unique_points:
                        if set(data[l][1]) != set(data[r][1]):
                                return False
                else:
                        if sorted(data[l][1]) != sorted(data[r][1]):
                                return False
                l += 1
                r -= 1

        return True

# points — это как бы std::vector<std::array<int, 2>>
def symmetrical_points(points, use_unique_points):

        if len(points) == 0:
                print("No points")
                return

        points_are_symmetrical = symmetrical(points, use_unique_points)

        title = ("Symmetrical {0}" if points_are_symmetrical else "Asymmetrical {0}")\
                        .format("for unique points" if use_unique_points else "for all points")

        show_points(points, "Points", title)

if __name__ == "__main__":

        symmetrical_points([(1, 2), (2, 5), (3, 5), (3, 5), (4, 2)], use_unique_points = True)
