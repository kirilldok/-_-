import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
import random

# Параметры системы
planet_radius = 2.0          # Радиус планеты
atmosphere_thickness = 0.6   # Толщина всей атмосферы (30% от радиуса)
exosphere_thickness = 0.2    # Толщина экзосферы (10% от радиуса)
total_particles = 400        # Общее количество частиц

# Границы слоев
exosphere_inner = planet_radius + atmosphere_thickness - exosphere_thickness
exosphere_outer = planet_radius + atmosphere_thickness

# Новые границы экзосферы (110%-145%)
exo_110 = planet_radius * 1.10
exo_145 = planet_radius * 1.45

def initialize_particles():
    particles = []
    for _ in range(total_particles):
        # 90% частиц в экзосфере, 10% в нижних слоях
        if random.random() < 0.9:
            r = random.uniform(exosphere_inner, exosphere_outer)
        else:
            r = planet_radius + (atmosphere_thickness - exosphere_thickness) * random.random()**2
        
        angle = random.uniform(0, 2*np.pi)
        x = r * np.cos(angle)
        y = r * np.sin(angle)
        
        if r > exosphere_inner:
            speed = random.uniform(0.02, 0.08)
        else:
            speed = random.uniform(0.005, 0.02)
            
        angle = random.uniform(0, 2*np.pi)
        vx = speed * np.cos(angle)
        vy = speed * np.sin(angle)
        
        particle_type = 'H2' if random.random() < 0.98 else 'He'
        
        particles.append({
            'position': np.array([x, y]),
            'velocity': np.array([vx, vy]),
            'escaped': False,
            'type': particle_type,
            'energy': 0.0
        })
    return particles

# Настройка графики
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
fig.suptitle('Модель диссипации атмосферы с границами экзосферы', y=0.98)

# Сохраняем патчи в переменные
def init_plot(ax):
    ax.set_xlim([-3.5, 3.5])
    ax.set_ylim([-3.5, 3.5])
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.3)
    
    # Планета
    planet = Circle((0, 0), planet_radius, color='darkorange', alpha=0.4)
    ax.add_patch(planet)
    
    # Границы атмосферы
    exo_inner_patch = Circle((0, 0), exosphere_inner, fill=False, 
                            linestyle='--', color='red', linewidth=1.5, alpha=0.7)
    ax.add_patch(exo_inner_patch)
    
    exo_outer_patch = Circle((0, 0), exosphere_outer, fill=False, 
                            linestyle='-', color='blue', linewidth=0.7, alpha=0.5)
    ax.add_patch(exo_outer_patch)
    
    # Новые границы
    exo_110_patch = Circle((0, 0), exo_110, fill=False, 
                          linestyle=':', color='green', linewidth=1.2, alpha=0.6)
    ax.add_patch(exo_110_patch)
    
    exo_145_patch = Circle((0, 0), exo_145, fill=False, 
                          linestyle=':', color='green', linewidth=1.2, alpha=0.6)
    ax.add_patch(exo_145_patch)
    
    # Подписи
    ax.text(0, exosphere_inner*1.05, 'Нижняя граница экзосферы', 
           ha='center', color='red', fontsize=9)
    ax.text(0, exo_110*1.05, '110% R', ha='center', color='green', fontsize=8)
    ax.text(0, exo_145*1.05, '145% R', ha='center', color='green', fontsize=8)

init_plot(ax1)
init_plot(ax2)

ax1.set_title('Термальная диссипация (все частицы)')
ax2.set_title('Воздействие солнечного ветра (x > 0)')

# Инициализация
particles = initialize_particles()
scatter1 = ax1.scatter([], [], c=[], s=10, cmap='coolwarm', vmin=0, vmax=1)
scatter2 = ax2.scatter([], [], c=[], s=10, cmap='coolwarm', vmin=0, vmax=1)

info_text1 = ax1.text(0.02, 0.95, "", transform=ax1.transAxes,
                     bbox=dict(facecolor='white', alpha=0.7))
info_text2 = ax2.text(0.02, 0.95, "", transform=ax2.transAxes,
                     bbox=dict(facecolor='white', alpha=0.7))

def update(frame):
    global particles
    
    escaped_thermal = escaped_solar = 0
    pos1, colors1, pos2, colors2 = [], [], [], []
    
    for p in particles:
        if p['escaped']: 
            if p['escaped'] == 'thermal': escaped_thermal += 1
            else: escaped_solar += 1
            continue
            
        p['position'] += p['velocity']
        r = np.linalg.norm(p['position'])
        
        if r < planet_radius:
            normal = p['position']/r
            p['position'] = planet_radius * 1.01 * normal
            p['velocity'] -= 1.8 * np.dot(p['velocity'], normal) * normal
            
        if r > planet_radius:
            p['velocity'] -= 0.0005 * p['position'] / r**3
            
        if r > exosphere_inner and random.random() < 0.05:
            p['escaped'] = 'thermal'
            escaped_thermal += 1
            continue
                
        if p['position'][0] > 0 and r > exosphere_inner:
            p['energy'] += 0.01 * random.random()
            if p['energy'] > 0.25 and random.random() < 0.1:
                p['escaped'] = 'solar' 
                escaped_solar += 1
                continue
                
        pos1.append(p['position'])
        colors1.append(0 if p['type'] == 'H2' else 1)
        if p['position'][0] > 0:
            pos2.append(p['position'])
            colors2.append(p['energy'])
    
    if pos1:
        scatter1.set_offsets(pos1)
        scatter1.set_array(np.array(colors1))
    if pos2:
        scatter2.set_offsets(pos2)
        scatter2.set_array(np.array(colors2))
    
    remaining = total_particles - escaped_thermal - escaped_solar
    info_text1.set_text(f"Осталось: {remaining}")
    info_text2.set_text(f"Осталось: {remaining}")
    
    return scatter1, scatter2, info_text1, info_text2

ani = FuncAnimation(fig, update, frames=300, interval=200, blit=False,
                   init_func=lambda: [scatter1, scatter2, info_text1, info_text2])

plt.tight_layout()
plt.show()