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
import math
import matplotlib.pyplot as plt

STRATIFIED_JITTERED_SAMPLER = "Stratified Jittered Sampler"
LATIN_HYPERCUBE_SAMPLER = "Latin Hypercube Sampler"
PASS_COUNT_STRING = "Pass count:"

if sys.version_info < (3, 6):
        sys.exit("Python >= 3.6 is required.")

def error(message):
        sys.exit(message)

def draw_line(point_from, point_to):
        plt.plot([point_from[0], point_to[0]], [point_from[1], point_to[1]],
                 color = 'gray', linestyle = 'solid', linewidth = 0.5)

def draw_points(points):
        plt.scatter(*zip(*points), color = 'green', s = 4)

# points — это как бы std::vector<std::array<int, 2>>
def show_points(title, grid_size, points, window_title):

        if len(points) == 0:
                error('No points to show')

        for x in range(0, grid_size + 1):
                draw_line((x / grid_size, 0), (x / grid_size, 1))

        for y in range(0, grid_size + 1):
                draw_line((0, y / grid_size), (1, y / grid_size))

        draw_points(points)

        plt.axes().set_aspect('equal')
        plt.gcf().canvas.set_window_title(window_title)
        plt.title(title)
        plt.show()

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
        if len(point) != 2:
                error("Not 2D point input:\n{0}".format(text))
        if not isinstance(point[0], (int, float)):
                error("Not 2D point input:\n{0}".format(text))
        if not isinstance(point[1], (int, float)):
                error("Not 2D point input:\n{0}".format(text))
        if not (point[0] >= 0 and point[0] <= 1 and point[1] >= 0 and point[1] <= 1):
                error("Point coordinates out of [0, 1]:\n{0}".format(text))

        return point

# Количество делений квадрата по одному измерению в зависимости от типа семплера
def compute_grid_size(sampler_type, point_count, pass_count):

        samples_group_size = point_count / pass_count

        if not samples_group_size.is_integer():
                error("Sample group size is not integer:\n{0}".format(samples_group_size))

        if sampler_type == STRATIFIED_JITTERED_SAMPLER:
                one_dimension_size = math.sqrt(samples_group_size)
                if not one_dimension_size.is_integer():
                        error("Stratified Jittered Sampler point count must be a square:\n{0}"\
                              .format(samples_group_size))
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
        points = []

        line_num = 0

        for line in open(file_name):

                line = line.strip()

                if line == "":
                        continue

                if line_num == 0:
                        sampler_type = parse_sampler_type(line, samplers)
                elif line_num == 1:
                        pass_count = parse_pass_count(line, PASS_COUNT_STRING)
                else:
                        points.append(parse_sampler_point(line))

                line_num += 1

        if sampler_type == "":
                error("No sampler type")
        if len(points) < 1:
                error("No points")

        grid_size = compute_grid_size(sampler_type, len(points), pass_count)

        return (sampler_type, grid_size, points)

if __name__ == "__main__":

        try:
                if len(sys.argv) != 2:
                        error("No file name in the command line")

                show_points(*read_file(sys.argv[1]), "Sampler points")

        except Exception as e:

                sys.exit("{0}".format(e))
