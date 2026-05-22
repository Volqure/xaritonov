import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import f

# ============================================================
# 1. ВВОД ДАННЫХ (вставьте свою таблицу)
# ============================================================
print("=" * 60)
print("ВВОД ДАННЫХ")
print("=" * 60)
print("Введите данные в формате: X Y")
print("Пример: 2 52")
print("Когда закончите, введите 'end'")
print("-" * 60)

X_list = []
Y_list = []

while True:
    user_input = input("> ")
    if user_input.lower() == 'end':
        break
    try:
        x_val, y_val = map(float, user_input.split())
        X_list.append(x_val)
        Y_list.append(y_val)
    except ValueError:
        print("Ошибка! Введите два числа через пробел или 'end' для завершения")

X = np.array(X_list)
Y = np.array(Y_list)
n = len(X)

# Альтернативный способ: захардкодить данные прямо здесь (раскомментируйте при необходимости)
# X = np.array([2, 3, 5, 7, 8, 10, 11, 12, 14, 16])
# Y = np.array([52, 58, 70, 82, 90, 102, 108, 115, 125, 135])

print("\n" + "=" * 60)
print("ИСХОДНЫЕ ДАННЫЕ")
print("=" * 60)
print(f"{'X':>8} {'Y':>8}")
for i in range(n):
    print(f"{X[i]:>8.2f} {Y[i]:>8.2f}")
print(f"\nКоличество наблюдений: n = {n}")
print(f"Среднее X: {np.mean(X):.4f}")
print(f"Среднее Y: {np.mean(Y):.4f}")

