import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import streamlit.components.v1 as components

# Configuración de la página
st.set_page_config(page_title="Simulador CW", layout="wide")

st.title("🏭 Simulador CW v2.0")
st.markdown("---")

# ==========================================
# 🎛️ BARRA LATERAL (CONTROLES)
# ==========================================
st.sidebar.header("⚙️ Configuración")

# --- CONTROL DE TIEMPO (NUEVO) ---
st.sidebar.subheader("⏱️ Tiempo de Animación")
st.sidebar.info("Si la cinta es muy larga, aumenta este tiempo para ver llegar las bolsas.")
duracion_segundos = st.sidebar.slider("Duración (segundos)", min_value=10, max_value=60, value=20, step=5)

# Grupo 1: Geometría
st.sidebar.subheader("1. Dimensiones (Metros)")
L_entrada = st.sidebar.number_input("Largo Entrada", value=5.0)
L_separadora = st.sidebar.number_input("Largo Separadora", value=1.2)
L_balanza = st.sidebar.number_input("Largo Balanza (CW)", value=1.5)
L_salida = st.sidebar.number_input("Largo Salida", value=5.0)

# Grupo 2: Producto
st.sidebar.subheader("2. Producto")
largo_bolsa_m = st.sidebar.number_input("Largo Bolsa (m)", value=0.8)
distancia_entre_bolsas_m = st.sidebar.number_input("Espacio entre bolsas (m)", value=0.5)
texto_logo = st.sidebar.text_input("Texto", value="HARINA")

# Grupo 3: Mecánica
st.sidebar.subheader("3. Motorización")
rpm_motor = st.sidebar.number_input("RPM Motor Base", value=1450)
diametro_rodillo_mm = st.sidebar.number_input("Diámetro Rodillo (mm)", value=160)

st.sidebar.subheader("4. Reductores (Relación)")
reductor_1 = st.sidebar.number_input("Red. Entrada", value=40.0)
reductor_2 = st.sidebar.number_input("Red. Separadora", value=30.0)
reductor_3 = st.sidebar.number_input("Red. Balanza", value=25.0)
reductor_4 = st.sidebar.number_input("Red. Salida", value=40.0)

# ==========================================
# 🧠 CÁLCULOS
# ==========================================
perimetro_rodillo_m = (np.pi * diametro_rodillo_mm) / 1000

def calcular_velocidad(reductor):
    if reductor == 0: return 0
    rpm_salida = rpm_motor / reductor
    return (rpm_salida * perimetro_rodillo_m) / 60

v1 = calcular_velocidad(reductor_1)
v2 = calcular_velocidad(reductor_2)
v3 = calcular_velocidad(reductor_3)
v4 = calcular_velocidad(reductor_4)

# ==========================================
# 📊 VISUALIZACIÓN DE DATOS
# ==========================================
st.subheader("📋 Ficha Técnica de la Línea")

col1, col2, col3, col4 = st.columns(4)

def mostrar_tarjeta(col, titulo, L, red, v, tipo="info"):
    with col:
        if tipo == "success": st.success(f"**{titulo}**")
        else: st.info(f"**{titulo}**")
        
        st.write(f"📏 Largo: **{L} m**")
        st.write(f"⚙️ Reductor: **1/{red}**")
        st.write(f"🔄 Motor: **{rpm_motor} rpm**")
        st.write(f"🚀 Vel: **{v:.2f} m/s**")
        st.caption(f"({v*60:.1f} m/min)")

mostrar_tarjeta(col1, "1. Entrada", L_entrada, reductor_1, v1)
mostrar_tarjeta(col2, "2. Separadora", L_separadora, reductor_2, v2)
mostrar_tarjeta(col3, "3. Checkweigher", L_balanza, reductor_3, v3, tipo="success")
mostrar_tarjeta(col4, "4. Salida", L_salida, reductor_4, v4)

st.markdown("### Estado del Sistema")
if v3 < v2:
    st.error("🛑 **ERROR DE DISEÑO:** La Balanza (CW) es más lenta que la Separadora.")
else:
    st.success("✅ **DISEÑO CORRECTO:** La Balanza es más rápida.")

