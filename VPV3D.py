import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import Normalize
import random

# Параметры планеты и атмосферы
planet_radius = 2.0  # Увеличенный радиус планеты
atmosphere_thickness = planet_radius * 0.3  # Толщина атмосферы (40% от радиуса)
exosphere_thickness = planet_radius * 0.1  # Зона экзосферы (10% от радиуса)
total_particles = 150  # Общее количество частиц

# Начальные параметры для термальной диссипации
def initialize_particles():
    particles = []
    for _ in range(total_particles):
        # Случайное положение в экзосфере (90-100% от атмосферы)
        r = planet_radius + random.uniform(atmosphere_thickness - exosphere_thickness, 
                                         atmosphere_thickness)
        theta = random.uniform(0, 2*np.pi)
        phi = random.uniform(0, np.pi)
        
        # Преобразование в декартовы координаты
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta)
        z = r * np.cos(phi)
        
        # Случайная скорость (для термальной диссипации)
        speed = random.uniform(0, 0.1)
        vx = random.gauss(0, speed)
        vy = random.gauss(0, speed)
        vz = random.gauss(0, speed)
        
        # Тип частицы (H2 или He)
        particle_type = random.choices(['H2', 'He'], weights=[0.98, 0.02])[0]
        
        particles.append({
            'position': np.array([x, y, z]),
            'velocity': np.array([vx, vy, vz]),
            'escaped': False,
            'type': particle_type,
            'energy': 0.0  # для солнечного ветра
        })
    return particles

# Инициализация частиц
particles = initialize_particles()

# Создание фигуры
fig = plt.figure(figsize=(12, 6))
ax1 = fig.add_subplot(121, projection='3d')  # для термальной диссипации
ax2 = fig.add_subplot(122, projection='3d')  # для солнечного ветра

# Настройка графиков
plot_limits = [-planet_radius*1.5, planet_radius*1.5]
for ax in [ax1, ax2]:
    ax.set_xlim(plot_limits)
    ax.set_ylim(plot_limits)
    ax.set_zlim(plot_limits)
    ax.set_title('Термальная диссипация' if ax == ax1 else 'Диссипация солнечным ветром')
    ax.set_axis_off()

# Рисуем планету
u = np.linspace(0, 2 * np.pi, 100)
v = np.linspace(0, np.pi, 100)
x = planet_radius * np.outer(np.cos(u), np.sin(v))
y = planet_radius * np.outer(np.sin(u), np.sin(v))
z = planet_radius * np.outer(np.ones(np.size(u)), np.cos(v))
for ax in [ax1, ax2]:
    ax.plot_surface(x, y, z, color='yellow', alpha=0.5)

# Инициализация точек для частиц (уменьшен размер частиц)
particle_size = 5  # Уменьшенный размер частиц
scatter1 = ax1.scatter([], [], [], c=[], s=particle_size, cmap='viridis', 
                      norm=Normalize(vmin=0, vmax=1))
scatter2 = ax2.scatter([], [], [], c=[], s=particle_size, cmap='viridis', 
                      norm=Normalize(vmin=0, vmax=1))

# Текст с информацией
info_text1 = ax1.text2D(0.05, 0.95, "", transform=ax1.transAxes)
info_text2 = ax2.text2D(0.05, 0.95, "", transform=ax2.transAxes)

# Функция обновления для анимации
def update(frame):
    global particles
    
    escaped_count1 = 0
    escaped_count2 = 0
    
    # Обновляем позиции частиц для термальной диссипации
    pos1 = []
    colors1 = []
    sizes1 = []
    
    # Обновляем позиции частиц для диссипации солнечным ветром
    pos2 = []
    colors2 = []
    sizes2 = []
    
    for p in particles:
        if p['escaped']:
            if p['escaped'] == 'thermal':
                escaped_count1 += 1
            else:
                escaped_count2 += 1
            continue
        
        # Термальная диссипация
        r = np.linalg.norm(p['position'])
        
        # Проверка, чтобы частицы не заходили внутрь планеты
        if r < planet_radius:
            # Отталкиваем частицу от поверхности планеты
            direction = p['position'] / r
            p['position'] = planet_radius * 1.01 * direction
            p['velocity'] += direction * 0.01
            
        # Применяем гравитацию
        if r > planet_radius:
            gravity = -0.01 * p['position'] / r**3
            p['velocity'] += gravity
            
            # Проверка на улетание
            if (np.linalg.norm(p['velocity']) > 0.15 and 
                r > planet_radius + atmosphere_thickness*0.9):
                escape_prob = 0.1 if p['type'] == 'H2' else 0.01
                if random.random() < escape_prob:
                    p['escaped'] = 'thermal'
                    escaped_count1 += 1
                    continue
        
        # Диссипация солнечным ветром (только для частиц на дневной стороне)
        if p['position'][0] > 0:  # дневная сторона (x > 0)
            if random.random() < 0.02:
                p['energy'] += random.uniform(0, 0.5)
                
            if (p['energy'] > 0.3 and 
                r > planet_radius + atmosphere_thickness*0.9):
                escape_prob = 0.2 if p['type'] == 'H2' else 0.05
                if random.random() < escape_prob:
                    p['escaped'] = 'solar'
                    escaped_count2 += 1
                    continue
        
        # Обновление позиции
        p['position'] += p['velocity']
        
        # Добавляем частицу в списки для отображения
        pos1.append(p['position'])
        colors1.append(0 if p['type'] == 'H2' else 1)
        sizes1.append(particle_size)
        
        if p['position'][0] > 0:  # только дневная сторона для солнечного ветра
            pos2.append(p['position'])
            colors2.append(p['energy'])
            sizes2.append(particle_size + p['energy']*10)
    
    # Обновляем данные для scatter plot
    if pos1:
        pos1 = np.array(pos1)
        scatter1._offsets3d = (pos1[:, 0], pos1[:, 1], pos1[:, 2])
        scatter1.set_array(np.array(colors1))
        scatter1.set_sizes(np.array(sizes1))
    else:
        scatter1._offsets3d = ([], [], [])
    
    if pos2:
        pos2 = np.array(pos2)
        scatter2._offsets3d = (pos2[:, 0], pos2[:, 1], pos2[:, 2])
        scatter2.set_array(np.array(colors2))
        scatter2.set_sizes(np.array(sizes2))
    else:
        scatter2._offsets3d = ([], [], [])
    
    # Обновляем информацию
    info_text1.set_text(f"Термальная диссипация\nУлетевших частиц: {escaped_count1}\nОсталось: {total_particles - escaped_count1 - escaped_count2}")
    info_text2.set_text(f"Солнечный ветер\nУлетевших частиц: {escaped_count2}\nОсталось: {total_particles - escaped_count1 - escaped_count2}")
    
    return scatter1, scatter2, info_text1, info_text2

# Создание анимации
ani = FuncAnimation(fig, update, frames=200, interval=100, blit=False)

plt.tight_layout()
plt.show()