# ============================================================
# 2. ПОЛЕ КОРРЕЛЯЦИИ
# ============================================================
plt.figure(figsize=(8, 5))
plt.scatter(X, Y, color='blue', edgecolors='black', s=80)
plt.title('Поле корреляции', fontsize=14)
plt.xlabel('Фактор X', fontsize=12)
plt.ylabel('Результат Y', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

# Гипотеза о форме связи
print("\n" + "=" * 60)
print("ГИПОТЕЗА О ФОРМЕ СВЯЗИ")
print("=" * 60)
if np.corrcoef(X, Y)[0, 1] > 0:
    print("Гипотеза: связь положительная (с ростом X растёт Y)")
else:
    print("Гипотеза: связь отрицательная (с ростом X убывает Y)")
print("Предполагаемая форма связи: линейная (проверим через модели)")

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================
def print_regression_stats(x, y, model_name, params, y_pred):
    """Выводит все статистики для заданной модели"""
    n = len(y)
    y_mean = np.mean(y)
    
    # Коэффициент детерминации R^2
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y_mean) ** 2)
    r2 = 1 - ss_res / ss_tot
    r = np.sqrt(r2) if np.corrcoef(x, y)[0, 1] > 0 else -np.sqrt(r2)
    
    # Скорректированный R^2
    r2_adj = 1 - (1 - r2) * (n - 1) / (n - 2)
    
    # Стандартная ошибка регрессии
    se_reg = np.sqrt(ss_res / (n - 2))
    
    # Коэффициент эластичности
    if len(params) >= 2:
        if 'линейная' in model_name:
            b = params[1]
            elasticity = b * np.mean(x) / np.mean(y)
        elif 'гиперболическая' in model_name:
            b = params[1]
            elasticity = b * (1/np.mean(x)) / np.mean(y)  # для 1/x
        elif 'степенная' in model_name:
            elasticity = params[1]  # y = a*x^b -> эластичность = b
        elif 'показательная' in model_name:
            elasticity = params[1] * np.mean(x)  # y = a*e^(bx) -> эластичность = b*x_mean
        else:
            elasticity = None
    else:
        elasticity = None
    
    # F-критерий Фишера
    f_stat = (r2 / (1 - r2)) * (n - 2) if r2 < 1 else float('inf')
    p_value_f = 1 - f.cdf(f_stat, 1, n - 2)
    
    # t-статистики для коэффициентов
    if 'линейная' in model_name:
        # Стандартная ошибка коэффициента b
        sb = se_reg / np.sqrt(np.sum((x - np.mean(x)) ** 2))
        t_b = params[1] / sb
        # Стандартная ошибка коэффициента a
        sa = se_reg * np.sqrt(1/n + np.mean(x)**2 / np.sum((x - np.mean(x))**2))
        t_a = params[0] / sa
    else:
        t_a = t_b = None
    
    print("\n" + "=" * 60)
    print(f"МОДЕЛЬ: {model_name}")
    print("=" * 60)
    if 'линейная' in model_name and len(params) == 2:
        print(f"Уравнение: y = {params[0]:.4f} + {params[1]:.4f} * x")
        print(f"\nОценка значимости коэффициентов:")
        print(f"  t(коэф. a) = {t_a:.4f}  (критическое t(0.05;{n-2}) ≈ {stats.t.ppf(0.975, n-2):.4f})")
        print(f"  t(коэф. b) = {t_b:.4f}  (критическое t(0.05;{n-2}) ≈ {stats.t.ppf(0.975, n-2):.4f})")
        if abs(t_a) > stats.t.ppf(0.975, n-2):
            print("  → Коэффициенты СТАТИСТИЧЕСКИ ЗНАЧИМЫ")
        else:
            print("  → Коэффициенты НЕ ЗНАЧИМЫ")
    elif 'гиперболическая' in model_name and len(params) == 2:
        print(f"Уравнение: y = {params[0]:.4f} + {params[1]:.4f} / x")
    elif 'степенная' in model_name and len(params) == 2:
        print(f"Уравнение: y = {params[0]:.4f} * x^{params[1]:.4f}")
    elif 'показательная' in model_name and len(params) == 2:
        print(f"Уравнение: y = {params[0]:.4f} * e^({params[1]:.4f} * x)")
    
    print(f"\nКоэффициент корреляции r = {r:.4f}")
    print(f"Коэффициент детерминации R² = {r2:.4f}")
    print(f"Скорректированный R²_adj = {r2_adj:.4f}")
    print(f"Стандартная ошибка регрессии = {se_reg:.4f}")
    if elasticity is not None:
        print(f"Коэффициент эластичности (средний) = {elasticity:.4f}")
    
    print(f"\nF-критерий Фишера = {f_stat:.4f}")
    print(f"p-value (F-критерий) = {p_value_f:.6f}")
    if p_value_f < 0.05:
        print("  → Модель статистически надежна (p < 0.05)")
    else:
        print("  → Модель НЕ надежна (p >= 0.05)")
    
    return {'model': model_name, 'R2': r2, 'R2_adj': r2_adj, 
            'F_stat': f_stat, 'p_value': p_value_f, 
            'elasticity': elasticity, 'se': se_reg,
            'equation': params}

# ============================================================
# 3. ЛИНЕЙНАЯ МОДЕЛЬ
# ============================================================
slope, intercept, r_value, p_value, std_err = stats.linregress(X, Y)
y_pred_lin = intercept + slope * X
params_lin = [intercept, slope]
stats_lin = print_regression_stats(X, Y, "1. Линейная регрессия", params_lin, y_pred_lin)

# ============================================================
# 4. ГИПЕРБОЛИЧЕСКАЯ МОДЕЛЬ  y = a + b / x
# ============================================================
X_inv = 1 / X
slope_inv, intercept_inv, _, _, _ = stats.linregress(X_inv, Y)
y_pred_hyp = intercept_inv + slope_inv * X_inv
params_hyp = [intercept_inv, slope_inv]
stats_hyp = print_regression_stats(X, Y, "2. Гиперболическая регрессия", params_hyp, y_pred_hyp)

