#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Прочитать треугольники из файла OBJ.
# Рассчитать точки-семплы этих треугольников.
# Записать точки в текстовый файл по одной на строку.

import sys
import os
import math
import statistics
import numpy as np
import matplotlib.pyplot as plt

if sys.version_info[0:2] < (3, 6):
        sys.exit("Python >= 3.6 is required.")

class ObjSamplesException(Exception):
        pass

def error(message):
        raise ObjSamplesException(message)

def draw_line(point_from, point_to):
        plt.plot([point_from[0], point_to[0]], [point_from[1], point_to[1]],
                 color = 'gray', linestyle = 'solid', linewidth = 0.5)

def draw_points(points):
        plt.scatter(*zip(*points), color = 'green', s = 1)

def show_triangle_samples(window_title, title, vertices, samples):

        if len(samples) == 0:
                error('No samples to show')

        assert len(vertices) == 3

        v0, v1, v2 = vertices

        draw_line(v0, v1)
        draw_line(v1, v2)
        draw_line(v2, v0)

        draw_points(samples)

        plt.axes().set_aspect('equal')
        plt.gcf().canvas.set_window_title(window_title)
        plt.title(title)
        plt.show()

def random_barycentric(uniform_random):

        # Matt Pharr, Wenzel Jakob, Greg Humphreys.
        # Physically Based Rendering. From theory to implementation. Third edition.
        # Elsevier, 2017.
        # 13.6.5 Sampling a triangle

        assert len(uniform_random) == 2

        sqrt_0 = math.sqrt(uniform_random[0])

        u = 1 - sqrt_0
        v = uniform_random[1] * sqrt_0

        return (u, v)

def triangle_sample(v0, v1, v2):

        u, v = random_barycentric(np.random.rand(2))

        return v0 * u + v1 * v + v2 * (1 - u - v)

def parse_float(text):

        try:
                r = float(text)
        except Exception as e:
                error("{0}".format(e))

        if not isinstance(r, (int, float)):
                error("Not float \"{0}\"".format(text))

        return float(r)

def parse_integer(text):

        try:
                r = int(text)
        except Exception as e:
                error("{0}".format(e))

        if not isinstance(r, int):
                error("Not integer \"{0}\"".format(text))

        return r

class Triangle:

        def __init__(self, indices):

                assert len(indices) == 3

                self.__indices = []
                self.__indices.extend(indices)

        def sample(self, vertices):

                return triangle_sample(*vertices[self.__indices])

        def area(self, vertices):

                v0, v1, v2 = vertices[self.__indices]

                e1 = v1 - v0
                e2 = v2 - v0

                cross = np.cross(e1, e2)

                #return 0.5 * np.linalg.norm(cross)
                return 0.5 * np.sqrt(max(0, cross.dot(cross)))

