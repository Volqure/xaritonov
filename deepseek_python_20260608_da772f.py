# -*- coding: utf-8 -*-
"""
Индивидуальное домашнее задание №2.1 «Дискретные случайные величины»
Вариант 1
"""

print("=" * 70)
print("ИНДИВИДУАЛЬНОЕ ДОМАШНЕЕ ЗАДАНИЕ №2.1")
print("Дискретные случайные величины")
print("Вариант 1")
print("=" * 70)

# ----------------------------------------------------------------------
# ЗАДАЧА 1
# ----------------------------------------------------------------------
print("\n" + "=" * 70)
print("ЗАДАЧА 1")
print("=" * 70)
print("""Условие задачи:
Две независимые случайные величины X и Y заданы таблицами распределения:

    X   | 2,5 | 6   | 8,3
    P   | 0,3 | 0,5 | 0,2

    Y   | 5,2 | 7,6
    P   | 0,6 | 0,4

Составить ряд распределения случайной величины X·Y и проверить
справедливость свойства о математическом ожидании произведения
независимых случайных величин:  M[X·Y] = M[X]·M[Y]
""")

# Данные
X_vals = [2.5, 6.0, 8.3]
X_probs = [0.3, 0.5, 0.2]

Y_vals = [5.2, 7.6]
Y_probs = [0.6, 0.4]

print("\nИсходные данные:")
print("X:", list(zip(X_vals, X_probs)))
print("Y:", list(zip(Y_vals, Y_probs)))

# ----------------------------------------------------------------------
# 1) Вычисляем M[X] и M[Y] по формуле: M[X] = Σ x_i * p_i
# ----------------------------------------------------------------------
print("\n" + "-" * 50)
print("ШАГ 1: Вычисление математических ожиданий M[X] и M[Y]")
print("Формула: M[X] = Σ (x_i · p_i)")
print("-" * 50)

M_X = sum(x * p for x, p in zip(X_vals, X_probs))
print("\nM[X] =", " + ".join(f"{x}·{p}" for x, p in zip(X_vals, X_probs)), "=", M_X)

M_Y = sum(y * p for y, p in zip(Y_vals, Y_probs))
print("M[Y] =", " + ".join(f"{y}·{p}" for y, p in zip(Y_vals, Y_probs)), "=", M_Y)

# ----------------------------------------------------------------------
# 2) Ряд распределения Z = X·Y
#    Так как X и Y независимы, то P(Z = x_i·y_j) = P(X=x_i)·P(Y=y_j)
# ----------------------------------------------------------------------
print("\n" + "-" * 50)
print("ШАГ 2: Составление ряда распределения Z = X·Y")
print("Свойство независимости: P(X=x_i, Y=y_j) = P(X=x_i)·P(Y=y_j)")
print("-" * 50)

Z_vals = []
Z_probs = []

print("\nВсе возможные произведения и их вероятности:")
for i, (x, px) in enumerate(zip(X_vals, X_probs)):
    for j, (y, py) in enumerate(zip(Y_vals, Y_probs)):
        z = round(x * y, 4)  # округлим для красоты, но считаем точно
        p = px * py
        Z_vals.append(z)
        Z_probs.append(p)
        print(f"X={x} · Y={y} = {z:8.4f}    P = {px}·{py} = {p}")

# Суммируем вероятности для одинаковых значений (хотя здесь все уникальны)
# Но для корректности сгруппируем:
unique_Z = {}
for z, p in zip(Z_vals, Z_probs):
    unique_Z[z] = unique_Z.get(z, 0.0) + p

Z_vals_sorted = sorted(unique_Z.keys())
Z_probs_sorted = [unique_Z[z] for z in Z_vals_sorted]

print("\nРяд распределения Z = X·Y (после группировки):")
print("   z      |   P(Z=z)")
print("-" * 25)
for z, p in zip(Z_vals_sorted, Z_probs_sorted):
    print(f" {z:8.4f} | {p}")

# Проверка суммы вероятностей
sum_probs = sum(Z_probs_sorted)
print(f"\nСумма вероятностей: {sum_probs}  (должна равняться 1)")

# ----------------------------------------------------------------------
# 3) Вычисляем M[X·Y] двумя способами
# ----------------------------------------------------------------------
print("\n" + "-" * 50)
print("ШАГ 3: Проверка свойства M[X·Y] = M[X]·M[Y]")
print("-" * 50)

# Способ 1: по определению M[Z] = Σ z_k · p_k
M_XY_direct = sum(z * p for z, p in zip(Z_vals_sorted, Z_probs_sorted))

print("\nСпособ 1 (по ряду распределения Z):")
print("M[X·Y] = Σ (z_i · p_i) =")
terms = [f"{z}·{p}" for z, p in zip(Z_vals_sorted, Z_probs_sorted)]
print(" + ".join(terms))
print(f" = {M_XY_direct}")

# Способ 2: по свойству M[X]·M[Y]
M_XY_property = M_X * M_Y

print("\nСпособ 2 (по свойству математического ожидания):")
print("M[X]·M[Y] =", M_X, "·", M_Y, "=", M_XY_property)

# ----------------------------------------------------------------------
# 4) Вывод
# ----------------------------------------------------------------------
print("\n" + "-" * 50)
print("РЕЗУЛЬТАТ ПРОВЕРКИ")
print("-" * 50)

