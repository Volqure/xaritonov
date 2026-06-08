# -*- coding: utf-8 -*-
"""
Непрерывные случайные величины — вывод в понятном текстовом виде
без \frac в коде результата
"""

import sympy as sp
from sympy.printing import pretty_print as pp
from sympy.printing import latex

# Настройка вывода в консоли
sp.init_printing(use_unicode=True, pretty_print=True)

print("=" * 70)
print("НЕПРЕРЫВНЫЕ СЛУЧАЙНЫЕ ВЕЛИЧИНЫ (Вариант 1)")
print("=" * 70)

# ----------------------------------------------------------------------
# ЗАДАЧА 1
# ----------------------------------------------------------------------
print("\n" + "=" * 70)
print("ЗАДАЧА 1")
print("=" * 70)
print("""
Плотность распределения: f(x) = (2/π)·cos²(x)  на (-π/2, π/2)
""")

x = sp.Symbol('x', real=True)
f1 = (2 / sp.pi) * sp.cos(x)**2

print("f(x) = ", end="")
pp(f1)

# Проверка нормировки
print("\n1) Проверка нормировки: ∫ f(x) dx = 1")
norm1 = sp.integrate(f1, (x, -sp.pi/2, sp.pi/2))
print("   ∫ f(x) dx = ", end="")
pp(norm1)
print("   → Условие выполняется." if abs(norm1 - 1) < 1e-9 else "   → Ошибка!")

# Математическое ожидание
print("\n2) Математическое ожидание M[X] = ∫ x·f(x) dx")
M1 = sp.integrate(x * f1, (x, -sp.pi/2, sp.pi/2))
print("   M[X] = ", end="")
pp(M1)

# Второй момент M[X²]
print("\n3) Второй момент M[X²] = ∫ x²·f(x) dx")
M_X2_1 = sp.integrate(x**2 * f1, (x, -sp.pi/2, sp.pi/2))
print("   M[X²] = ", end="")
pp(M_X2_1)

# Дисперсия
print("\n4) Дисперсия D[X] = M[X²] − (M[X])²")
D1 = sp.simplify(M_X2_1 - M1**2)
print("   D[X] = ", end="")
pp(D1)

print("\nОтвет по задаче 1:")
print("   M[X] = 0")
print("   D[X] = π²/12 − 1/2 ≈", float(D1))

# ----------------------------------------------------------------------
# ЗАДАЧА 2
# ----------------------------------------------------------------------
print("\n" + "=" * 70)
print("ЗАДАЧА 2")
print("=" * 70)
print("""
Плотность распределения: f(x) = a·x  при 0 ≤ x ≤ 2, иначе 0
""")

a = sp.Symbol('a', positive=True, real=True)
f2 = a * x

# Находим a из нормировки
norm2 = sp.integrate(f2, (x, 0, 2))
a_val = sp.solve(norm2 - 1, a)[0]
f2_final = f2.subs(a, a_val)

print("1) Находим a из условия ∫₀² a·x dx = 1")
print("   ∫₀² a·x dx = ", end="")
pp(norm2)
print(f"   → a = {a_val}")
print("   Плотность: f(x) = ", end="")
pp(f2_final)

# Математическое ожидание
print("\n2) M[X] = ∫₀² x·f(x) dx")
M2 = sp.integrate(x * f2_final, (x, 0, 2))
print("   M[X] = ", end="")
pp(M2)

# Второй момент
print("\n3) M[X²] = ∫₀² x²·f(x) dx")
M_X2_2 = sp.integrate(x**2 * f2_final, (x, 0, 2))
print("   M[X²] = ", end="")
pp(M_X2_2)

# Дисперсия
print("\n4) D[X] = M[X²] − (M[X])²")
D2 = sp.simplify(M_X2_2 - M2**2)
print("   D[X] = ", end="")
pp(D2)

print("\nОтвет по задаче 2:")
print(f"   a = {a_val}")
print("   M[X] = 4/3 ≈", float(M2))
print("   D[X] = 2/9 ≈", float(D2))

print("\n" + "=" * 70)
print("КОНЕЦ РЕШЕНИЯ")
print("=" * 70)