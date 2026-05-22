import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.metrics import r2_score

# ============================================================
# 1. ЗАГРУЗКА ДАННЫХ ИЗ EXCEL
# ============================================================
# Укажите путь к вашему файлу и названия столбцов
file_path = "данные.xlsx"   # измените на свой путь
df = pd.read_excel(file_path)

# Предположим, что столбцы называются 'X' и 'Y'
# Если названия другие, поменяйте здесь
X = df['X'].values
Y = df['Y'].values

n = len(X)

print("=" * 60)
print("ИСХОДНЫЕ ДАННЫЕ")
print("=" * 60)
print(df.to_string(index=False))
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

# Гипотеза о форме связи (будет выведена после расчётов)
# ============================================================

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================
def print_regression_stats(x, y, model_name, params, y_pred):
    """
    Выводит все статистики для заданной модели
    """
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
        if 'линейная' in model_name or 'гиперболическая' in model_name:
            b = params[1] if len(params) > 1 else params[0]
            elasticity = b * np.mean(x) / np.mean(y)
        elif 'степенная' in model_name:
            # y = a * x^b -> эластичность = b (константа)
            elasticity = params[1]
        elif 'показательная' in model_name:
            # y = a * e^(b*x) -> эластичность = b * x_mean
            elasticity = params[1] * np.mean(x)
        else:
            elasticity = None
    else:
        elasticity = None
    
    # t-статистики для параметров (упрощённо)
    # Для простоты выводим только значимость модели через F-критерий
    f_stat = (r2 / (1 - r2)) * (n - 2)
    from scipy.stats import f
    p_value_f = 1 - f.cdf(f_stat, 1, n - 2)
    
    print("\n" + "=" * 60)
    print(f"МОДЕЛЬ: {model_name}")
    print("=" * 60)
    if 'линейная' in model_name and len(params) == 2:
        print(f"Уравнение: y = {params[0]:.4f} + {params[1]:.4f} * x")
    elif 'гиперболическая' in model_name and len(params) == 2:
        print(f"Уравнение: y = {params[0]:.4f} + {params[1]:.4f} / x")
    elif 'степенная' in model_name and len(params) == 2:
        print(f"Уравнение: y = {params[0]:.4f} * x^{params[1]:.4f}")
    elif 'показательная' in model_name and len(params) == 2:
        print(f"Уравнение: y = {params[0]:.4f} * e^{params[1]:.4f} * x")
    
    print(f"\nКоэффициент корреляции r = {r:.4f}")
    print(f"Коэффициент детерминации R² = {r2:.4f}")
    print(f"Скорректированный R²_adj = {r2_adj:.4f}")
    print(f"Стандартная ошибка регрессии = {se_reg:.4f}")
    if elasticity is not None:
        print(f"Коэффициент эластичности (средний) = {elasticity:.4f}")
    
    print(f"\nF-статистика Фишера = {f_stat:.4f}")
    print(f"p-value (F-критерий) = {p_value_f:.6f}")
    if p_value_f < 0.05:
        print("  → Модель статистически значима (p < 0.05)")
    else:
        print("  → Модель статистически не значима (p >= 0.05)")
    
    return {'model': model_name, 'R2': r2, 'R2_adj': r2_adj, 
            'F_stat': f_stat, 'p_value': p_value_f, 
            'elasticity': elasticity, 'se': se_reg}

# ============================================================
# 3. ЛИНЕЙНАЯ МОДЕЛЬ
# ============================================================
from scipy.stats import linregress
slope, intercept, r_value, p_value, std_err = linregress(X, Y)
y_pred_lin = intercept + slope * X
params_lin = [intercept, slope]
stats_lin = print_regression_stats(X, Y, "1. Линейная регрессия", params_lin, y_pred_lin)

# ============================================================
# 4. ГИПЕРБОЛИЧЕСКАЯ МОДЕЛЬ  y = a + b / x
# ============================================================
X_inv = 1 / X
slope_inv, intercept_inv, _, _, _ = linregress(X_inv, Y)
y_pred_hyp = intercept_inv + slope_inv * X_inv
params_hyp = [intercept_inv, slope_inv]
stats_hyp = print_regression_stats(X, Y, "2. Гиперболическая регрессия (y = a + b/x)", params_hyp, y_pred_hyp)

# ============================================================
# 5. СТЕПЕННАЯ МОДЕЛЬ  y = a * x^b  (логарифмирование)
# ============================================================
# Избавляемся от нулей и отрицательных (для примера)
if np.all(X > 0) and np.all(Y > 0):
    logX = np.log(X)
    logY = np.log(Y)
    slope_log, intercept_log, _, _, _ = linregress(logX, logY)
    a_power = np.exp(intercept_log)
    b_power = slope_log
    y_pred_power = a_power * (X ** b_power)
    params_power = [a_power, b_power]
    stats_power = print_regression_stats(X, Y, "3. Степенная регрессия (y = a * x^b)", params_power, y_pred_power)
else:
    print("\nВНИМАНИЕ: Степенная модель не применима (есть нули или отрицательные значения).")
    stats_power = {'R2': -np.inf}

# ============================================================
# 6. ПОКАЗАТЕЛЬНАЯ МОДЕЛЬ  y = a * e^(b*x)
# ============================================================
if np.all(Y > 0):
    logY_exp = np.log(Y)
    slope_exp, intercept_exp, _, _, _ = linregress(X, logY_exp)
    a_exp = np.exp(intercept_exp)
    b_exp = slope_exp
    y_pred_exp = a_exp * np.exp(b_exp * X)
    params_exp = [a_exp, b_exp]
    stats_exp = print_regression_stats(X, Y, "4. Показательная регрессия (y = a * e^(b*x))", params_exp, y_pred_exp)
else:
    print("\nВНИМАНИЕ: Показательная модель не применима (Y <= 0).")
    stats_exp = {'R2': -np.inf}

# ============================================================
# 7. ВЫБОР ЛУЧШЕЙ МОДЕЛИ ПО R^2
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
x_pred = x_mean * 1.15   # увеличение на 15%

print("\n" + "=" * 60)
print("ПРОГНОЗ ПО ЛУЧШЕЙ МОДЕЛИ")
print("=" * 60)
print(f"Среднее значение фактора X̄ = {x_mean:.4f}")
print(f"Прогнозное значение X_прогноз = {x_pred:.4f} (+15% от среднего)")

if best_model['model'] == "1. Линейная регрессия":
    y_pred_future = intercept + slope * x_pred
    print(f"Уравнение: y = {intercept:.4f} + {slope:.4f} * x")
    print(f"Прогноз Y = {y_pred_future:.4f}")

elif best_model['model'] == "2. Гиперболическая регрессия (y = a + b/x)":
    y_pred_future = intercept_inv + slope_inv / x_pred
    print(f"Уравнение: y = {intercept_inv:.4f} + {slope_inv:.4f} / x")
    print(f"Прогноз Y = {y_pred_future:.4f}")

elif best_model['model'] == "3. Степенная регрессия (y = a * x^b)":
    y_pred_future = a_power * (x_pred ** b_power)
    print(f"Уравнение: y = {a_power:.4f} * x^{b_power:.4f}")
    print(f"Прогноз Y = {y_pred_future:.4f}")

elif best_model['model'] == "4. Показательная регрессия (y = a * e^(b*x))":
    y_pred_future = a_exp * np.exp(b_exp * x_pred)
    print(f"Уравнение: y = {a_exp:.4f} * e^{b_exp:.4f} * x")
    print(f"Прогноз Y = {y_pred_future:.4f}")

print("\n" + "=" * 60)
