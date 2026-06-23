import streamlit as st
import requests
import hashlib
import json
from datetime import datetime, date
# ==============================================================================
# 🔥 ENDPOINT NATIVO ULTRA-LIGHT PARA LANDING (NETLIFY)
# ==============================================================================
# Coloca aquí tus llaves correctas
WOMPI_INTEGRITY_SECRET = "WOMPI_INTEGRITY_SECRET" 
ANTHROPIC_API_KEY = "ANTHROPIC_API_KEY"

# Interceptamos las llamadas de la Landing Page antes de que Streamlit dibuje la pantalla
query_params = st.query_params

if "api_action" in query_params:
    accion = query_params["api_action"]
    
    # 💳 Caso 1: Firma Wompi
    if accion == "firma-wompi":
        try:
            referencia = query_params.get("reference", "")
            monto = query_params.get("amountInCents", "")
            moneda = query_params.get("currency", "COP")
            
            cadena_firma = f"{referencia}{monto}{moneda}{WOMPI_INTEGRITY_SECRET}"
            signature = hashlib.sha256(cadena_firma.encode('utf-8')).hexdigest()
            
            # Formato JSON limpio que el navegador acepta sin chistar
            st.code(json.dumps({"signature": signature}), language="json")
            st.stop()  
        except Exception as e:
            st.code(json.dumps({"error": str(e)}), language="json")
            st.stop()

    # 🤖 Caso 2: Chatbot IA
    elif accion == "chat":
        try:
            mensaje_usuario = query_params.get("message", "")
            prompt_sistema = (
                "Eres el asistente virtual premium de la Agencia A.R.I.Z.A. Tu objetivo es calificar "
                "al lead de forma fluida. Identifica con sutileza su nombre, sector, WhatsApp y "
                "su mayor CUELLO DE BOTELLA operativo. Sé persuasivo."
            )
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 600,
                    "system": prompt_sistema,
                    "messages": [{"role": "user", "content": mensaje_usuario}]
                },
                timeout=15
            )
            
            bot_reply = response.json()["content"][0]["text"] if response.status_code == 200 else "Disculpa, tengo intermitencia en mi núcleo de IA. Inténtalo de nuevo."
            
            # 💡 El truco maestro: Respondemos con un HTML que le manda el JSON a tu Landing
            html_bypasser = f"""
            <script>
                window.parent.postMessage({json.dumps({"reply": bot_reply})}, "https://agencia-ariza.netlify.app");
            </script>
            """
            st.components.v1.html(html_bypasser, height=0)
            st.stop()  
        except Exception as e:
            html_error = """
            <script>
                window.parent.postMessage({"reply": "Error de conexión en la nube."}, "https://agencia-ariza.netlify.app");
            </script>
            """
            st.components.v1.html(html_error, height=0)
            st.stop()
# ==============================================================================
# ABAJO DE ESTO QUEDA TU CÓDIGO ORIGINAL INTACTO:
# st.markdown("""<!DOCTYPE html>...""")
# ==============================================================================
# -------- CONFIG --------
SUPABASE_URL = "https://hivvykyslqodrrfmteer.supabase.co"
SUPABASE_KEY =  st.secrets["SUPABASE_KEY"]
HEADERS = {
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "apikey": SUPABASE_KEY,
    "Content-Type": "application/json"
}

# -------- SUPABASE: LEADS --------
def obtener_leads():
    r = requests.get(f"{SUPABASE_URL}/rest/v1/leads?order=created_at.desc", headers=HEADERS)
    return r.json() if r.status_code == 200 else []

def actualizar_lead(id_lead, datos):
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/leads?id=eq.{id_lead}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json=datos
    )
    return r.status_code == 204

# -------- SUPABASE: CLIENTES --------
def obtener_clientes():
    r = requests.get(f"{SUPABASE_URL}/rest/v1/clientes?order=created_at.desc", headers=HEADERS)
    return r.json() if r.status_code == 200 else []

def crear_cliente(datos):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/clientes",
        headers={**HEADERS, "Prefer": "return=representation"},
        json=datos
    )
    return r.status_code == 201