class ObjFile:

        @staticmethod
        def __SAMPLE_FORMAT_STRING():
                return "{:9.6f} {:9.6f} {:9.6f}"

        # Строка int/int/int.
        # Нужно получить первое значение.
        @staticmethod
        def __parse_vertex_number(text):

                v = text.split("/")

                if len(v) < 1:
                        error("Error face element \"{0}\"".format(text))

                v = v[0].strip()

                if len(v) < 1:
                        error("Error face element \"{0}\"".format(text))

                return parse_integer(v)

        # Три числа float float float.
        @staticmethod
        def __parse_vertex(line):

                line = line.strip()

                if len(line) < 1:
                        error("Empty vertex string")

                data = line.split()

                if len(data) != 3:
                        error("Error vertex line \"{0}\"".format(line))

                return [parse_float(data[i]) for i in range(0, 3)]

        # Группы из 3 чисел int/int/int int/int/int int/int/int
        # с возможным отсутствием чисел. Здесь требуется первое
        # число в каждой группе как индекс вершины.
        @staticmethod
        def __parse_face(line):

                line = line.strip()

                if len(line) < 1:
                        error("Empty face string")

                data = line.split()

                if len(data) < 3:
                        error("Error face line \"{0}\"".format(line))

                if len(data) > 3:
                        error("Faces with {0} vertices are not supported \"{1}\"".format(len(data), line))

                return [ObjFile.__parse_vertex_number(data[i]) for i in range(0, 3)]

        @staticmethod
        def __correct_face_indices(indices, vertex_count):

                assert len(indices) == 3

                for i in range(0, 3):

                        index = indices[i]

                        # Индекс может быть отрицательным, поэтому abs
                        if not 1 <= abs(index) <= vertex_count:
                                error("Triangle index abs({0}) is out of range [{1}, {2}]"\
                                      .format(index, 1, vertex_count))

                        # Надо с началом от 0
                        if index > 0:
                                index -= 1

                        # Если индекс от конца списка, то преобразовать с началом от 0
                        if index < 0:
                                index = vertex_count + index

                        indices[i] = index

                return indices

        # Сместить к началу координат в интервал от 0 до 1
        def __scale_vertices(self):

                vertex_min = np.amin(self.__vertices, axis = 0)
                vertex_max = np.amax(self.__vertices, axis = 0)

                length = vertex_max - vertex_min
                center = vertex_min + 0.5 * length

                length_max = max(length)

                if length_max == 0:
                        error("No dimensions")

                scale = 2 / length_max

                for i in range(0, len(self.__vertices)):
                        self.__vertices[i] = (self.__vertices[i] - center) * scale

        def __compute_area_and_delete_zero_area_triangles(self):

                self.__area = []
                self.__area_all = 0

                i = 0
                while i < len(self.__triangles):
                        area = self.__triangles[i].area(self.__vertices)
                        if area != 0:
                                self.__area.append(area)
                                self.__area_all += area
                                i += 1
                        else:
                                self.__triangles.pop(i)

                assert len(self.__triangles) == len(self.__area)

        def __triangle_sample(self, index):

                sample = self.__triangles[index].sample(self.__vertices)

                return self.__SAMPLE_FORMAT_STRING().format(*sample)

        def __init__(self, file_name):

                self.__file_name = file_name
                self.__triangles = []
                self.__vertices = []

                for line in open(file_name):

                        line = line.strip()

                        if line == "":
                                continue

                        if line[0] == "#":
                                continue

                        first = line.split()[0]

                        if first == "v":

                                second = line[len(first):]

                                self.__vertices.append(self.__parse_vertex(second))

                        elif first == "f":

                                second = line[len(first):]

                                indices = self.__parse_face(second)

                                indices = self.__correct_face_indices(indices, len(self.__vertices))

                                self.__triangles.append(Triangle(indices))

                if len(self.__triangles) == 0:
                        error("No triangles loaded from OBJ file")

                self.__vertices = np.array(self.__vertices)

                self.__scale_vertices()
                self.__compute_area_and_delete_zero_area_triangles()

                if len(self.__triangles) == 0:
                        error("No 2D triangles")

        def print_statictics(self):

                triangle_count = len(self.__triangles)
                area_min = min(self.__area)
                area_max = max(self.__area)
                area_average = self.__area_all / triangle_count
                area_median = statistics.median(self.__area)

                print("File \"{0}\"\n".format(self.__file_name))
                print("triangle count = {0}".format(triangle_count))
                print("area all = {0}".format(self.__area_all))
                print("area min = {0}".format(area_min))
                print("area max = {0}".format(area_max))
                print("area ratio = {0}".format(area_max / area_min))
                print("area average = {0}".format(area_average))
                print("area median = {0}".format(area_median))

        def write_samples_to_file(self, file_name, sample_count):

                assert len(self.__triangles) == len(self.__area)

                sample_density = sample_count / self.__area_all

                all_sample_count = 0

                print("\nFile \"{0}\", sample count {1}\n".format(file_name, sample_count))

                with open(file_name, "w") as f:

                        for i in range(0, len(self.__triangles)):

                                count = math.ceil(sample_density * self.__area[i])

                                for _ in range(0, count):
                                        print(self.__triangle_sample(i), file = f)

                                all_sample_count += count

                                if (i + 1) % 100 == 0:
                                        print("{0} samples for {1} ({2}) triangles"\
                                              .format(all_sample_count, i + 1, len(self.__triangles)))

                print("\nsample count {0} ({1})".format(all_sample_count, sample_count))

def test_triangle_samples(point_count):

        # 3 вершины по 2 координаты в каждой
        vertices = np.random.rand(3, 2)

        points = [triangle_sample(*vertices) for i in range(0, point_count)]

        show_triangle_samples("Test Triangle Samples", "Samples", vertices, points)

def check_file_names(obj_file, sample_file):

        if not os.path.exists(obj_file):
                error("File \"{0}\" doesn't exist".format(obj_file))
        if not os.path.isfile(obj_file):
                error("\"{0}\" is not a file".format(obj_file))

        if os.path.exists(sample_file):
                if not os.path.isfile(sample_file):
                        error("\"{0}\" is not a file".format(sample_file))
                if os.path.samefile(obj_file, sample_file):
                        error("obj_file sample_file are the same")

def get_sample_count(sample_count):

        try:
                sample_count = int(sample_count)
        except Exception:
                error("Error sample count \"{0}\" conversion to integer".format(sample_count))

        if sample_count <= 0:
                error("Sample count must be positive")

        return sample_count

def sample_obj_file(obj_file, sample_file, sample_count):

        check_file_names(obj_file, sample_file)

        sample_count = get_sample_count(sample_count)

        file = ObjFile(obj_file)

        file.print_statictics()

        file.write_samples_to_file(sample_file, sample_count)

if __name__ == "__main__":

        try:
                if len(sys.argv) != 4:
                        error("Usage: obj_file sample_file sample_count")

                sample_obj_file(*sys.argv[1:])

                # test_triangle_samples(1000)

        except Exception as e:

                sys.exit("{0}".format(e))