# ============================================================
# 5. СТЕПЕННАЯ МОДЕЛЬ  y = a * x^b
# ============================================================
if np.all(X > 0) and np.all(Y > 0):
    logX = np.log(X)
    logY = np.log(Y)
    slope_log, intercept_log, _, _, _ = stats.linregress(logX, logY)
    a_power = np.exp(intercept_log)
    b_power = slope_log
    y_pred_power = a_power * (X ** b_power)
    params_power = [a_power, b_power]
    stats_power = print_regression_stats(X, Y, "3. Степенная регрессия", params_power, y_pred_power)
else:
    print("\n⚠️ Степенная модель не применима (есть нули или отрицательные значения)")
    stats_power = {'R2': -np.inf, 'model': "3. Степенная регрессия (не применима)"}

# ============================================================
# 6. ПОКАЗАТЕЛЬНАЯ МОДЕЛЬ  y = a * e^(b*x)
# ============================================================
if np.all(Y > 0):
    logY_exp = np.log(Y)
    slope_exp, intercept_exp, _, _, _ = stats.linregress(X, logY_exp)
    a_exp = np.exp(intercept_exp)
    b_exp = slope_exp
    y_pred_exp = a_exp * np.exp(b_exp * X)
    params_exp = [a_exp, b_exp]
    stats_exp = print_regression_stats(X, Y, "4. Показательная регрессия", params_exp, y_pred_exp)
else:
    print("\n⚠️ Показательная модель не применима (Y <= 0)")
    stats_exp = {'R2': -np.inf, 'model': "4. Показательная регрессия (не применима)"}

# ============================================================
# 7. ВЫБОР ЛУЧШЕЙ МОДЕЛИ
# ============================================================
models_list = [stats_lin, stats_hyp, stats_power, stats_exp]
best_model = max(models_list, key=lambda x: x['R2'] if x['R2'] != -np.inf else -np.inf)

print("\n" + "=" * 60)
print("ВЫБОР ЛУЧШЕГО УРАВНЕНИЯ РЕГРЕССИИ")
print("=" * 60)
print(f"Лучшая модель: {best_model['model']}")
print(f"Максимальный R² = {best_model['R2']:.4f}")
print(f"Скорректированный R²_adj = {best_model['R2_adj']:.4f}")
print(f"F-статистика = {best_model['F_stat']:.4f}")

# ============================================================
# 8. ПРОГНОЗ ПО ЛУЧШЕЙ МОДЕЛИ
# ============================================================
x_mean = np.mean(X)
x_pred = x_mean * 1.15

print("\n" + "=" * 60)
print("ПРОГНОЗ ПО ЛУЧШЕЙ МОДЕЛИ")
print("=" * 60)
print(f"Среднее значение фактора X̄ = {x_mean:.4f}")
print(f"Прогнозное значение X_прогноз = {x_pred:.4f} (+15% от среднего)")

if 'Линейная' in best_model['model']:
    y_pred_future = intercept + slope * x_pred
    print(f"Уравнение: y = {intercept:.4f} + {slope:.4f} * x")
    print(f"Прогноз Y = {y_pred_future:.4f}")
elif 'Гиперболическая' in best_model['model']:
    y_pred_future = intercept_inv + slope_inv / x_pred
    print(f"Уравнение: y = {intercept_inv:.4f} + {slope_inv:.4f} / x")
    print(f"Прогноз Y = {y_pred_future:.4f}")
elif 'Степенная' in best_model['model']:
    y_pred_future = a_power * (x_pred ** b_power)
    print(f"Уравнение: y = {a_power:.4f} * x^{b_power:.4f}")
    print(f"Прогноз Y = {y_pred_future:.4f}")
elif 'Показательная' in best_model['model']:
    y_pred_future = a_exp * np.exp(b_exp * x_pred)
    print(f"Уравнение: y = {a_exp:.4f} * e^({b_exp:.4f} * x)")
    print(f"Прогноз Y = {y_pred_future:.4f}")

print("\n" + "=" * 60)
print("АНАЛИЗ ЗАВЕРШЕН")
print("=" * 60)