def actualizar_cliente(id_cliente, datos):
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/clientes?id=eq.{id_cliente}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json=datos
    )
    return r.status_code == 204

# -------- SUPABASE: PAGOS --------
def obtener_pagos():
    r = requests.get(f"{SUPABASE_URL}/rest/v1/pagos?order=fecha_pago.desc", headers=HEADERS)
    return r.json() if r.status_code == 200 else []

def registrar_pago(datos):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/pagos",
        headers={**HEADERS, "Prefer": "return=representation"},
        json=datos
    )
    return r.status_code == 201

# -------- UTILIDADES --------
def formato_cop(valor):
    """Formatea número a pesos colombianos"""
    if valor is None:
        return "$0"
    return f"${valor:,.0f}".replace(",", ".")

def calcular_mrr(clientes):
    """Calcula Monthly Recurring Revenue de clientes activos"""
    activos = [c for c in clientes if c.get("estado") == "Activo"]
    return sum(c.get("precio_mensual", 0) or 0 for c in activos)

# -------- CONFIG PAGINA --------
st.set_page_config(page_title="Panel CEO — A.R.I.Z.A.", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0a0a0a; }
.stButton > button {
    background: linear-gradient(135deg, #1a1500, #2a2000) !important;
    color: #C9A84C !important;
    border: 1px solid #C9A84C66 !important;
    border-radius: 4px !important;
    font-size: 12px !important;
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stSelectbox > div > div > div {
    background-color: #111111 !important;
    color: #e0e0e0 !important;
    border: 1px solid #C9A84C44 !important;
}
.stTextArea > div > div > textarea {
    background-color: #111111 !important;
    color: #e0e0e0 !important;
    border: 1px solid #C9A84C44 !important;
}
.metric-card {
    background: linear-gradient(135deg, #111, #1a1a1a);
    border: 1px solid #C9A84C33;
    border-radius: 8px;
    padding: 20px 24px;
    text-align: center;
}
.metric-num {
    font-family: serif;
    font-size: 42px;
    font-weight: 700;
    color: #C9A84C;
    line-height: 1;
}
.metric-label {
    font-size: 11px;
    color: #888;
    letter-spacing: 2px;
    margin-top: 6px;
}
.metric-card-green {
    background: linear-gradient(135deg, #0a1a0a, #112211);
    border: 1px solid #44ff4433;
    border-radius: 8px;
    padding: 20px 24px;
    text-align: center;
}
.metric-num-green {
    font-family: serif;
    font-size: 36px;
    font-weight: 700;
    color: #44ff88;
    line-height: 1;
}
.divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #C9A84C44, transparent);
    margin: 20px 0;
}
.section-title {
    font-family: serif;
    font-size: 16px;
    color: #C9A84C;
    margin-bottom: 16px;
}
.cliente-card {
    background: #111;
    border: 1px solid #C9A84C22;
    border-radius: 6px;
    padding: 16px 20px;
    margin: 8px 0;
}
.pago-row {
    background: #0d0d0d;
    border: 1px solid #C9A84C15;
    border-radius: 4px;
    padding: 10px 16px;
    margin: 4px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.bar-container {
    background: #1a1a1a;
    border-radius: 4px;
    height: 28px;
    width: 100%;
    margin: 2px 0;
    position: relative;
    overflow: hidden;
}
.bar-fill {
    height: 100%;
    border-radius: 4px;
    display: flex;
    align-items: center;
    padding-left: 8px;
    font-size: 11px;
    color: #fff;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# -------- HEADER --------
st.markdown("""
<div style='text-align:center; padding:20px 0 10px 0; border-bottom:1px solid #C9A84C33; margin-bottom:20px;'>
    <div style='font-family:serif; font-size:11px; color:#C9A84C; letter-spacing:4px;'>AGENCIA A.R.I.Z.A.</div>
    <div style='font-family:serif; font-size:26px; font-weight:700; color:#ffffff;'>Panel CEO</div>
    <div style='font-family:sans-serif; font-size:11px; color:#888888; letter-spacing:2px; margin-top:4px;'>LEADS · CLIENTES · INGRESOS · SEGUIMIENTO</div>
</div>
""", unsafe_allow_html=True)

# -------- MENU --------
if "menu_ceo" not in st.session_state:
    st.session_state.menu_ceo = "Resumen"

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("◈ RESUMEN", use_container_width=True):
        st.session_state.menu_ceo = "Resumen"
        st.rerun()
with col2:
    if st.button("◈ LEADS", use_container_width=True):
        st.session_state.menu_ceo = "Leads"
        st.rerun()
with col3:
    if st.button("◈ CLIENTES", use_container_width=True):
        st.session_state.menu_ceo = "Clientes"
        st.rerun()
with col4:
    if st.button("◈ INGRESOS", use_container_width=True):
        st.session_state.menu_ceo = "Ingresos"
        st.rerun()

menu = st.session_state.menu_ceo
st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ==============================
# RESUMEN
# ==============================
if menu == "Resumen":
    leads = obtener_leads()
    clientes = obtener_clientes()
    pagos = obtener_pagos()

    nuevos = len([l for l in leads if l.get("estado") == "Nuevo"])
    cerrados = len([l for l in leads if l.get("estado") == "Cerrado"])
    conversion = round((cerrados / len(leads) * 100), 1) if leads else 0
    activos = len([c for c in clientes if c.get("estado") == "Activo"])
    mrr = calcular_mrr(clientes)
    total_ingresos = sum(p.get("monto", 0) or 0 for p in pagos)

    st.markdown("<div class='section-title'>Resumen del negocio</div>", unsafe_allow_html=True)

    # Fila 1: Leads
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-num'>{len(leads)}</div><div class='metric-label'>TOTAL LEADS</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-num'>{nuevos}</div><div class='metric-label'>LEADS NUEVOS</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-num'>{cerrados}</div><div class='metric-label'>CERRADOS</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-num'>{conversion}%</div><div class='metric-label'>CONVERSIÓN</div></div>", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Fila 2: Negocio
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-card-green'><div class='metric-num-green'>{activos}</div><div class='metric-label'>CLIENTES ACTIVOS</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card-green'><div class='metric-num-green'>{formato_cop(mrr)}</div><div class='metric-label'>MRR (INGRESO RECURRENTE)</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card-green'><div class='metric-num-green'>{formato_cop(total_ingresos)}</div><div class='metric-label'>INGRESOS TOTALES</div></div>", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Leads recientes</div>", unsafe_allow_html=True)

    for lead in leads[:5]:
        color = {"Nuevo": "#C9A84C", "En proceso": "#4488ff", "Cerrado": "#44ff44", "Perdido": "#ff4444"}.get(lead.get("estado"), "#888")
        st.markdown(f"""
        <div style='background:#111; border:1px solid #C9A84C22; border-left:3px solid {color}; padding:12px 16px; border-radius:4px; margin:6px 0; display:flex; justify-content:space-between;'>
            <span style='color:#e0e0e0; font-size:13px;'><strong>{lead.get('nombre')}</strong> — {lead.get('empresa')} — {lead.get('sector')}</span>
            <span style='color:{color}; font-size:11px; letter-spacing:1px;'>{lead.get('estado')}</span>
        </div>
        """, unsafe_allow_html=True)

# ==============================
# LEADS
# ==============================
elif menu == "Leads":
    leads = obtener_leads()
    st.markdown("<div style='font-family:serif; font-size:20px; color:#C9A84C; margin-bottom:16px;'>Leads — Prospectos</div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", len(leads))
    with col2:
        st.metric("Nuevos", len([l for l in leads if l.get("estado") == "Nuevo"]))
    with col3:
        st.metric("En proceso", len([l for l in leads if l.get("estado") == "En proceso"]))
    with col4:
        st.metric("Cerrados", len([l for l in leads if l.get("estado") == "Cerrado"]))

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    filtro = st.selectbox("Filtrar:", ["Todos", "Nuevo", "En proceso", "Cerrado", "Perdido"])

    for lead in leads:
        if filtro != "Todos" and lead.get("estado") != filtro:
            continue

        color = {"Nuevo": "#C9A84C", "En proceso": "#4488ff", "Cerrado": "#44ff44", "Perdido": "#ff4444"}.get(lead.get("estado"), "#888")

        with st.expander(f"{lead.get('nombre')} — {lead.get('empresa')} — {lead.get('sector')}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Nombre:** {lead.get('nombre')}")
                st.markdown(f"**Empresa:** {lead.get('empresa')}")
                st.markdown(f"**WhatsApp:** {lead.get('whatsapp')}")
            with col2:
                st.markdown(f"**Sector:** {lead.get('sector')}")
                st.markdown(f"**Fecha:** {lead.get('created_at', '')[:10]}")
                st.markdown(f"<span style='color:{color}'>**Estado: {lead.get('estado')}**</span>", unsafe_allow_html=True)

            st.markdown(f"**Cuello de botella:** {lead.get('cuello_botella')}")

            nota = st.text_area("Notas:", value=lead.get('notas_ceo', '') or '', key=f"nota_{lead.get('id')}", placeholder="Escribe tus notas aquí...")

            col_a, col_b, col_c, col_d, col_e = st.columns(5)
            with col_a:
                if st.button("En proceso", key=f"lp_{lead.get('id')}"):
                    actualizar_lead(lead.get('id'), {"estado": "En proceso"})
                    st.rerun()
            with col_b:
                if st.button("Cerrado", key=f"lc_{lead.get('id')}"):
                    actualizar_lead(lead.get('id'), {"estado": "Cerrado"})
                    st.rerun()
            with col_c:
                if st.button("Perdido", key=f"lperd_{lead.get('id')}"):
                    actualizar_lead(lead.get('id'), {"estado": "Perdido"})
                    st.rerun()
            with col_d:
                if st.button("Guardar nota", key=f"ln_{lead.get('id')}"):
                    actualizar_lead(lead.get('id'), {"notas_ceo": nota})
                    st.success("✓ Nota guardada")
            with col_e:
                num = lead.get('whatsapp', '').replace(' ', '').replace('-', '')
                st.markdown(f"<a href='https://wa.me/57{num}' target='_blank' style='color:#C9A84C; font-size:12px;'>📱 WhatsApp</a>", unsafe_allow_html=True)

# ==============================
# CLIENTES
# ==============================
elif menu == "Clientes":
    clientes = obtener_clientes()
    activos = [c for c in clientes if c.get("estado") == "Activo"]
    suspendidos = [c for c in clientes if c.get("estado") == "Suspendido"]

    st.markdown("<div style='font-family:serif; font-size:20px; color:#C9A84C; margin-bottom:16px;'>Clientes Activos</div>", unsafe_allow_html=True)

    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-num'>{len(clientes)}</div><div class='metric-label'>TOTAL CLIENTES</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card-green'><div class='metric-num-green'>{len(activos)}</div><div class='metric-label'>ACTIVOS</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-num' style='color:#ff8844;'>{len(suspendidos)}</div><div class='metric-label'>SUSPENDIDOS</div></div>", unsafe_allow_html=True)
    with col4:
        mrr = calcular_mrr(clientes)
        st.markdown(f"<div class='metric-card-green'><div class='metric-num-green' style='font-size:28px;'>{formato_cop(mrr)}</div><div class='metric-label'>MRR</div></div>", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ---- Registrar nuevo cliente ----
    with st.expander("➕ Registrar nuevo cliente"):
        st.markdown("<div style='color:#888; font-size:12px; margin-bottom:12px;'>Completa los datos del nuevo cliente</div>", unsafe_allow_html=True)

        rc1, rc2 = st.columns(2)
        with rc1:
            cli_nombre = st.text_input("Nombre del contacto", key="cli_nombre")
            cli_empresa = st.text_input("Empresa", key="cli_empresa")
            cli_whatsapp = st.text_input("WhatsApp", key="cli_whatsapp", placeholder="3001234567")
            cli_sector = st.text_input("Sector", key="cli_sector", placeholder="Seguros, Salud, Legal...")
        with rc2:
            cli_plan = st.selectbox("Plan contratado", ["Básico", "Profesional", "Empresarial", "Gestión Documental"], key="cli_plan")

            precios_impl = {"Básico": 2500000, "Profesional": 3000000, "Empresarial": 6000000, "Gestión Documental": 1800000}
            precios_mens = {"Básico": 490000, "Profesional": 490000, "Empresarial": 490000, "Gestión Documental": 490000}

            cli_precio_impl = st.number_input("Precio implementación (COP)", value=precios_impl.get(cli_plan, 0), step=100000, key="cli_impl")
            cli_precio_mens = st.number_input("Precio mensual (COP)", value=precios_mens.get(cli_plan, 0), step=50000, key="cli_mens")
            cli_url = st.text_input("URL del sistema", key="cli_url", placeholder="https://sistema-cliente.onrender.com")

        cli_notas = st.text_area("Notas", key="cli_notas", placeholder="Información adicional...")

        if st.button("✓ Registrar cliente", key="btn_crear_cliente"):
            if cli_nombre and cli_empresa:
                datos = {
                    "nombre": cli_nombre,
                    "empresa": cli_empresa,
                    "whatsapp": cli_whatsapp,
                    "sector": cli_sector,
                    "plan": cli_plan,
                    "precio_implementacion": cli_precio_impl,
                    "precio_mensual": cli_precio_mens,
                    "url_sistema": cli_url,
                    "estado": "Activo",
                    "fecha_inicio": str(date.today()),
                    "notas": cli_notas
                }
                if crear_cliente(datos):
                    st.success("✓ Cliente registrado exitosamente")
                    st.rerun()
                else:
                    st.error("Error al registrar cliente")
            else:
                st.warning("Nombre y empresa son obligatorios")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ---- Filtro ----
    filtro_cli = st.selectbox("Filtrar por estado:", ["Todos", "Activo", "Suspendido", "Cancelado"], key="filtro_clientes")

    # ---- Lista de clientes ----
    for cliente in clientes:
        if filtro_cli != "Todos" and cliente.get("estado") != filtro_cli:
            continue

        estado = cliente.get("estado", "Activo")
        color_estado = {"Activo": "#44ff88", "Suspendido": "#ff8844", "Cancelado": "#ff4444"}.get(estado, "#888")
        plan = cliente.get("plan", "—")

        with st.expander(f"{cliente.get('nombre')} — {cliente.get('empresa')} — {plan}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Nombre:** {cliente.get('nombre')}")
                st.markdown(f"**Empresa:** {cliente.get('empresa')}")
                st.markdown(f"**WhatsApp:** {cliente.get('whatsapp')}")
                st.markdown(f"**Sector:** {cliente.get('sector')}")
            with col2:
                st.markdown(f"**Plan:** {plan}")
                st.markdown(f"**Implementación:** {formato_cop(cliente.get('precio_implementacion'))}")
                st.markdown(f"**Mensualidad:** {formato_cop(cliente.get('precio_mensual'))}")
                st.markdown(f"**Inicio:** {cliente.get('fecha_inicio', '—')}")
                st.markdown(f"<span style='color:{color_estado}'>**Estado: {estado}**</span>", unsafe_allow_html=True)

            url = cliente.get('url_sistema')
            if url:
                st.markdown(f"**Sistema:** [{url}]({url})")

            st.markdown(f"**Notas:** {cliente.get('notas') or '—'}")

            # Acciones
            st.markdown("<hr class='divider'>", unsafe_allow_html=True)
            ca, cb, cc, cd = st.columns(4)
            with ca:
                if estado != "Activo":
                    if st.button("Activar", key=f"ca_{cliente.get('id')}"):
                        actualizar_cliente(cliente.get('id'), {"estado": "Activo"})
                        st.rerun()
            with cb:
                if estado == "Activo":
                    if st.button("Suspender", key=f"cs_{cliente.get('id')}"):
                        actualizar_cliente(cliente.get('id'), {"estado": "Suspendido"})
                        st.rerun()
            with cc:
                if estado != "Cancelado":
                    if st.button("Cancelar", key=f"cx_{cliente.get('id')}"):
                        actualizar_cliente(cliente.get('id'), {"estado": "Cancelado"})
                        st.rerun()
            with cd:
                num = (cliente.get('whatsapp') or '').replace(' ', '').replace('-', '')
                if num:
                    st.markdown(f"<a href='https://wa.me/57{num}' target='_blank' style='color:#C9A84C; font-size:12px;'>📱 WhatsApp</a>", unsafe_allow_html=True)

    if not clientes:
        st.markdown("<div style='text-align:center; color:#666; padding:40px; font-size:14px;'>No hay clientes registrados. Usa el botón ➕ para agregar el primero.</div>", unsafe_allow_html=True)

# ==============================
# INGRESOS
# ==============================
elif menu == "Ingresos":
    clientes = obtener_clientes()
    pagos = obtener_pagos()

    total_ingresos = sum(p.get("monto", 0) or 0 for p in pagos)
    mrr = calcular_mrr(clientes)
    activos = len([c for c in clientes if c.get("estado") == "Activo"])

    # Ingresos del mes actual
    hoy = date.today()
    mes_actual = hoy.strftime("%Y-%m")
    pagos_mes = [p for p in pagos if (p.get("fecha_pago") or "")[:7] == mes_actual]
    ingresos_mes = sum(p.get("monto", 0) or 0 for p in pagos_mes)

    # Implementaciones vs mensualidades
    total_impl = sum(p.get("monto", 0) or 0 for p in pagos if p.get("tipo") == "Implementación")
    total_mens = sum(p.get("monto", 0) or 0 for p in pagos if p.get("tipo") == "Mensualidad")

    st.markdown("<div style='font-family:serif; font-size:20px; color:#C9A84C; margin-bottom:16px;'>Ingresos</div>", unsafe_allow_html=True)

    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card-green'><div class='metric-num-green' style='font-size:30px;'>{formato_cop(total_ingresos)}</div><div class='metric-label'>INGRESOS TOTALES</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card-green'><div class='metric-num-green' style='font-size:30px;'>{formato_cop(ingresos_mes)}</div><div class='metric-label'>ESTE MES</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card-green'><div class='metric-num-green' style='font-size:30px;'>{formato_cop(mrr)}</div><div class='metric-label'>MRR</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-num'>{activos}</div><div class='metric-label'>CLIENTES ACTIVOS</div></div>", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ---- Gráfica de ingresos por mes (barras HTML) ----
    if pagos:
        st.markdown("<div class='section-title'>Ingresos por mes</div>", unsafe_allow_html=True)

        # Agrupar pagos por mes
        ingresos_por_mes = {}
        for p in pagos:
            mes = (p.get("fecha_pago") or "")[:7]
            if mes:
                ingresos_por_mes[mes] = ingresos_por_mes.get(mes, 0) + (p.get("monto", 0) or 0)

        if ingresos_por_mes:
            meses_ordenados = sorted(ingresos_por_mes.keys())[-6:]  # Últimos 6 meses
            max_val = max(ingresos_por_mes.values()) if ingresos_por_mes else 1

            for mes in meses_ordenados:
                val = ingresos_por_mes[mes]
                pct = (val / max_val * 100) if max_val > 0 else 0
                nombre_mes = mes
                try:
                    dt = datetime.strptime(mes, "%Y-%m")
                    meses_es = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
                    nombre_mes = f"{meses_es[dt.month]} {dt.year}"
                except:
                    pass

                st.markdown(f"""
                <div style='display:flex; align-items:center; margin:6px 0;'>
                    <div style='width:80px; color:#888; font-size:12px; text-align:right; padding-right:12px;'>{nombre_mes}</div>
                    <div class='bar-container' style='flex:1;'>
                        <div class='bar-fill' style='width:{max(pct, 8)}%; background:linear-gradient(90deg, #1a3a1a, #44ff88);'>
                            {formato_cop(val)}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        # Composición de ingresos
        st.markdown("<div class='section-title'>Composición</div>", unsafe_allow_html=True)
        ci1, ci2 = st.columns(2)
        with ci1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-num' style='font-size:28px;'>{formato_cop(total_impl)}</div>
                <div class='metric-label'>IMPLEMENTACIONES</div>
            </div>
            """, unsafe_allow_html=True)
        with ci2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-num' style='font-size:28px;'>{formato_cop(total_mens)}</div>
                <div class='metric-label'>MENSUALIDADES</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ---- Registrar pago ----
    with st.expander("➕ Registrar pago"):
        st.markdown("<div style='color:#888; font-size:12px; margin-bottom:12px;'>Registra un pago recibido</div>", unsafe_allow_html=True)

        # Selector de cliente
        if clientes:
            opciones_clientes = {f"{c.get('nombre')} — {c.get('empresa')}": c.get('id') for c in clientes}
            cliente_sel = st.selectbox("Cliente", list(opciones_clientes.keys()), key="pago_cliente")
            cliente_id = opciones_clientes[cliente_sel]
        else:
            st.warning("Registra un cliente primero en el módulo Clientes")
            cliente_id = None

        pc1, pc2 = st.columns(2)
        with pc1:
            pago_concepto = st.text_input("Concepto", key="pago_concepto", placeholder="Implementación plan Básico / Mensualidad mayo...")
            pago_tipo = st.selectbox("Tipo", ["Implementación", "Mensualidad", "Adicional"], key="pago_tipo")
        with pc2:
            pago_monto = st.number_input("Monto (COP)", min_value=0, step=50000, key="pago_monto")
            pago_metodo = st.selectbox("Método de pago", ["Transferencia", "Wompi", "Efectivo", "Otro"], key="pago_metodo")

        pago_fecha = st.date_input("Fecha del pago", value=date.today(), key="pago_fecha")
        pago_notas = st.text_area("Notas del pago", key="pago_notas", placeholder="Detalles adicionales...")

        if st.button("✓ Registrar pago", key="btn_registrar_pago"):
            if cliente_id and pago_monto > 0 and pago_concepto:
                datos_pago = {
                    "cliente_id": cliente_id,
                    "concepto": pago_concepto,
                    "monto": pago_monto,
                    "tipo": pago_tipo,
                    "metodo_pago": pago_metodo,
                    "fecha_pago": str(pago_fecha),
                    "notas": pago_notas
                }
                if registrar_pago(datos_pago):
                    st.success("✓ Pago registrado exitosamente")
                    st.rerun()
                else:
                    st.error("Error al registrar pago")
            else:
                st.warning("Cliente, concepto y monto son obligatorios")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ---- Historial de pagos ----
    st.markdown("<div class='section-title'>Historial de pagos</div>", unsafe_allow_html=True)

    if pagos:
        # Crear mapa de clientes para mostrar nombres
        mapa_clientes = {c.get("id"): f"{c.get('nombre')} — {c.get('empresa')}" for c in clientes}

        for pago in pagos[:20]:
            tipo = pago.get("tipo", "—")
            color_tipo = {"Implementación": "#C9A84C", "Mensualidad": "#44ff88", "Adicional": "#4488ff"}.get(tipo, "#888")
            nombre_cli = mapa_clientes.get(pago.get("cliente_id"), "Cliente desconocido")

            st.markdown(f"""
            <div class='pago-row'>
                <div>
                    <span style='color:#e0e0e0; font-size:13px;'><strong>{pago.get('concepto')}</strong></span><br>
                    <span style='color:#666; font-size:11px;'>{nombre_cli} · {pago.get('fecha_pago', '—')} · {pago.get('metodo_pago', '—')}</span>
                </div>
                <div style='text-align:right;'>
                    <span style='color:#44ff88; font-size:16px; font-weight:700;'>{formato_cop(pago.get('monto'))}</span><br>
                    <span style='color:{color_tipo}; font-size:10px; letter-spacing:1px;'>{tipo.upper()}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center; color:#666; padding:40px; font-size:14px;'>No hay pagos registrados. Usa el botón ➕ para agregar el primero.</div>", unsafe_allow_html=True)

# -------- FOOTER --------
st.markdown("""
<div style='text-align:center; padding:20px 0; margin-top:30px; border-top:1px solid #C9A84C22; font-family:serif; font-size:10px; color:#C9A84C66; letter-spacing:3px;'>
    AGENCIA A.R.I.Z.A. — PANEL CEO
</div>
""", unsafe_allow_html=True)