if abs(M_XY_direct - M_XY_property) < 1e-9:
    print("✓ Свойство ВЫПОЛНЯЕТСЯ:")
    print(f"  M[X·Y] = {M_XY_direct}")
    print(f"  M[X]·M[Y] = {M_XY_property}")
    print("  Значения совпадают.")
else:
    print("✗ Свойство НЕ выполняется. Ошибка в расчётах.")

# ----------------------------------------------------------------------
# ЗАДАЧА 2
# ----------------------------------------------------------------------
print("\n" + "=" * 70)
print("ЗАДАЧА 2")
print("=" * 70)
print("""Условие задачи:
Длительное наблюдение за числами остановок X и Y двух машин в час выявило,
что случайные величины X и Y определяются таблицами распределения:

    X   | 0   | 1   | 2
    P   | 0,3 | 0,6 | 0,1

    Y   | 0   | 1
    P   | 0,2 | 0,8

Определить законы распределения и характеристики случайных величин:
    a) X+Y (общее число остановок в час обеих машин);
    b) (X+Y)/2 (среднее число остановок).
""")

# Данные
X_vals2 = [0, 1, 2]
X_probs2 = [0.3, 0.6, 0.1]

Y_vals2 = [0, 1]
Y_probs2 = [0.2, 0.8]

print("\nИсходные данные:")
print("X:", list(zip(X_vals2, X_probs2)))
print("Y:", list(zip(Y_vals2, Y_probs2)))

# ----------------------------------------------------------------------
# 1) Ряд распределения S = X+Y
# ----------------------------------------------------------------------
print("\n" + "-" * 50)
print("ЧАСТЬ А: Закон распределения X+Y")
print("Для независимых X и Y: P(X+Y = s) = Σ P(X=x)·P(Y=s-x)")
print("-" * 50)

# Вычисляем все возможные суммы и их вероятности
S_vals = []
S_probs = []
for x, px in zip(X_vals2, X_probs2):
    for y, py in zip(Y_vals2, Y_probs2):
        s = x + y
        p = px * py
        S_vals.append(s)
        S_probs.append(p)

# Группируем по значениям суммы
unique_S = {}
for s, p in zip(S_vals, S_probs):
    unique_S[s] = unique_S.get(s, 0.0) + p

S_vals_sorted = sorted(unique_S.keys())
S_probs_sorted = [unique_S[s] for s in S_vals_sorted]

print("\nРяд распределения S = X+Y:")
print("   s    |   P(S=s)")
print("-" * 20)
for s, p in zip(S_vals_sorted, S_probs_sorted):
    print(f"   {s}    |   {p}")

# Проверка суммы
sum_s = sum(S_probs_sorted)
print(f"\nСумма вероятностей: {sum_s}")

# ----------------------------------------------------------------------
# Характеристики M[S] и D[S] через свойства
# ----------------------------------------------------------------------
print("\nХарактеристики S = X+Y:")

# M[S] = M[X] + M[Y]
M_X2 = sum(x * p for x, p in zip(X_vals2, X_probs2))
M_Y2 = sum(y * p for y, p in zip(Y_vals2, Y_probs2))
M_S = M_X2 + M_Y2

print(f"  M[X] = {M_X2}")
print(f"  M[Y] = {M_Y2}")
print(f"  M[S] = M[X] + M[Y] = {M_S}")

# D[S] = D[X] + D[Y] для независимых
D_X = sum((x - M_X2)**2 * p for x, p in zip(X_vals2, X_probs2))
D_Y = sum((y - M_Y2)**2 * p for y, p in zip(Y_vals2, Y_probs2))
D_S = D_X + D_Y

print(f"  D[X] = {D_X:.4f}")
print(f"  D[Y] = {D_Y:.4f}")
print(f"  D[S] = D[X] + D[Y] = {D_S:.4f}")

# σ[S] = sqrt(D[S])
import math
sigma_S = math.sqrt(D_S)
print(f"  σ[S] = √{D_S:.4f} = {sigma_S:.4f}")

# ----------------------------------------------------------------------
# 2) Ряд распределения A = (X+Y)/2
# ----------------------------------------------------------------------
print("\n" + "-" * 50)
print("ЧАСТЬ Б: Закон распределения (X+Y)/2")
print("Если S = X+Y, то A = S/2. Значения A = s/2, вероятности те же, что у S.")
print("-" * 50)

A_vals = [s / 2 for s in S_vals_sorted]
A_probs = S_probs_sorted

print("\nРяд распределения A = (X+Y)/2:")
print("    a     |   P(A=a)")
print("-" * 22)
for a, p in zip(A_vals, A_probs):
    print(f"   {a:4.1f}   |   {p}")

# Характеристики A
M_A = M_S / 2
D_A = D_S / 4   # D[S/2] = D[S] / 4
sigma_A = sigma_S / 2

print("\nХарактеристики A = (X+Y)/2:")
print(f"  M[A] = M[S] / 2 = {M_S} / 2 = {M_A}")
print(f"  D[A] = D[S] / 4 = {D_S:.4f} / 4 = {D_A:.4f}")
print(f"  σ[A] = σ[S] / 2 = {sigma_S:.4f} / 2 = {sigma_A:.4f}")

print("\n" + "=" * 70)
print("КОНЕЦ РЕШЕНИЯ")
print("=" * 70)