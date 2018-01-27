# -*- coding: utf-8 -*-

# Отображение точек семплеров графической программы.
# Формат данных:
#  Stratified Jittered Sampler | Latin Hypercube Sampler
#  Pass count: number
#  (x, y)
#  (x, y)
#  ...
#  (x, y)

import sys
import ast
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

STRATIFIED_JITTERED_SAMPLER = "Stratified Jittered Sampler"
LATIN_HYPERCUBE_SAMPLER = "Latin Hypercube Sampler"
PASS_COUNT_STRING = "Pass count:"

if sys.version_info < (3, 6):
        sys.exit("Python >= 3.6 is required.")

def error(message):
        sys.exit(message)

def draw_line(point_from, point_to):
        assert len(point_from) == 2 and len(point_to) == 2

        plt.plot([point_from[0], point_to[0]], [point_from[1], point_to[1]],
                 color = 'gray', linestyle = 'solid', linewidth = 0.5)

def show_points_2d(title, grid_size, points, window_title):

        assert len(points) > 0 and len(points[0]) == 2

        for x in range(0, grid_size + 1):
                draw_line((x / grid_size, 0), (x / grid_size, 1))

        for y in range(0, grid_size + 1):
                draw_line((0, y / grid_size), (1, y / grid_size))

        plt.scatter(*zip(*points), color = 'green', s = 4)

        plt.axes().set_aspect('equal')
        plt.gcf().canvas.set_window_title(window_title)
        plt.title(title)
        plt.show()

def show_points_3d(title, points, window_title):

        assert len(points) > 0 and len(points[0]) == 3

        #fig = plt.figure()
        #ax = fig.add_subplot(111, projection='3d')
        ax = Axes3D(plt.figure())

        ax.scatter(*zip(*points), c = 'green', marker = '.')

        plt.gcf().canvas.set_window_title(window_title)
        plt.title(title)
        plt.show()

def show_points(title, grid_size, points, window_title):

        if len(points) == 0:
                error('No points to show')

        if len(points[0]) == 2:
                show_points_2d(title, grid_size, points, window_title)
        elif len(points[0]) == 3:
                show_points_3d(title, points, window_title)
        else:
                error('Point dimension {0} is not supported'.format(len(points[0])))

# Поиск типа семплера в строке "*Sampler name"
def parse_sampler_type(text, samplers):

        sampler_type = ""

        for sampler in samplers:
                if text.find(sampler) >= 0:
                        sampler_type = sampler
                        break

        if sampler_type == "":
                error("Unknown sampler type:\n{0}".format(text))

        return sampler_type

# Преобразование строки "*Pass count: number" в число number
def parse_pass_count(text, keyword):

        word_begin = text.find(keyword)
        if word_begin < 0:
                error("\"" + keyword + "\" not found")

        text = text[word_begin + len(keyword):].strip()

        try:
                pass_count = ast.literal_eval(text)
        except ValueError:
                error("Malformed \"{0}\" input:\n{1}".format(keyword, text))

        if not isinstance(pass_count, int):
                error("Not \"{0}\" input:\n{1}".format(keyword, text))

        return pass_count

# Преобразование строки "*(x, y)*" в tuple(x, y)
def parse_sampler_point(text):

        # Убрать всё из строки до первой открывающей скобки
        # и после соответствующей ей закрывающей скобки
        point_begin = text.find("(")
        if point_begin < 0:
                error("Malformed input:\n{0}".format(text))
        point_end = text.find(")", point_begin)
        if point_end < 0:
                error("Malformed input:\n{0}".format(text))
        text = text[point_begin : point_end + 1]

        try:
                point = ast.literal_eval(text)
        except ValueError:
                error("Malformed input:\n{0}".format(text))

        if not isinstance(point, tuple):
                error("Not tuple input:\n{0}".format(text))

        for i in range(0, len(point)):
                if not isinstance(point[i], (int, float)):
                        error("Not point input:\n{0}".format(text))
                if not (point[i] >= 0 and point[i] <= 1):
                        error("Point coordinates out of [0, 1]:\n{0}".format(text))

        return point

# Количество делений квадрата по одному измерению в зависимости от типа семплера
def compute_grid_size(sampler_type, point_count, pass_count, dimension):

        samples_group_size = point_count / pass_count

        if not samples_group_size.is_integer():
                error("Sample group size is not integer:\n{0}".format(samples_group_size))

        samples_group_size = int(samples_group_size)

        if sampler_type == STRATIFIED_JITTERED_SAMPLER:

                one_dimension_size = round(pow(samples_group_size, 1 / dimension))

                if pow(one_dimension_size, dimension) != samples_group_size:
                        error("Stratified Jittered Sampler point count ({0}) must be the {1} power of an integer"\
                              .format(samples_group_size, dimension))

                grid_size = one_dimension_size

        elif sampler_type == LATIN_HYPERCUBE_SAMPLER:

                grid_size = samples_group_size

        else:
                error("Error sampler type \"{0}\"".format(sampler_type))

        return int(grid_size)

# Возвращаемое значение
# (название семплера, количество делений квадрата по одному измерению, координаты точек)
def read_file(file_name):

        samplers = [STRATIFIED_JITTERED_SAMPLER, LATIN_HYPERCUBE_SAMPLER]

        sampler_type = ""
        pass_count = -1
        grid_size = -1
        point_list = []

        line_num = 0

        dimension = -1

        for line in open(file_name):

                line = line.strip()

                if line == "":
                        continue

                if line_num == 0:
                        sampler_type = parse_sampler_type(line, samplers)
                elif line_num == 1:
                        pass_count = parse_pass_count(line, PASS_COUNT_STRING)
                else:
                        point = parse_sampler_point(line)

                        if dimension > 0:
                                if len(point) != dimension:
                                        error("Inconsistent point dimensions {0} and {1}".format(dimension, len(point)))
                        else:
                                dimension = len(point)

                        point_list.append(point)

                line_num += 1

        if sampler_type == "":
                error("No sampler type")
        if len(point_list) < 1:
                error("No points")
        if dimension < 1:
                error("No dimension")

        grid_size = compute_grid_size(sampler_type, len(point_list), pass_count, dimension)

        return (sampler_type, grid_size, point_list)

if __name__ == "__main__":

        try:
                if len(sys.argv) != 2:
                        error("No file name in the command line")

                show_points(*read_file(sys.argv[1]), "Sampler points")

        except Exception as e:

                sys.exit("{0}".format(e))