# ==========================================
# 🎬 GENERACIÓN DE LA GRÁFICA (OPTIMIZADA)
# ==========================================
st.markdown("---")
if st.button('▶️ INICIAR SIMULACIÓN CW', use_container_width=True):
    
    # Espacio para mensajes de estado
    estado = st.empty()
    barra_progreso = st.progress(0)
    
    with st.spinner('Calibrando física y generando animación...'):
        
        # 1. Configuración de Física más liviana
        dt = 0.1  # AUMENTAMOS EL PASO (Antes 0.05). Calcula menos frames, carga más rápido.
        total_frames = int(duracion_segundos / dt)
        
        # Geometría
        alto_bolsa_m = 0.25
        limites = [L_entrada, 
                   L_entrada + L_separadora, 
                   L_entrada + L_separadora + L_balanza, 
                   L_entrada + L_separadora + L_balanza + L_salida]
        total_len = limites[3]

        fig, ax = plt.subplots(figsize=(10, 3))
        ax.set_xlim(0, total_len)
        ax.set_ylim(0, 2)
        ax.set_aspect('equal')
        ax.set_xlabel("Distancia (metros)")
        ax.set_yticks([])
        
        # Fondos
        colores = ['#e0e0e0', '#ddfadd', '#a3d6f5', '#fff5cc']
        nombres = ['Entrada', 'Separadora', 'CW (Balanza)', 'Salida']
        
        prev = 0
        for lim, col, nom in zip(limites, colores, nombres):
            ax.axvspan(prev, lim, color=col, alpha=0.7)
            ax.text((prev + lim)/2, 0.1, nom, ha='center', fontsize=8, color='#333', weight='bold')
            prev = lim

        # Generación de bolsas
        pitch = largo_bolsa_m + distancia_entre_bolsas_m
        num_bolsas = int(total_len / pitch) + 2
        bolsas = [{'x': - (i * pitch), 'v': v1} for i in range(num_bolsas)]
        
        rects = []
        texts = []
        for b in bolsas:
            r = plt.Rectangle((b['x'], 0.5), largo_bolsa_m, alto_bolsa_m, facecolor='peru', edgecolor='black')
            t = ax.text(b['x'], 0.6, texto_logo, ha='center', color='white', fontsize=6, weight='bold')
            ax.add_patch(r)
            rects.append(r)
            texts.append(t)

        def update(frame):
            # Actualizamos la barra de progreso visualmente cada 10 frames para no frenar el cálculo
            if frame % 10 == 0:
                progreso = min(frame / total_frames, 1.0)
                barra_progreso.progress(progreso)
            
            for i, b in enumerate(bolsas):
                c = b['x'] + largo_bolsa_m/2
                
                if c < limites[0]: b['v'] = v1
                elif c < limites[1]: b['v'] = v2
                elif c < limites[2]: b['v'] = v3
                else: b['v'] = v4
                
                b['x'] += b['v'] * dt
                
                if b['x'] > total_len:
                    xs = [bd['x'] for bd in bolsas if bd is not b]
                    b['x'] = min(xs) - pitch if xs else -pitch

                rects[i].set_x(b['x'])
                texts[i].set_position((b['x'] + largo_bolsa_m/2, 0.5 + alto_bolsa_m/2))
                
                if limites[1] < c < limites[2]:
                    if v3 < v2: rects[i].set_facecolor('#d62728')
                    else: rects[i].set_facecolor('peru')
                else:
                    rects[i].set_facecolor('peru')
            return rects + texts

        # Generamos la animación
        # interval=100 significa 100ms entre cuadros (ya que aumentamos el dt, aumentamos el intervalo para que se vea velocidad real)
        ani = animation.FuncAnimation(fig, update, frames=total_frames, interval=100, blit=False)
        
        estado.info("Renderizando video... (esto es lo más pesado, espera un momento)")
        html_video = ani.to_jshtml()
        
        # Limpieza
        barra_progreso.empty()
        estado.empty()
        
        components.html(html_video, height=400)
        plt.close(fig) # Cierra la figura para liberar memoria RAM

else:
    st.info("👆 Ajusta los valores y dale al Play. (Máx recomendado: 40 segundos)")

