import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Trivia SOMP", page_icon="🩺", layout="centered")

# Título del juego
st.title("🩺💜 Trivia: ¿Mito o realidad sobre el SOMP?")
st.subheader("Pon a prueba tus conocimientos y combate la desinformación.")

# Cargar la base de datos automáticamente desde el repositorio
@st.cache_data
def cargar_datos():
    try:
        # Lee el archivo que está en la misma carpeta de GitHub
        df = pd.read_excel("Pensamiento - Base de datos.xlsx")
        return df
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'Pensamiento - Base de datos.xlsx' en el repositorio de GitHub. Revisa que el nombre coincida exactamente.")
        return None
    except Exception as e:
        st.error(f"❌ Error al leer el archivo Excel: {e}")
        return None

df = cargar_datos()

if df is not None:
    # Validar columnas
    columnas_requeridas = ["nivel", "categoría", "mito", "A", "B", "C", "D", "respuesta", "explicación"]
    falta_columna = False
    for columna in columnas_requeridas:
        if columna not in df.columns:
            st.error(f"❌ Falta la columna '{columna}' en el Excel.")
            falta_columna = True
    
    if not falta_columna:
        # Inicializar variables del estado de la sesión
        if "juego_iniciado" not in st.session_state:
            st.session_state.juego_iniciado = False
            st.session_state.preguntas = None
            st.session_state.pregunta_actual = 0
            st.session_state.puntaje = 0
            st.session_state.respondido = False
            st.session_state.respuesta_correcta = False

        # --- PANTALLA DE CONFIGURACIÓN ---
        if not st.session_state.juego_iniciado:
            st.markdown("### 📚 Configuración de la partida")
            
            orden_niveles = ["Fácil", "Medio", "Difícil"]
            niveles_disponibles = [n for n in orden_niveles if n in df["nivel"].unique()]
            
            if not niveles_disponibles:
                st.error("❌ No se encontraron los niveles 'Fácil', 'Medio' o 'Difícil' en la columna 'nivel' de tu Excel.")
            else:
                nivel_elegido = st.selectbox("Elige un nivel:", niveles_disponibles)
                
                if st.button("🚀 Comenzar Juego", use_container_width=True):
                    preguntas_nivel = df[df["nivel"] == nivel_elegido]
                    
                    if len(preguntas_nivel) == 0:
                        st.error("❌ No existen preguntas para ese nivel.")
                    else:
                        cantidad_preguntas = min(10, len(preguntas_nivel))
                        st.session_state.preguntas = preguntas_nivel.sample(n=cantidad_preguntas).reset_index(drop=True)
                        st.session_state.juego_iniciado = True
                        st.session_state.pregunta_actual = 0
                        st.session_state.puntaje = 0
                        st.session_state.respondido = False
                        st.rerun()

        # --- PANTALLA DE JUEGO ---
        else:
            preguntas = st.session_state.preguntas
            idx = st.session_state.pregunta_actual
            total_preguntas = len(preguntas)

            # Si terminaron las preguntas, mostrar resultados
            if idx >= total_preguntas:
                st.markdown("---")
                st.markdown("## 🏁 FIN DEL JUEGO")
                st.markdown(f"### ➡️ Puntaje: **{st.session_state.puntaje}/{total_preguntas}**")
                
                porcentaje = (st.session_state.puntaje / total_preguntas) * 100
                
                if porcentaje == 100:
                    st.balloons()
                    st.success("🏆 ¡Excelente! Conoces muy bien el SOMP.")
                elif porcentaje >= 80:
                    st.success("🌟 Muy buen trabajo. Tienes conocimientos sólidos sobre el SOMP.")
                elif porcentaje >= 60:
                    st.info("👏 Vas por buen camino. Sigue aprendiendo sobre el SOMP.")
                elif porcentaje >= 40:
                    st.warning("👀 Aún existen algunos mitos por aclarar.")
                else:
                    st.error("📖 Sigue informándote sobre el SOMP y ayuda a combatir la desinformación.")
                
                st.markdown("💜 *Gracias por jugar y aprender sobre el SOMP.*")
                
                if st.button("🔄 Volver a jugar"):
                    st.session_state.juego_iniciado = False
                    st.rerun()
            
            else:
                fila = preguntas.iloc[idx]
                
                st.markdown(f"**📖 Pregunta {idx + 1} de {total_preguntas}**")
                st.caption(f"📂 Categoría: {fila['categoría']}")
                
                st.info(f"**🔷 MITO:**\n\n{fila['mito']}")
                
                opciones = {
                    f"A) {fila['A']}": "A",
                    f"B) {fila['B']}": "B",
                    f"C) {fila['C']}": "C",
                    f"D) {fila['D']}": "D"
                }
                
                with st.form(key=f"form_pregunta_{idx}"):
                    seleccion = st.radio("Selecciona tu respuesta:", list(opciones.keys()))
                    enviar = st.form_submit_button("Enviar Respuesta", use_container_width=True)
                
                if enviar and not st.session_state.respondido:
                    st.session_state.respondido = True
                    letra_seleccionada = opciones[seleccion]
                    correcta = str(fila["respuesta"]).strip().upper()
                    
                    if letra_seleccionada == correcta:
                        st.session_state.respuesta_correcta = True
                        st.session_state.puntaje += 1
                    else:
                        st.session_state.respuesta_correcta = False
                
                if st.session_state.respondido:
                    correcta = str(fila["respuesta"]).strip().upper()
                    if st.session_state.respuesta_correcta:
                        st.success("✅ ¡Correcto!")
                    else:
                        st.error(f"❌ Incorrecto. La respuesta correcta era la **{correcta}**")
                    
                    st.markdown(f"**💡 Información:**\n\n{fila['explicación']}")
                    
                    if st.button("Siguiente Pregunta ➡️", use_container_width=True):
                        st.session_state.pregunta_actual += 1
                        st.session_state.respondido = False
                        st.rerun()

