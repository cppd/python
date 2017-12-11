# -*- coding: utf-8 -*-

# Пересечение и две разности двух множеств за один проход

import random

set_a = sorted(set(random.sample(range(1, 20), 10)))
set_b = sorted(set(random.sample(range(1, 20), 10)))

difference_a = []
difference_b = []
intersection = []

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

print("a = {0}".format(set_a))
print("b = {0}".format(set_b))
print("")
print("a - b = {0}\n {1}".format(difference_a, difference_a == sorted(set(set_a) - set(set_b))))
print("")
print("b - a = {0}\n {1}".format(difference_b, difference_b == sorted(set(set_b) - set(set_a))))
print("")
print("a & b = {0}\n {1}".format(intersection, intersection == sorted(set(set_a) & set(set_b))))
