import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
from collections import Counter
import os, re, unicodedata
from io import BytesIO

st.set_page_config(
    page_title="Comercial De Nigris | Inteligência Comercial",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# IDENTIDADE DA EMPRESA — ajuste aqui se necessário
# ============================================================
# Nomes que identificam a De Nigris nos dados de emplacamento
NOMES_DENIGRIS = [
    "COMERCIAL DE VEICULOS DE NIGRIS LTDA",
]
# Padrão regex para busca (gerado automaticamente a partir da lista acima)
REGEX_DENIGRIS = "|".join([re.escape(n) for n in NOMES_DENIGRIS])

def is_denigris(serie: pd.Series) -> pd.Series:
    """Retorna máscara booleana: True onde o concessionário é a De Nigris."""
    return serie.str.upper().str.contains(REGEX_DENIGRIS, na=False, regex=True)

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Source+Sans+3:wght@300;400;500;600&display=swap');
*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] * { font-family: 'Source Sans 3', sans-serif !important; }

[data-testid="stAppViewContainer"] { background: #f0f2f5 !important; color: #1a1e2a !important; }
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
.main .block-container { padding: 0 !important; max-width: 100% !important; }

/* TOPBAR */
.topbar { background:#0a1628; border-bottom:3px solid #c8a84b; padding:0 36px; height:62px;
  display:flex; align-items:center; justify-content:space-between; position:sticky; top:0; z-index:999; }
.topbar-title { font-family:'Playfair Display',serif !important; font-size:17px; font-weight:700; color:#fff; }
.topbar-sub { font-size:10px; color:#c8a84b; text-transform:uppercase; letter-spacing:2px; }
.topbar-avatar { width:34px; height:34px; background:rgba(200,168,75,0.15); border:1px solid #c8a84b55;
  border-radius:50%; display:inline-flex; align-items:center; justify-content:center;
  font-size:13px; color:#c8a84b; font-weight:700; }

/* PAGE */
.page-content { padding:28px 36px; max-width:1400px; margin:0 auto; }
.page-header { margin-bottom:24px; padding-bottom:16px; border-bottom:2px solid #e0e4ee; }
.page-header h1 { font-family:'Playfair Display',serif !important; font-size:24px; font-weight:700; color:#0a1628; margin-bottom:3px; }
.page-header p { font-size:13px; color:#6b7a99; }

/* KPI */
.kpi-card { background:#fff; border:1px solid #e0e4ee; border-radius:12px; padding:18px 20px;
  position:relative; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.04); }
.kpi-card::before { content:''; position:absolute; top:0;left:0;right:0; height:3px;
  background:linear-gradient(90deg,#0a1628,#c8a84b); }
.kpi-label { font-size:11px; text-transform:uppercase; letter-spacing:1.5px; color:#8a95b0; margin-bottom:7px; font-weight:600; }
.kpi-value { font-family:'Playfair Display',serif !important; font-size:28px; font-weight:700; color:#0a1628; line-height:1; }
.kpi-sub { font-size:12px; color:#8a95b0; margin-top:5px; }

/* SECTION TITLE */
.section-title { font-family:'Playfair Display',serif !important; font-size:15px; font-weight:700; color:#0a1628;
  margin:24px 0 12px 0; padding-bottom:8px; border-bottom:1px solid #e0e4ee; }

/* CLIENT HERO */
.client-hero { background:linear-gradient(135deg,#0a1628,#0f1e38); border:1px solid #1e3055;
  border-radius:14px; padding:26px 30px; margin-bottom:20px; }
.client-name { font-family:'Playfair Display',serif !important; font-size:21px; font-weight:700; color:#fff; margin-bottom:3px; }
.client-cnpj { font-size:13px; color:#c8a84b; font-family:monospace; letter-spacing:1px; }

/* INFO TABLE */
.info-table { background:#fff; border:1px solid #e0e4ee; border-radius:10px; overflow:hidden; }
.info-row { display:flex; align-items:flex-start; padding:10px 16px; border-bottom:1px solid #f0f2f7; }
.info-row:last-child { border-bottom:none; }
.info-label { font-size:11px; text-transform:uppercase; letter-spacing:1px; color:#8a95b0;
  width:140px; min-width:140px; padding-top:2px; font-weight:600; }
.info-value { font-size:13px; color:#2a3548; font-weight:500; flex:1; }

/* CONTACT BUTTONS */
.contact-btn { display:inline-flex; align-items:center; gap:5px; padding:6px 14px; border-radius:20px;
  font-size:12px; font-weight:600; text-decoration:none !important; cursor:pointer;
  transition:all 0.15s; margin:3px 4px 3px 0; border:1px solid; }
.btn-phone   { background:#e8f4ff; color:#0055bb; border-color:#b0d4ff; }
.btn-whatsapp{ background:#e8fff0; color:#007a3d; border-color:#a0e8c0; }
.btn-email   { background:#fff8e8; color:#a06000; border-color:#f0d090; }

/* BADGES */
.badge { display:inline-block; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700;
  text-transform:uppercase; letter-spacing:0.8px; }
.badge-top    { background:#fff8e0; color:#8a6000; border:1px solid #f0d080; }
.badge-ativo  { background:#e0f8e8; color:#007030; border:1px solid #80d090; }
.badge-baixa  { background:#fff4e0; color:#a05000; border:1px solid #f0c070; }
.badge-inativo{ background:#ffeee8; color:#a02020; border:1px solid #f0a090; }

/* ALERTS */
.alert-urgent { background:#ffeee8; border:1px solid #f0a090; border-left:4px solid #cc3300;
  border-radius:8px; padding:11px 15px; color:#8a2200; margin:8px 0; font-size:13px; }
.alert-hot    { background:#fff8e0; border:1px solid #f0d080; border-left:4px solid #e8a000;
  border-radius:8px; padding:11px 15px; color:#8a5000; margin:8px 0; font-size:13px; }
.alert-warm   { background:#e8f8ee; border:1px solid #90d8a8; border-left:4px solid #00aa55;
  border-radius:8px; padding:11px 15px; color:#005530; margin:8px 0; font-size:13px; }
.alert-cold   { background:#e8f0ff; border:1px solid #90b8f8; border-left:4px solid #0055cc;
  border-radius:8px; padding:11px 15px; color:#003080; margin:8px 0; font-size:13px; }

/* SÓCIO */
.socio-card { background:#f8f9fc; border:1px solid #e0e4ee; border-radius:10px; padding:15px 17px; margin-bottom:10px; }
.socio-name { font-family:'Playfair Display',serif !important; font-size:14px; font-weight:700; color:#0a1628; margin-bottom:2px; }
.socio-cargo { font-size:11px; color:#0055aa; text-transform:uppercase; letter-spacing:0.8px; font-weight:600; }

/* FILTERS */
.filters-bar { background:#fff; border:1px solid #e0e4ee; border-radius:10px; padding:16px 20px; margin-bottom:22px; box-shadow:0 2px 6px rgba(0,0,0,0.04); }

/* UPLOAD */
.upload-section { background:#f8f9fc; border:1px dashed #c0c8dc; border-radius:10px; padding:18px 20px; margin-bottom:14px; }
.upload-title { font-size:13px; font-weight:700; color:#0a1628; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:6px; }

/* STREAMLIT OVERRIDES */
.stTextInput input, .stTextInput textarea {
  background:#fff !important; border:1px solid #d0d8ee !important;
  color:#1a1e2a !important; border-radius:8px !important; font-size:14px !important; }
.stButton>button { background:#0a1628 !important; color:#c8a84b !important; border:none !important;
  border-radius:8px !important; font-weight:700 !important; padding:8px 20px !important; }
.stButton>button:hover { background:#142038 !important; }
.stButton>button[kind="secondary"] { background:#f0f2f7 !important; color:#0a1628 !important; border:1px solid #d0d8ee !important; }
.stSelectbox>div>div, .stMultiSelect>div>div { background:#fff !important; border:1px solid #d0d8ee !important;
  color:#1a1e2a !important; border-radius:8px !important; }
.stDataFrame thead tr th { background:#0a1628 !important; color:#c8a84b !important; font-weight:700 !important; font-size:12px !important; }
.stTabs [data-baseweb="tab-list"] { background:#f0f2f7; border-radius:8px; padding:3px; gap:3px; }
.stTabs [data-baseweb="tab"] { background:transparent; border-radius:6px; font-weight:600; font-size:13px; color:#4a5568; }
.stTabs [aria-selected="true"] { background:#0a1628 !important; color:#c8a84b !important; }
div[data-testid="stExpander"] { background:#f8f9fc; border:1px solid #e0e4ee !important; border-radius:10px !important; }
.stDownloadButton>button { background:#0a1628 !important; color:#c8a84b !important; font-weight:700 !important; border:none !important; border-radius:8px !important; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPERS
# ============================================================
def norm_str(s):
    """Normaliza string: uppercase, sem acento, sem espaço duplo."""
    if not isinstance(s, str):
        s = str(s)
    s = s.upper().strip()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r'\s+', ' ', s)
    return s

def norm_cnpj(s):
    return re.sub(r"[.\-/]", "", str(s)).strip()

def format_tel(ddd, num):
    try:
        ddd = str(int(float(ddd))) if pd.notna(ddd) else ""
        num = str(int(float(num))) if pd.notna(num) else ""
        if ddd and num:
            return f"({ddd}) {num}"
    except:
        pass
    return ""

def safe_str(v, fallback="—"):
    s = str(v).strip()
    return fallback if s in ["nan", "None", "NaN", "", "NAN"] else s

def safe_atividade(last, col="ATIVIDADE_ECONOMICA"):
    """Retorna atividade econômica sem erro de TypeError."""
    v = last.get(col, None)
    s = safe_str(v)
    if s == "—": return "—"
    return (s[:90] + "...") if len(s) > 90 else s

def make_phone_number(ddd, num):
    """Monta número de telefone para links tel: e wa.me/"""
    try:
        d = str(int(float(ddd))) if pd.notna(ddd) else ""
        n = str(int(float(num))) if pd.notna(num) else ""
        if d and n: return f"55{d}{n}"
    except: pass
    return ""

MESES_PT = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
            7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}

def get_modes(series, top=3):
    s = series.dropna().astype(str)
    s = s[~s.isin(["nan", "None", "NaN", "", "N/A"])]
    if s.empty:
        return []
    return [x for x, _ in Counter(s).most_common(top)]

def calc_prediction(dates):
    if not dates or len(dates) < 2:
        return None, None
    dates = sorted([d for d in dates if pd.notna(d)])
    intervals = []
    for i in range(1, len(dates)):
        d = relativedelta(dates[i], dates[i-1])
        m = d.years * 12 + d.months
        intervals.append(max(m, 0.5))
    avg = max(sum(intervals) / len(intervals), 1)
    predicted = dates[-1] + relativedelta(months=int(round(avg)))
    meses_pt = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    label = f"{meses_pt[predicted.month-1]} de {predicted.year}"
    return label, predicted

def get_badge_class(cls):
    c = str(cls).lower()
    if "top" in c: return "badge-top"
    if "baixa" in c: return "badge-baixa"
    if "ativo" in c: return "badge-ativo"
    return "badge-inativo"


# ============================================================
# CARREGAMENTO DE DADOS
# ============================================================
@st.cache_data(show_spinner=False)
def load_area_operacional(src):
    if isinstance(src, BytesIO): src.seek(0)
    df = pd.read_excel(src)
    df.columns = ["Regiao", "Municipio", "Bairro", "Consultor"]
    df = df.iloc[1:].reset_index(drop=True)   # remove linha de cabeçalho duplicada
    df["Municipio_norm"] = df["Municipio"].apply(norm_str)
    df["Bairro_norm"]    = df["Bairro"].apply(lambda x: norm_str(x) if pd.notna(x) else "")
    df["Consultor"]      = df["Consultor"].fillna("ZONA LIVRE").apply(norm_str)
    return df

@st.cache_data(show_spinner=False)
def load_carteira(src):
    if isinstance(src, BytesIO): src.seek(0)
    df = pd.read_excel(src)
    df.columns = [c.strip() for c in df.columns]
    df["CPF/CNPJ"]  = df["CPF/CNPJ"].astype(str).str.strip()
    df["CNPJ_NORM"] = df["CPF/CNPJ"].apply(norm_cnpj)
    df["VENDEDOR"]  = df["VENDEDOR"].astype(str).str.strip()
    return df

@st.cache_data(show_spinner=False)
def load_emplacamentos_file(src, label=""):
    """Carrega UM arquivo de emplacamentos (pode ser de qualquer mês/ano desde 2022)."""
    if isinstance(src, BytesIO): src.seek(0)
    # Descobrir a linha de cabeçalho (sempre contém 'Chassi')
    raw = pd.read_excel(src, header=None)
    header_row = 5  # padrão
    for i in range(15):
        row_vals = raw.iloc[i].astype(str).tolist()
        if any("Chassi" in v or "chassi" in v for v in row_vals):
            header_row = i
            break

    if isinstance(src, BytesIO): src.seek(0)
    df = pd.read_excel(src, header=header_row)
    df.columns = [c.strip() for c in df.columns]
    df["_fonte"] = label

    # Normalizar campos-chave
    for col in ["CPFCNPJPROPRIETARIO", "NOMEPROPRIETARIO", "NO_CIDADE",
                "NO_BAIRRO", "Placa", "Chassi", "Concessionário"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df["CNPJ_NORM"] = df["CPFCNPJPROPRIETARIO"].apply(norm_cnpj)
    df["Data emplacamento"] = pd.to_datetime(df["Data emplacamento"], dayfirst=True, errors="coerce")
    df["Ano"]  = df["Data emplacamento"].dt.year
    df["Mes"]  = df["Data emplacamento"].dt.month
    df["Placa_norm"] = df["Placa"].str.replace("-","").str.replace(" ","").str.upper()
    df["NO_CIDADE_NORM"] = df["NO_CIDADE"].apply(norm_str)
    df["NO_BAIRRO_NORM"] = df["NO_BAIRRO"].apply(lambda x: norm_str(x) if x not in ["nan","None"] else "")
    df.dropna(subset=["Ano"], inplace=True)
    df["Ano"] = df["Ano"].astype(int)
    return df

def merge_emplacamentos(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    """Concatena vários DataFrames de emplacamentos removendo duplicatas por Chassi."""
    merged = pd.concat(dfs, ignore_index=True)
    merged.drop_duplicates(subset=["Chassi"], keep="last", inplace=True)
    merged.sort_values("Data emplacamento", inplace=True)
    return merged

def get_consultor_por_cidade_bairro(cidade_norm: str, bairro_norm: str, df_area: pd.DataFrame) -> str:
    """Retorna o consultor responsável pela cidade/bairro."""
    if df_area is None:
        return None
    # 1. Tenta match cidade + bairro
    if bairro_norm:
        m = df_area[
            (df_area["Municipio_norm"] == cidade_norm) &
            (df_area["Bairro_norm"].str.contains(bairro_norm[:10], na=False))
        ]
        if not m.empty:
            return m.iloc[0]["Consultor"]
    # 2. Tenta match só cidade
    m = df_area[df_area["Municipio_norm"] == cidade_norm]
    if not m.empty:
        return m.iloc[0]["Consultor"]
    return None


# ============================================================
# USUÁRIOS — gerados dinamicamente da área operacional
# ============================================================
# Mapeamento consultor → usuário de login
USUARIO_FIXOS = {
    "ADMIN": {"senha": "admin2025", "perfil": "gestor", "nome": "Administrador"},
    "GERENTE": {"senha": "gerente2025", "perfil": "gerente", "nome": "Gerente"},
}
# Senhas padrão para consultores (login = primeira palavra do nome, senha = nome[:4].lower()+"2025")
def gerar_login(nome_consultor: str):
    partes = nome_consultor.split()
    login = partes[0].upper()
    senha = partes[0][:4].lower() + "2025"
    return login, senha


# ============================================================
# LOGIN
# ============================================================
if "user" not in st.session_state:
    st.session_state.user = None
if "df_area" not in st.session_state:
    st.session_state.df_area = None
if "df_cart" not in st.session_state:
    st.session_state.df_cart = None
if "df_emp_list" not in st.session_state:   # lista de DataFrames de emplacamentos
    st.session_state.df_emp_list = []
if "emp_fontes" not in st.session_state:     # rótulos dos arquivos carregados
    st.session_state.emp_fontes = []

# Tentar carregar área operacional padrão
DATA_DIR = "data"
AREA_FILE     = os.path.join(DATA_DIR, "ARÉA_OPERACIONAL_-_CONSULTORES_CAMINHÕES.xlsx")
CARTEIRA_FILE = os.path.join(DATA_DIR, "CARTEIRA_DE_CAMINHÕES.xlsx")

if st.session_state.df_area is None and os.path.exists(AREA_FILE):
    st.session_state.df_area = load_area_operacional(AREA_FILE)
if st.session_state.df_cart is None and os.path.exists(CARTEIRA_FILE):
    st.session_state.df_cart = load_carteira(CARTEIRA_FILE)

df_area = st.session_state.df_area

# Construir dict de usuários dinâmico
def build_usuarios():
    users = dict(USUARIO_FIXOS)
    if df_area is not None:
        consultores = df_area[df_area["Consultor"] != "ZONA LIVRE"]["Consultor"].unique()
        for c in consultores:
            # Pode ter "SUZAN ODA & FRANCISCO" — criar login para cada
            for parte in c.split("&"):
                nome = parte.strip()
                if not nome:
                    continue
                login, senha = gerar_login(nome)
                users[login] = {"senha": senha, "perfil": "vendedor",
                                "nome": nome.title(), "consultor_key": c}
    return users

USUARIOS = build_usuarios()

# ── Inicializar pagina ──
if "pagina" not in st.session_state:
    st.session_state.pagina = "🔍 Busca de Cliente"

if st.session_state.user is None:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;margin-top:60px;margin-bottom:16px;">
            <div style="display:inline-flex;align-items:center;justify-content:center;
                width:56px;height:56px;background:#0a1628;border-radius:12px;font-size:26px;margin-bottom:12px;">🚚</div><br>
            <span style="font-family:'Playfair Display',serif;font-size:22px;font-weight:700;color:#0a1628;">Comercial De Nigris</span><br>
            <span style="font-size:11px;color:#8a95b0;text-transform:uppercase;letter-spacing:2px;">Inteligência Comercial · Acesso Restrito</span>
        </div>
        """, unsafe_allow_html=True)
        usuario_input = st.text_input("Usuário", placeholder="Seu login")
        senha_input   = st.text_input("Senha", type="password", placeholder="••••••••")
        with st.expander("ℹ️ Como fazer login"):
            st.markdown("""
            **Gestores:** `ADMIN` / `GERENTE`  
            **Consultores:** use a **primeira palavra do seu nome** como login  
            Exemplo: `RENATA` → senha: `rena2025`  
            """)
        if st.button("Entrar no Sistema", use_container_width=True):
            key = usuario_input.strip().upper()
            if key in USUARIOS and USUARIOS[key]["senha"] == senha_input.strip():
                st.session_state.user = key
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos")
    st.stop()

usuario_atual = st.session_state.user
perfil_atual  = USUARIOS[usuario_atual]["perfil"]
nome_atual    = USUARIOS[usuario_atual]["nome"]
consultor_key = USUARIOS[usuario_atual].get("consultor_key", usuario_atual)

# ── Carregar dados ──
EMP_DEFAULT = os.path.join(DATA_DIR, "EMPLACAMENTO ANUAL - CAMINHÕES.xlsx")
if not st.session_state.df_emp_list and os.path.exists(EMP_DEFAULT):
    df_default = load_emplacamentos_file(EMP_DEFAULT, label="default")
    st.session_state.df_emp_list = [df_default]
    st.session_state.emp_fontes  = ["default"]

df_cart = st.session_state.get("df_cart")
df_area = st.session_state.get("df_area")
df_emp  = None
if st.session_state.df_emp_list:
    df_emp = merge_emplacamentos(st.session_state.df_emp_list)

# ── Páginas por perfil ──
if perfil_atual in ("gestor", "gerente"):
    PAGINAS = ["🔍 Busca de Cliente", "📍 Minha Área", "📊 Painel Geral",
               "📈 Gestão & Performance", "🎯 Oportunidades", "⚙️ Gerenciar Dados"]
else:
    PAGINAS = ["🔍 Busca de Cliente", "📍 Minha Área", "🎯 Oportunidades"]

if st.session_state.pagina not in PAGINAS:
    st.session_state.pagina = PAGINAS[0]

# ── TOPBAR ──
sigla = nome_atual[0].upper()
perfil_label = {"gestor": "Administrador", "gerente": "Gerente", "vendedor": "Consultor"}[perfil_atual]
st.markdown(f"""
<div class="topbar">
    <div style="display:flex;align-items:center;gap:14px;">
        <div style="width:36px;height:36px;background:rgba(200,168,75,0.15);border:1px solid #c8a84b55;
            border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;">🚚</div>
        <div>
            <div class="topbar-title">Comercial De Nigris</div>
            <div class="topbar-sub">Inteligência Comercial</div>
        </div>
    </div>
    <div style="display:flex;align-items:center;gap:12px;">
        <div style="text-align:right;">
            <div style="font-size:13px;color:#e8eaf0;font-weight:600;">{nome_atual}</div>
            <div style="font-size:10px;color:#c8a84b;text-transform:uppercase;letter-spacing:1px;">{perfil_label}</div>
        </div>
        <div class="topbar-avatar">{sigla}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── NAVBAR ──
nav_cols = st.columns(len(PAGINAS) + 1)
for i, p in enumerate(PAGINAS):
    with nav_cols[i]:
        if st.button(p, key=f"nav_{p}"):
            st.session_state.pagina = p
            st.rerun()
with nav_cols[-1]:
    if st.button("🚪 Sair", key="btn_sair"):
        st.session_state.user = None
        st.rerun()

pagina = st.session_state.pagina

# ============================================================
# CONTEÚDO
# ============================================================
st.markdown('<div class="page-content">', unsafe_allow_html=True)

# ============================================================
# PÁGINA: BUSCA DE CLIENTE
# ============================================================
if pagina == "🔍 Busca de Cliente":
    st.markdown("""
    <div class="page-header">
        <h1>Busca de Cliente</h1>
        <p>Pesquise por razão social, CNPJ/CPF ou placa · busca livre em toda a base</p>
    </div>""", unsafe_allow_html=True)

    if df_emp is None:
        st.warning("⚠️ Adicione ao menos um arquivo de emplacamentos na barra lateral.")
        st.stop()

    # ✅ Busca sempre usa df_emp COMPLETO — sem restrição por consultor
    anos_disp = sorted(df_emp["Ano"].unique(), reverse=True)
    col_s, col_y, col_b = st.columns([4, 1.5, 1])
    with col_s:
        query = st.text_input("", placeholder="🔍  Nome, CNPJ ou Placa — busca em toda a base...", label_visibility="collapsed")
    with col_y:
        anos_sel = st.multiselect("Ano(s):", anos_disp, default=anos_disp, label_visibility="collapsed",
                                  placeholder="Todos os anos")
    with col_b:
        buscar = st.button("Buscar", use_container_width=True)

    # SEMPRE usa a base completa, independente do perfil
    df_emp_filtrado = df_emp[df_emp["Ano"].isin(anos_sel)] if anos_sel else df_emp

    if buscar and query:
        q = query.strip()
        q_digits = re.sub(r"\D", "", q)
        q_placa  = q.replace("-","").replace(" ","").upper()

        mask = df_emp_filtrado["NOMEPROPRIETARIO"].str.contains(q, case=False, na=False)
        if len(q_digits) > 5:
            mask |= df_emp_filtrado["CNPJ_NORM"].str.contains(q_digits, na=False)
        if q_placa:
            mask |= df_emp_filtrado["Placa_norm"].str.contains(q_placa, na=False)

        results = df_emp_filtrado[mask]
        if results.empty:
            st.warning(f"Nenhum resultado para **{q}** nos anos selecionados.")
            st.stop()

        unique_cnpjs = results["CNPJ_NORM"].unique()
        st.markdown(f'<div style="color:#3a6a9a;font-size:13px;margin-bottom:12px;">✦ {len(unique_cnpjs)} cliente(s) encontrado(s)</div>', unsafe_allow_html=True)

        target_cnpj = unique_cnpjs[0]
        if len(unique_cnpjs) > 1:
            opcoes = []
            for c in unique_cnpjs:
                n = df_emp_filtrado[df_emp_filtrado["CNPJ_NORM"] == c]["NOMEPROPRIETARIO"].iloc[0]
                opcoes.append(f"{n}  —  {c}")
            sel = st.selectbox("Múltiplos clientes. Selecione:", opcoes)
            target_cnpj = sel.split("—")[-1].strip()

        # Usar TODOS os anos para a ficha (não só o filtrado)
        client_df  = df_emp[df_emp["CNPJ_NORM"] == target_cnpj].copy()
        client_srt = client_df.sort_values("Data emplacamento", ascending=False)
        last        = client_srt.iloc[0]

        # --- Dados da carteira ---
        cart_row = None
        vendedor_cart = None
        classificacao  = None
        if df_cart is not None:
            cm = df_cart[df_cart["CNPJ_NORM"] == target_cnpj]
            if not cm.empty:
                cart_row      = cm.iloc[0]
                vendedor_cart = safe_str(cart_row.get("VENDEDOR"))
                classificacao = safe_str(cart_row.get("Classificação Mercedes"))

        # --- Consultor por área operacional ---
        cidade_norm = norm_str(safe_str(last.get("NO_CIDADE", ""), ""))
        bairro_norm = norm_str(safe_str(last.get("NO_BAIRRO", ""), ""))
        consultor_area = get_consultor_por_cidade_bairro(cidade_norm, bairro_norm, df_area)

        # --- Estatísticas ---
        total_emp = len(client_df)
        first_d   = client_df["Data emplacamento"].min()
        last_d    = client_df["Data emplacamento"].max()
        anos_cli  = relativedelta(pd.Timestamp.now(), first_d).years if pd.notna(first_d) else 0
        marcas    = get_modes(client_df["Marca"])
        modelos   = get_modes(client_df["Modelo"])
        pred_label, pred_date = calc_prediction(client_df["Data emplacamento"].dropna().tolist())

        today = pd.Timestamp.now()
        months_to_next = None
        if pred_date:
            d = relativedelta(pred_date, today)
            months_to_next = d.years * 12 + d.months

        # --- Hero ---
        badge_class = get_badge_class(classificacao) if classificacao else "badge-inativo"
        badge_label = classificacao if classificacao else "Sem classificação"
        st.markdown(f"""
        <div class="client-hero">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
                <div>
                    <div class="client-name">{safe_str(last['NOMEPROPRIETARIO'])}</div>
                    <div class="client-cnpj">{safe_str(last['CPFCNPJPROPRIETARIO'])}</div>
                </div>
                <span class="badge {badge_class}">{badge_label}</span>
            </div>
        </div>""", unsafe_allow_html=True)

        # --- KPIs ---
        k1,k2,k3,k4 = st.columns(4)
        with k1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Emplacamentos Totais</div><div class="kpi-value">{total_emp}</div><div class="kpi-sub">Em todos os anos</div></div>', unsafe_allow_html=True)
        with k2:
            last_str = last_d.strftime("%d/%m/%Y") if pd.notna(last_d) else "—"
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Último Emplacamento</div><div class="kpi-value" style="font-size:20px;">{last_str}</div></div>', unsafe_allow_html=True)
        with k3:
            ps = pred_label or "Insuficiente"
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Próxima Compra Prevista</div><div class="kpi-value" style="font-size:18px;color:#0044aa;">{ps}</div></div>', unsafe_allow_html=True)
        with k4:
            anos_str = f"{anos_cli} ano{'s' if anos_cli!=1 else ''}" if anos_cli else "< 1 ano"
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Cliente há</div><div class="kpi-value" style="font-size:22px;">{anos_str}</div><div class="kpi-sub">Desde {first_d.strftime("%Y") if pd.notna(first_d) else "—"}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- Alerta de oportunidade ---
        if pred_label:
            if months_to_next is not None and months_to_next <= 0:
                st.markdown(f'<div class="alert-urgent">🚨 <strong>Atenção!</strong> Compra prevista para {pred_label} pode ter passado! Contato urgente.</div>', unsafe_allow_html=True)
            elif months_to_next is not None and months_to_next <= 2:
                st.markdown(f'<div class="alert-hot">🔥 <strong>Oportunidade quente!</strong> Compra prevista para {pred_label}. Aborde agora!</div>', unsafe_allow_html=True)
            elif months_to_next is not None and months_to_next <= 6:
                st.markdown(f'<div class="alert-warm">📅 <strong>Planeje a abordagem.</strong> Compra prevista para {pred_label}.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-cold">⏳ Próxima compra estimada para {pred_label}. Mantenha o relacionamento ativo.</div>', unsafe_allow_html=True)

        # --- Responsável ---
        resp_tags = ""
        if vendedor_cart and vendedor_cart != "—":
            resp_tags += f'<span style="background:#e8f0ff;border:1px solid #b0c8f8;color:#0044aa;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:600;margin-right:8px;">👤 Vendedor: {vendedor_cart}</span>'
        if consultor_area:
            resp_tags += f'<span style="background:#e8f8ee;border:1px solid #90d8a8;color:#006030;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:600;">📍 Consultor: {consultor_area.title()}</span>'
        if resp_tags:
            st.markdown(f'<div style="margin:12px 0 20px 0;">{resp_tags}</div>', unsafe_allow_html=True)

        # --- Dados Cadastrais + Preferências ---
        col_d, col_p = st.columns([3, 2])
        with col_d:
            st.markdown('<div class="section-title">📋 Dados Cadastrais</div>', unsafe_allow_html=True)

            # Coletar telefones/celulares com links
            phones_raw = []
            for i in range(1, 6):
                t = format_tel(last.get(f"DDD{i}"), last.get(f"TELEFONE{i}"))
                num = make_phone_number(last.get(f"DDD{i}"), last.get(f"TELEFONE{i}"))
                if t: phones_raw.append(("fixo", t, num))
            for i in range(1, 4):
                c = format_tel(last.get(f"DDD_CELULAR{i}"), last.get(f"CELULAR{i}"))
                num = make_phone_number(last.get(f"DDD_CELULAR{i}"), last.get(f"CELULAR{i}"))
                if c: phones_raw.append(("celular", c, num))

            email_val = safe_str(last.get("EMAIL",""))

            # Botões de contato
            contact_btns = ""
            msg_prosp = "Olá! Entro em contato da Comercial De Nigris para apresentar nossas soluções em caminhões. Podemos conversar?"
            for tipo, fmt, num in phones_raw[:3]:
                if tipo == "celular":
                    contact_btns += f'<a href="https://wa.me/{num}?text={msg_prosp}" target="_blank" class="contact-btn btn-whatsapp">💬 {fmt}</a>'
                contact_btns += f'<a href="tel:+{num}" class="contact-btn btn-phone">📞 {fmt}</a>'
            if email_val != "—":
                subj = "Comercial De Nigris - Proposta Comercial"
                body = "Olá, entro em contato da Comercial De Nigris para apresentar nossas soluções em caminhões."
                contact_btns += f'<a href="mailto:{email_val}?subject={subj}&body={body}" class="contact-btn btn-email">✉️ E-mail</a>'
            if contact_btns:
                st.markdown(f'<div style="margin-bottom:14px;">{contact_btns}</div>', unsafe_allow_html=True)

            endereco = " ".join([safe_str(last.get(c,""),"") for c in ["NO_LOGR","NU_LOGR","NO_COMPL","NO_BAIRRO"]]).strip(" —")
            infos = [
                ("Razão Social",     safe_str(last.get("NOMEPROPRIETARIO",""))),
                ("Nome Fantasia",    safe_str(last.get("NOME_FANTASIA",""))),
                ("Endereço",         endereco or "—"),
                ("Cidade / UF",      f"{safe_str(last.get('NO_CIDADE',''))} - {safe_str(last.get('SG_ESTADO',''))}"),
                ("CEP",              str(int(float(last.get("NU_CEP",0)))) if pd.notna(last.get("NU_CEP")) and str(last.get("NU_CEP","")) not in ["nan",""] else "—"),
                ("E-mail",           email_val),
                ("Site",             safe_str(last.get("SITE",""))),
                ("Atividade",        safe_atividade(last)),
                ("Natureza Jurídica",safe_str(last.get("NATUREZA_JURIDICA",""))),
                ("Situação Receita", safe_str(last.get("SITUACAO_RECEITA",""))),
                ("Data Abertura",    safe_str(last.get("DT_ABERTURA",""))),
            ]
            st.markdown('<div class="info-table">', unsafe_allow_html=True)
            for lbl, val in infos:
                st.markdown(f'<div class="info-row"><div class="info-label">{lbl}</div><div class="info-value">{val}</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_p:
            st.markdown('<div class="section-title">🏷️ Preferências de Compra</div>', unsafe_allow_html=True)
            st.markdown('<div class="info-table">', unsafe_allow_html=True)
            for m in marcas:
                cnt = len(client_df[client_df["Marca"]==m])
                st.markdown(f'<div class="info-row"><div class="info-label">Marca</div><div class="info-value">{m} <span style="color:#8a95b0;font-size:11px;">({cnt}x)</span></div></div>', unsafe_allow_html=True)
            for mod in modelos:
                cnt = len(client_df[client_df["Modelo"]==mod])
                st.markdown(f'<div class="info-row"><div class="info-label">Modelo</div><div class="info-value" style="font-size:12px;">{mod} <span style="color:#8a95b0;font-size:11px;">({cnt}x)</span></div></div>', unsafe_allow_html=True)
            for conc in get_modes(client_df["Concessionário"], top=2):
                icon = "✅" if any(n in conc.upper() for n in NOMES_DENIGRIS) else "⚠️"
                st.markdown(f'<div class="info-row"><div class="info-label">Concessionária</div><div class="info-value" style="font-size:11px;">{icon} {conc}</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            nigris_cnt = int(is_denigris(client_df["Concessionário"]).sum())
            color = "#007030" if nigris_cnt > 0 else "#a02020"
            bg_n  = "#e8f8ee" if nigris_cnt > 0 else "#ffeee8"
            st.markdown(f"""
            <div style="margin-top:14px;background:{bg_n};border:1px solid #e0e4ee;border-radius:10px;padding:14px 16px;">
                <div style="font-size:11px;color:#8a95b0;text-transform:uppercase;letter-spacing:1px;margin-bottom:5px;">Compras na Comercial De Nigris</div>
                <div style="font-family:'Playfair Display',serif;font-size:28px;font-weight:700;color:{color};">{nigris_cnt}</div>
                <div style="font-size:12px;color:#6b7a99;">de {total_emp} emplacamentos totais</div>
            </div>""", unsafe_allow_html=True)

        # --- Sócios ---
        st.markdown('<div class="section-title">🤝 Quadro Societário</div>', unsafe_allow_html=True)
        socios = []
        for i in range(1, 4):
            nome_s = safe_str(last.get(f"NOME_SOCIO_DIRETOR{i}"), "")
            if nome_s and nome_s != "—":
                cel_s    = format_tel(last.get(f"DDD1_CEL_SOCIO{i}"), last.get(f"TEL1_CEL_SOCIO{i}"))
                cel_num_s = make_phone_number(last.get(f"DDD1_CEL_SOCIO{i}"), last.get(f"TEL1_CEL_SOCIO{i}"))
                email_s   = safe_str(last.get(f"EMAIL_SOCIO{i}"))
                socios.append({
                    "nome": nome_s, "cpf": safe_str(last.get(f"NU_CPF_CNPJ{i}")),
                    "cargo": safe_str(last.get(f"CARGO{i}")),
                    "email": email_s, "cel": cel_s, "cel_num": cel_num_s,
                })
        if socios:
            cols_s = st.columns(min(len(socios), 3))
            for idx, s in enumerate(socios):
                with cols_s[idx]:
                    btns_s = ""
                    if s["cel"] and s["cel"] != "—":
                        msg_s = "Olá! Entro em contato da Comercial De Nigris."
                        btns_s += f'<a href="https://wa.me/{s["cel_num"]}?text={msg_s}" target="_blank" class="contact-btn btn-whatsapp" style="font-size:11px;padding:4px 10px;">💬 WhatsApp</a>'
                        btns_s += f'<a href="tel:+{s["cel_num"]}" class="contact-btn btn-phone" style="font-size:11px;padding:4px 10px;">📞 Ligar</a>'
                    if s["email"] != "—":
                        btns_s += f'<a href="mailto:{s["email"]}" class="contact-btn btn-email" style="font-size:11px;padding:4px 10px;">✉️ E-mail</a>'
                    st.markdown(f"""
                    <div class="socio-card">
                        <div class="socio-name">{s['nome']}</div>
                        <div class="socio-cargo">{s['cargo']}</div>
                        <div style="margin-top:8px;font-size:12px;color:#6b7a99;">
                            <div>CPF: {s['cpf']}</div>
                            <div>{s['email']}</div>
                        </div>
                        <div style="margin-top:8px;">{btns_s}</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#8a95b0;font-size:13px;padding:10px 0;">Dados societários não disponíveis.</div>', unsafe_allow_html=True)

        # --- Histórico anual ---
        st.markdown('<div class="section-title">📈 Histórico de Emplacamentos por Ano</div>', unsafe_allow_html=True)
        hist_ano = client_df.groupby("Ano").size().reset_index(name="Qtd")
        fig = go.Figure(go.Bar(x=hist_ano["Ano"].astype(str), y=hist_ano["Qtd"],
                               marker_color="#0a1628", marker_line_color="#c8a84b", marker_line_width=1.5))
        fig.update_layout(plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
                          font_color="#4a5568", height=220,
                          xaxis=dict(showgrid=False), yaxis=dict(showgrid=True,gridcolor="#f0f2f7"),
                          margin=dict(t=10,b=10,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)

        # --- Tabela detalhada ---
        st.markdown('<div class="section-title">🚚 Todos os Emplacamentos</div>', unsafe_allow_html=True)
        det = client_srt[["Data emplacamento","Placa","Chassi","Modelo","Marca","Concessionário","Ano"]].copy()
        det["Data emplacamento"] = det["Data emplacamento"].dt.strftime("%d/%m/%Y")
        det.columns = ["Data","Placa","Chassi","Modelo","Marca","Concessionária","Ano"]
        st.dataframe(det, use_container_width=True, hide_index=True)

    elif buscar and not query:
        st.warning("Digite algo para buscar.")


# ============================================================
# PÁGINA: MINHA ÁREA
# ============================================================
elif pagina == "📍 Minha Área":
    st.markdown("""
    <div class="page-header">
        <h1>Minha Área</h1>
        <p>Performance da sua região · ranking de clientes · filtro por mês</p>
    </div>""", unsafe_allow_html=True)

    if df_area is None:
        st.warning("⚠️ Carregue o arquivo de Área Operacional em Gerenciar Dados.")
        st.stop()
    if df_emp is None:
        st.warning("⚠️ Carregue os emplacamentos em Gerenciar Dados.")
        st.stop()

    today = pd.Timestamp.now()

    # ── Gestor pode alternar entre consultores; vendedor vê só a dele ──
    if perfil_atual in ("gestor", "gerente"):
        todos_cons = ["Todos"] + sorted(df_area[df_area["Consultor"] != "ZONA LIVRE"]["Consultor"].unique().tolist())
        sel_cons = st.selectbox("Ver área do consultor:", todos_cons)
        titulo_area = sel_cons if sel_cons != "Todos" else "Todos os Consultores"
    else:
        sel_cons = consultor_key
        titulo_area = nome_atual

    # ── Filtro de mês/ano — padrão = mês anterior ──
    st.markdown('<div class="filters-bar">', unsafe_allow_html=True)
    mes_anterior = today.month - 1 if today.month > 1 else 12
    ano_mes_ant  = today.year if today.month > 1 else today.year - 1
    anos_disp_a  = sorted(df_emp["Ano"].unique(), reverse=True)
    fc1, fc2 = st.columns(2)
    with fc1:
        sel_ano_area = st.selectbox("Ano:", anos_disp_a,
                                    index=anos_disp_a.index(ano_mes_ant) if ano_mes_ant in anos_disp_a else 0)
    with fc2:
        meses_disp_a = sorted(df_emp[df_emp["Ano"] == sel_ano_area]["Mes"].unique().tolist())
        meses_labels_a = [MESES_PT[m] for m in meses_disp_a]
        default_mes_label = MESES_PT.get(mes_anterior, meses_labels_a[-1]) if mes_anterior in meses_disp_a else meses_labels_a[-1]
        sel_mes_label_a = st.selectbox("Mês:", meses_labels_a,
                                       index=meses_labels_a.index(default_mes_label) if default_mes_label in meses_labels_a else len(meses_labels_a)-1)
        sel_mes_num_a = meses_disp_a[meses_labels_a.index(sel_mes_label_a)]
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Área e dados ──
    if sel_cons == "Todos":
        area_df = df_area[df_area["Consultor"] != "ZONA LIVRE"].copy()
        munic_area = df_area["Municipio_norm"].unique()
    else:
        area_df = df_area[df_area["Consultor"] == sel_cons].copy()
        munic_area = area_df["Municipio_norm"].unique()

    emp_mes  = df_emp[(df_emp["NO_CIDADE_NORM"].isin(munic_area)) &
                      (df_emp["Ano"] == sel_ano_area) & (df_emp["Mes"] == sel_mes_num_a)].copy()
    emp_area = df_emp[df_emp["NO_CIDADE_NORM"].isin(munic_area)].copy()

    # Banner
    cor_b = "#1a3a6a" if perfil_atual == "vendedor" else "#1a3a1a"
    brd_b = "#4488cc" if perfil_atual == "vendedor" else "#44aa66"
    st.markdown(f"""
    <div style="background:{cor_b}18;border:1px solid {brd_b}44;border-left:4px solid {brd_b};
        border-radius:12px;padding:15px 20px;margin-bottom:18px;">
        <div style="font-size:11px;text-transform:uppercase;letter-spacing:1.5px;color:{brd_b};margin-bottom:2px;">📍 Área Operacional</div>
        <div style="font-family:'Playfair Display',serif;font-size:19px;font-weight:700;color:#0a1628;">{titulo_area.title()}</div>
        <div style="font-size:12px;color:#6b7a99;margin-top:2px;">Período selecionado: {sel_mes_label_a} de {sel_ano_area}</div>
    </div>
    """, unsafe_allow_html=True)

    # KPIs do mês
    total_mes    = len(emp_mes)
    clientes_mes = emp_mes["CNPJ_NORM"].nunique()
    nigris_mes   = int(is_denigris(emp_mes["Concessionário"]).sum()) if total_mes > 0 else 0
    conc_mes     = total_mes - nigris_mes
    ms_mes       = round(nigris_mes / total_mes * 100, 1) if total_mes > 0 else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Emplacamentos no Mês</div><div class="kpi-value">{total_mes}</div><div class="kpi-sub">{sel_mes_label_a[:3]} {sel_ano_area}</div></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Clientes no Mês</div><div class="kpi-value">{clientes_mes}</div></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">De Nigris</div><div class="kpi-value" style="color:#007030;">{nigris_mes}</div></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Concorrente</div><div class="kpi-value" style="color:#a02020;">{conc_mes}</div></div>', unsafe_allow_html=True)
    with k5: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Market Share</div><div class="kpi-value" style="color:#0044aa;">{ms_mes}%</div><div class="kpi-sub">no mês</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Clientes do mês
    if total_mes > 0:
        st.markdown(f'<div class="section-title">👥 Clientes que Emplacaram em {sel_mes_label_a}</div>', unsafe_allow_html=True)
        cli_mes = emp_mes.groupby(["CNPJ_NORM","NOMEPROPRIETARIO","NO_CIDADE"]).agg(
            Qtd=("Chassi","count"),
            De_Nigris=("Concessionário", lambda x: is_denigris(x).sum()),
            Marca=("Marca", lambda x: x.mode()[0] if not x.empty else "—"),
            Concessionaria=("Concessionário", lambda x: x.mode()[0] if not x.empty else "—"),
        ).reset_index().sort_values("Qtd", ascending=False)
        cli_mes["% De Nigris"] = (cli_mes["De_Nigris"]/cli_mes["Qtd"]*100).round(0).astype(int).astype(str)+"%"
        cli_mes_exib = cli_mes.drop(columns=["CNPJ_NORM"])
        cli_mes_exib.columns = ["Nome","Cidade","Qtd","De Nigris","Marca","Concessionária","% De Nigris"]
        cli_mes_exib.insert(0,"#",range(1,len(cli_mes_exib)+1))
        st.dataframe(cli_mes_exib, use_container_width=True, hide_index=True)
    else:
        st.info(f"Nenhum emplacamento em {sel_mes_label_a} de {sel_ano_area} nesta área.")

    # Gráficos
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown('<div class="section-title">📅 Emplacamentos por Mês (Ano Selecionado)</div>', unsafe_allow_html=True)
        emp_ano_sel = emp_area[emp_area["Ano"] == sel_ano_area]
        emp_mes_chart = emp_ano_sel.groupby("Mes").size().reset_index(name="Qtd")
        emp_mes_chart["Mes_nome"] = emp_mes_chart["Mes"].map(MESES_PT)
        fig = go.Figure(go.Bar(
            x=emp_mes_chart["Mes_nome"], y=emp_mes_chart["Qtd"],
            marker_color=["#c8a84b" if m == sel_mes_num_a else "#0a1628" for m in emp_mes_chart["Mes"]],
        ))
        fig.update_layout(plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", font_color="#4a5568", height=240,
                          xaxis=dict(showgrid=False, tickangle=-30), yaxis=dict(showgrid=True, gridcolor="#f0f2f7"),
                          margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

    with col_g2:
        st.markdown('<div class="section-title">🏷️ Marcas Emplacadas na Área</div>', unsafe_allow_html=True)
        marcas_area = emp_area["Marca"].value_counts().reset_index()
        marcas_area.columns = ["Marca", "Qtd"]
        fig2 = go.Figure(go.Pie(
            labels=marcas_area["Marca"], values=marcas_area["Qtd"], hole=0.45,
            marker_colors=["#0a1628","#0077cc","#0099ee","#00bbff","#1a6688","#2a5577","#1a3355","#0a1a33"]
        ))
        st.markdown('<div class="section-title">🏷️ Marcas na Área</div>', unsafe_allow_html=True)
        marcas_area = emp_area["Marca"].value_counts().reset_index()
        marcas_area.columns = ["Marca", "Qtd"]
        cores_pie = ["#0a1628","#c8a84b","#1a3a6a","#3a6aaa","#6a9acc","#a0c4e8","#d0e8f8","#f0f4fa"]
        fig2 = go.Figure(go.Pie(labels=marcas_area["Marca"], values=marcas_area["Qtd"], hole=0.45,
                                marker_colors=cores_pie))
        fig2.update_layout(plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", font_color="#4a5568", height=240,
                           margin=dict(t=10, b=10, l=10, r=10), legend=dict(font=dict(color="#4a5568", size=10)))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Top clientes da área ──
    top_cli = emp_area.groupby(["CNPJ_NORM", "NOMEPROPRIETARIO", "NO_CIDADE"]).agg(
        Total=("Chassi", "count"),
        UltimaCompra=("Data emplacamento", "max"),
        PrincipalMarca=("Marca", lambda x: x.mode()[0] if not x.empty else "—"),
        Na_De_Nigris=("Concessionário", lambda x: is_denigris(x).sum()),
    ).reset_index().sort_values("Total", ascending=False)
    top_cli["UltimaCompra"] = pd.to_datetime(top_cli["UltimaCompra"]).dt.strftime("%d/%m/%Y")
    top_cli["pct_nigris"] = (top_cli["Na_De_Nigris"] / top_cli["Total"] * 100).round(0).astype(int)

    # ── PÓDIO TOP 3 ──
    st.markdown('<div class="section-title">🏆 Top 3 Maiores Clientes (Histórico)</div>', unsafe_allow_html=True)
    podio_configs = [
        {"pos":1,"icon":"🥇","cor":"#B8860B","bg":"#fffbe8","borda":"#f0d060","label":"1º LUGAR"},
        {"pos":2,"icon":"🥈","cor":"#888888","bg":"#f8f8f8","borda":"#c0c0c0","label":"2º LUGAR"},
        {"pos":3,"icon":"🥉","cor":"#8B4513","bg":"#fff4ee","borda":"#d09060","label":"3º LUGAR"},
    ]
    ordem_visual = [1, 0, 2]
    top3 = top_cli.head(3).reset_index(drop=True)

    if len(top3) >= 1:
        cols_podio = st.columns(3)
        for col_idx, rank_idx in enumerate(ordem_visual):
            if rank_idx >= len(top3): continue
            row = top3.iloc[rank_idx]
            cfg = podio_configs[rank_idx]
            nc = "#007030" if row["pct_nigris"] >= 50 else "#a02020"

            tel_row = emp_area[emp_area["CNPJ_NORM"] == row["CNPJ_NORM"]].sort_values("Data emplacamento", ascending=False).iloc[0]
            tels = []
            for i in range(1,3):
                c = format_tel(tel_row.get(f"DDD_CELULAR{i}"), tel_row.get(f"CELULAR{i}"))
                cn = make_phone_number(tel_row.get(f"DDD_CELULAR{i}"), tel_row.get(f"CELULAR{i}"))
                if c: tels.append((c, cn))
            tel_btn = ""
            if tels:
                msg_p = "Olá! Entro em contato da Comercial De Nigris."
                tel_btn = f'<a href="https://wa.me/{tels[0][1]}?text={msg_p}" target="_blank" class="contact-btn btn-whatsapp" style="font-size:11px;padding:4px 10px;">💬 {tels[0][0]}</a>'

            with cols_podio[col_idx]:
                st.markdown(f"""
                <div style="background:{cfg['bg']};border:1px solid {cfg['borda']}99;border-top:4px solid {cfg['cor']};
                    border-radius:12px;padding:20px 16px;text-align:center;box-shadow:0 2px 10px rgba(0,0,0,0.06);">
                    <div style="font-size:28px;margin-bottom:3px;">{cfg['icon']}</div>
                    <div style="font-size:10px;text-transform:uppercase;letter-spacing:2px;color:{cfg['cor']};font-weight:700;">{cfg['label']}</div>
                    <div style="font-family:'Playfair Display',serif;font-size:13px;font-weight:700;color:#0a1628;margin:7px 0 3px 0;line-height:1.3;">
                        {str(row['NOMEPROPRIETARIO'])[:38]}{'...' if len(str(row['NOMEPROPRIETARIO'])) > 38 else ''}
                    </div>
                    <div style="font-size:11px;color:#6b7a99;margin-bottom:10px;">📍 {safe_str(row['NO_CIDADE'])}</div>
                    <div style="background:#f0f4fa;border-radius:8px;padding:8px;margin-bottom:7px;">
                        <div style="font-family:'Playfair Display',serif;font-size:24px;font-weight:700;color:{cfg['cor']};">{int(row['Total'])}</div>
                        <div style="font-size:10px;color:#8a95b0;text-transform:uppercase;">caminhões</div>
                    </div>
                    <div style="font-size:12px;color:{nc};font-weight:600;">{row['pct_nigris']}% De Nigris</div>
                    <div style="font-size:11px;color:#8a95b0;margin:3px 0;">{str(row['PrincipalMarca'])} · {str(row['UltimaCompra'])}</div>
                    {tel_btn}
                </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabela completa (top 30) ──
    st.markdown('<div class="section-title">📋 Ranking Completo da Área (Top 30)</div>', unsafe_allow_html=True)
    tabela = top_cli.head(30).copy()
    tabela["% De Nigris"] = tabela["pct_nigris"].astype(str) + "%"
    tabela = tabela.drop(columns=["CNPJ_NORM", "pct_nigris"])
    tabela.columns = ["Nome", "Cidade", "Total", "Última Compra", "Marca Principal", "Qtd De Nigris", "% De Nigris"]
    tabela.insert(0, "#", range(1, len(tabela) + 1))
    st.dataframe(tabela, use_container_width=True, hide_index=True)

    # ── Clientes inativos na área (alerta rápido) ──
    hoje = pd.Timestamp.now()
    ultima_emp = emp_area.groupby("CNPJ_NORM")["Data emplacamento"].max().reset_index()
    ultima_emp["MesesSem"] = ultima_emp["Data emplacamento"].apply(
        lambda x: relativedelta(hoje, x).years * 12 + relativedelta(hoje, x).months if pd.notna(x) else 999)
    inativos_area = ultima_emp[ultima_emp["MesesSem"] > 12]
    if not inativos_area.empty:
        st.markdown(f'<div class="alert-hot" style="margin-top:8px;">🚨 <strong>{len(inativos_area)} clientes</strong> da sua área estão há mais de 12 meses sem comprar · veja detalhes em <em>Oportunidades</em></div>', unsafe_allow_html=True)

    # ── Export ──
    buf = BytesIO()
    tabela.to_excel(buf, index=False, engine="openpyxl")
    buf.seek(0)
    st.download_button("📥 Exportar Ranking da Área (XLSX)", buf,
                       file_name=f"top_clientes_{sel_cons.replace(' ','_')}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ============================================================
# PÁGINA: PAINEL GERAL (gestor/gerente)
# ============================================================
elif pagina == "📊 Painel Geral":
    st.markdown("""
    <div class="page-header">
        <h1>Painel Geral</h1>
        <p>Visão consolidada · todos os anos</p>
    </div>""", unsafe_allow_html=True)

    if df_emp is None:
        st.warning("⚠️ Carregue os emplacamentos em Gerenciar Dados.")
        st.stop()

    anos_disp = sorted(df_emp["Ano"].unique(), reverse=True)
    anos_sel_p = st.multiselect("Filtrar por ano(s):", anos_disp, default=anos_disp)
    df_p = df_emp[df_emp["Ano"].isin(anos_sel_p)] if anos_sel_p else df_emp

    total_emp_p  = len(df_p)
    clientes_p   = df_p["CNPJ_NORM"].nunique()
    nigris_p     = int(is_denigris(df_p["Concessionário"]).sum())
    market_share = round(nigris_p/total_emp_p*100,1) if total_emp_p else 0

    k1,k2,k3,k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Emplacamentos</div><div class="kpi-value">{total_emp_p:,}</div></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Clientes Únicos</div><div class="kpi-value">{clientes_p:,}</div></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Vendidos De Nigris</div><div class="kpi-value" style="color:#007030;">{nigris_p}</div></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Market Share De Nigris</div><div class="kpi-value" style="color:#0044aa;">{market_share}%</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">📅 Emplacamentos por Ano</div>', unsafe_allow_html=True)
        ea = df_p.groupby("Ano").size().reset_index(name="Qtd")
        fig = go.Figure(go.Scatter(x=ea["Ano"].astype(str), y=ea["Qtd"],
            mode="lines+markers", line=dict(color="#0077cc",width=3),
            marker=dict(color="#00aaff",size=8), fill="tozeroy",
            fillcolor="rgba(10,22,40,0.07)"))
        fig.update_layout(plot_bgcolor="#ffffff",paper_bgcolor="#ffffff",
            font_color="#4a5568",height=260,
            xaxis=dict(showgrid=False),yaxis=dict(showgrid=True,gridcolor="#f0f2f7"),
            margin=dict(t=10,b=10,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">🚚 Market Share por Concessionária</div>', unsafe_allow_html=True)
        top_conc = df_p["Concessionário"].value_counts().head(8).reset_index()
        top_conc.columns = ["Concessionária","Qtd"]
        fig2 = go.Figure(go.Pie(labels=top_conc["Concessionária"],values=top_conc["Qtd"],hole=0.45,
            marker_colors=["#0a1628","#0077cc","#0099ee","#00bbff","#1a6688","#2a5577","#1a3355","#0a1a33"]))
        fig2.update_layout(plot_bgcolor="#ffffff",paper_bgcolor="#ffffff",
            font_color="#4a5568",height=260,margin=dict(t=10,b=10,l=10,r=10),
            legend=dict(font=dict(color="#4a5568",size=9)))
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-title">🏷️ Emplacamentos por Marca</div>', unsafe_allow_html=True)
        em = df_p["Marca"].value_counts().reset_index()
        em.columns = ["Marca","Qtd"]
        fig3 = go.Figure(go.Bar(x=em["Qtd"],y=em["Marca"],orientation="h",marker_color="#0a1628"))
        fig3.update_layout(plot_bgcolor="#ffffff",paper_bgcolor="#ffffff",
            font_color="#4a5568",height=300,
            xaxis=dict(showgrid=True,gridcolor="#f0f2f7"),yaxis=dict(showgrid=False),
            margin=dict(t=10,b=10,l=10,r=10))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-title">🗺️ Top Cidades</div>', unsafe_allow_html=True)
        cid = df_p["NO_CIDADE"].value_counts().head(10).reset_index()
        cid.columns = ["Cidade","Qtd"]
        fig4 = go.Figure(go.Bar(x=cid["Qtd"],y=cid["Cidade"],orientation="h",
            marker_color=["#4499ff" if "SAO PAULO" in c or "BERNARDO" in c else "#0a1628" for c in cid["Cidade"]]))
        fig4.update_layout(plot_bgcolor="#ffffff",paper_bgcolor="#ffffff",
            font_color="#4a5568",height=300,
            xaxis=dict(showgrid=True,gridcolor="#f0f2f7"),yaxis=dict(showgrid=False),
            margin=dict(t=10,b=10,l=10,r=10))
        st.plotly_chart(fig4, use_container_width=True)

    # Tabela emplacamentos por consultor (cruzando área operacional)
    if df_area is not None:
        st.markdown('<div class="section-title">👥 Emplacamentos por Consultor (Área Operacional)</div>', unsafe_allow_html=True)

        def get_cons(row):
            return get_consultor_por_cidade_bairro(
                norm_str(str(row.get("NO_CIDADE",""))),
                norm_str(str(row.get("NO_BAIRRO",""))),
                df_area
            ) or "Sem consultor"

        # Performance: fazer o merge via município
        munic_to_cons = df_area.groupby("Municipio_norm")["Consultor"].first().to_dict()
        df_p["Consultor"] = df_p["NO_CIDADE_NORM"].map(munic_to_cons).fillna("Sem consultor")
        cons_perf = df_p.groupby("Consultor").agg(
            Total=("Chassi","count"),
            DaNigris=("Concessionário", lambda x: is_denigris(x).sum()),
            Clientes=("CNPJ_NORM","nunique"),
        ).reset_index()
        cons_perf["% Nigris"] = (cons_perf["DaNigris"]/cons_perf["Total"]*100).round(1).astype(str)+"%"
        cons_perf = cons_perf.sort_values("Total",ascending=False)
        st.dataframe(cons_perf, use_container_width=True, hide_index=True)



# ============================================================
# PÁGINA: GESTÃO & PERFORMANCE (somente gestor/gerente)
# ============================================================
elif pagina == "📈 Gestão & Performance":
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#fff;">Gestão & Performance</div>
        <div style="font-size:13px;color:#3a5a7a;">Analise emplacamentos por período, consultor, marca e região</div>
    </div>""", unsafe_allow_html=True)

    if df_emp is None:
        st.warning("⚠️ Carregue ao menos um arquivo de emplacamentos.")
        st.stop()

    # ── FILTROS ──────────────────────────────────────────────
    st.markdown('<div class="section-title">🎛️ Filtros</div>', unsafe_allow_html=True)

    anos_disp  = sorted(df_emp["Ano"].unique(), reverse=True)
    meses_nomes = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
                   7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}
    meses_disp = sorted(df_emp["Mes"].dropna().unique().tolist())

    consultores_disp = ["Todos"]
    if df_area is not None:
        consultores_disp += sorted(df_area[df_area["Consultor"] != "ZONA LIVRE"]["Consultor"].str.title().unique().tolist())

    marcas_disp  = ["Todas"] + sorted(df_emp["Marca"].dropna().unique().tolist())
    cidades_disp = ["Todas"] + sorted(df_emp["NO_CIDADE"].dropna().unique().tolist())

    f1, f2, f3 = st.columns(3)
    with f1:
        sel_anos = st.multiselect("📅 Ano(s)", anos_disp, default=anos_disp)
    with f2:
        sel_meses_label = st.multiselect("🗓️ Mês(es)", options=list(meses_nomes.values()),
                                          default=list(meses_nomes.values()))
        sel_meses = [k for k,v in meses_nomes.items() if v in sel_meses_label]
    with f3:
        sel_consultor = st.selectbox("👤 Consultor", consultores_disp)

    f4, f5 = st.columns(2)
    with f4:
        sel_marca = st.selectbox("🏷️ Marca", marcas_disp)
    with f5:
        sel_cidade = st.selectbox("📍 Cidade", cidades_disp)

    # ── APLICAR FILTROS ──────────────────────────────────────
    df_g = df_emp.copy()
    if sel_anos:
        df_g = df_g[df_g["Ano"].isin(sel_anos)]
    if sel_meses:
        df_g = df_g[df_g["Mes"].isin(sel_meses)]
    if sel_consultor != "Todos" and df_area is not None:
        munic_to_cons = df_area.groupby("Municipio_norm")["Consultor"].first().to_dict()
        df_g["_cons"] = df_g["NO_CIDADE_NORM"].map(munic_to_cons).fillna("").str.title()
        df_g = df_g[df_g["_cons"] == sel_consultor]
    if sel_marca != "Todas":
        df_g = df_g[df_g["Marca"] == sel_marca]
    if sel_cidade != "Todas":
        df_g = df_g[df_g["NO_CIDADE"] == sel_cidade]

    if df_g.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
        st.stop()

    # ── KPIs DOS FILTROS ─────────────────────────────────────
    total_f       = len(df_g)
    clientes_f    = df_g["CNPJ_NORM"].nunique()
    nigris_f      = int(is_denigris(df_g["Concessionário"]).sum())
    concorrente_f = total_f - nigris_f
    ms_f          = round(nigris_f / total_f * 100, 1) if total_f else 0

    st.markdown('<div class="section-title">📊 Resultado do Período Filtrado</div>', unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Emplacamentos</div><div class="kpi-value">{total_f:,}</div></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Clientes Únicos</div><div class="kpi-value">{clientes_f}</div></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">De Nigris</div><div class="kpi-value" style="color:#007030;">{nigris_f}</div></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Concorrente</div><div class="kpi-value" style="color:#a02020;">{concorrente_f}</div></div>', unsafe_allow_html=True)
    with k5: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Market Share</div><div class="kpi-value" style="color:#0044aa;">{ms_f}%</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── DESEMPENHO POR CONSULTOR ─────────────────────────────
    if df_area is not None:
        st.markdown('<div class="section-title">👥 Desempenho por Consultor</div>', unsafe_allow_html=True)

        munic_to_cons = df_area.groupby("Municipio_norm")["Consultor"].first().to_dict()
        df_g["Consultor"] = df_g["NO_CIDADE_NORM"].map(munic_to_cons).fillna("Sem consultor").str.title()

        perf = df_g.groupby("Consultor").agg(
            Total=("Chassi", "count"),
            De_Nigris=("Concessionário", lambda x: is_denigris(x).sum()),
            Concorrente=("Concessionário", lambda x: (~is_denigris(x)).sum()),
            Clientes=("CNPJ_NORM", "nunique"),
            Marcas=("Marca", lambda x: x.mode()[0] if not x.empty else "—"),
        ).reset_index()
        perf["% De Nigris"] = (perf["De_Nigris"] / perf["Total"] * 100).round(1)
        perf = perf.sort_values("Total", ascending=False)

        # Gráfico de barras empilhadas
        fig_cons = go.Figure()
        fig_cons.add_trace(go.Bar(
            name="De Nigris", x=perf["Consultor"], y=perf["De_Nigris"],
            marker_color="#0a1628", text=perf["De_Nigris"], textposition="inside",
        ))
        fig_cons.add_trace(go.Bar(
            name="Concorrente", x=perf["Consultor"], y=perf["Concorrente"],
            marker_color="#cc4444", text=perf["Concorrente"], textposition="inside",
        ))
        fig_cons.update_layout(
            barmode="stack", plot_bgcolor="#0a0c10", paper_bgcolor="#0a0c10",
            font_color="#4a5568", height=340, legend=dict(font=dict(color="#8899bb")),
            xaxis=dict(showgrid=False, tickangle=-30),
            yaxis=dict(showgrid=True, gridcolor="#f0f2f7"),
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_cons, use_container_width=True)

        # Tabela detalhada por consultor
        perf["% De Nigris"] = perf["% De Nigris"].astype(str) + "%"
        perf.columns = ["Consultor", "Total", "De Nigris", "Concorrente", "Clientes Únicos", "Marca Mais Freq.", "% De Nigris"]
        st.dataframe(perf, use_container_width=True, hide_index=True)

    # ── EVOLUÇÃO MENSAL ──────────────────────────────────────
    st.markdown('<div class="section-title">📅 Evolução Mensal</div>', unsafe_allow_html=True)

    df_g["AnoMes"] = df_g["Ano"].astype(str) + "-" + df_g["Mes"].astype(str).str.zfill(2)
    evol = df_g.groupby("AnoMes").agg(
        Total=("Chassi","count"),
        De_Nigris=("Concessionário", lambda x: is_denigris(x).sum()),
    ).reset_index().sort_values("AnoMes")
    evol["Concorrente"] = evol["Total"] - evol["De_Nigris"]

    fig_evol = go.Figure()
    fig_evol.add_trace(go.Scatter(
        x=evol["AnoMes"], y=evol["De_Nigris"], name="De Nigris",
        mode="lines+markers", line=dict(color="#0077cc", width=3),
        marker=dict(size=7), fill="tozeroy", fillcolor="rgba(0,85,164,0.12)"
    ))
    fig_evol.add_trace(go.Scatter(
        x=evol["AnoMes"], y=evol["Concorrente"], name="Concorrente",
        mode="lines+markers", line=dict(color="#cc4444", width=2, dash="dot"),
        marker=dict(size=6),
    ))
    fig_evol.update_layout(
        plot_bgcolor="#0a0c10", paper_bgcolor="#0a0c10",
        font_color="#4a5568", height=300,
        xaxis=dict(showgrid=False, tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor="#f0f2f7"),
        legend=dict(font=dict(color="#8899bb")),
        margin=dict(t=10, b=10, l=10, r=10)
    )
    st.plotly_chart(fig_evol, use_container_width=True)

    # ── RANKING DE MARCAS ────────────────────────────────────
    col_m, col_c = st.columns(2)
    with col_m:
        st.markdown('<div class="section-title">🏷️ Ranking de Marcas</div>', unsafe_allow_html=True)
        marcas_rank = df_g.groupby("Marca").agg(
            Total=("Chassi","count"),
            De_Nigris=("Concessionário", lambda x: is_denigris(x).sum()),
        ).reset_index().sort_values("Total", ascending=False)
        marcas_rank["% De Nigris"] = (marcas_rank["De_Nigris"] / marcas_rank["Total"] * 100).round(1).astype(str) + "%"
        fig_m = go.Figure(go.Bar(
            x=marcas_rank["Total"], y=marcas_rank["Marca"],
            orientation="h", marker_color="#0a1628",
            text=marcas_rank["Total"], textposition="outside"
        ))
        fig_m.update_layout(plot_bgcolor="#0a0c10", paper_bgcolor="#0a0c10",
            font_color="#4a5568", height=300,
            xaxis=dict(showgrid=True, gridcolor="#f0f2f7"),
            yaxis=dict(showgrid=False),
            margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_m, use_container_width=True)

    with col_c:
        st.markdown('<div class="section-title">🏢 Top Concessionárias Concorrentes</div>', unsafe_allow_html=True)
        conc_rank = df_g[~is_denigris(df_g["Concessionário"])]["Concessionário"].value_counts().head(8).reset_index()
        conc_rank.columns = ["Concessionária", "Qtd"]
        # Abreviar nomes longos
        conc_rank["Conc. (abrev.)"] = conc_rank["Concessionária"].str[:35] + "..."
        fig_c = go.Figure(go.Bar(
            x=conc_rank["Qtd"], y=conc_rank["Conc. (abrev.)"],
            orientation="h", marker_color="#cc4444",
            text=conc_rank["Qtd"], textposition="outside"
        ))
        fig_c.update_layout(plot_bgcolor="#0a0c10", paper_bgcolor="#0a0c10",
            font_color="#4a5568", height=300,
            xaxis=dict(showgrid=True, gridcolor="#f0f2f7"),
            yaxis=dict(showgrid=False),
            margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_c, use_container_width=True)

    # ── TOP CLIENTES NO PERÍODO ──────────────────────────────
    st.markdown('<div class="section-title">🏆 Top Clientes no Período Filtrado</div>', unsafe_allow_html=True)
    top_per = df_g.groupby(["CNPJ_NORM","NOMEPROPRIETARIO","NO_CIDADE"]).agg(
        Total=("Chassi","count"),
        De_Nigris=("Concessionário", lambda x: is_denigris(x).sum()),
        UltimaCompra=("Data emplacamento","max"),
        Marca=("Marca", lambda x: x.mode()[0] if not x.empty else "—"),
    ).reset_index().sort_values("Total", ascending=False).head(20)
    top_per["% De Nigris"] = (top_per["De_Nigris"] / top_per["Total"] * 100).round(0).astype(int).astype(str) + "%"
    top_per["UltimaCompra"] = pd.to_datetime(top_per["UltimaCompra"]).dt.strftime("%d/%m/%Y")
    top_per = top_per.drop(columns=["CNPJ_NORM"])
    top_per.insert(0, "#", range(1, len(top_per)+1))
    top_per.columns = ["#","Nome","Cidade","Total","De Nigris","Última Compra","Marca","% De Nigris"]
    st.dataframe(top_per, use_container_width=True, hide_index=True)

    # ── EXPORTAR TUDO ────────────────────────────────────────
    st.markdown('<div class="section-title">📥 Exportar</div>', unsafe_allow_html=True)
    ex1, ex2, ex3 = st.columns(3)

    with ex1:
        buf = BytesIO()
        top_per.to_excel(buf, index=False, engine="openpyxl")
        buf.seek(0)
        st.download_button("📋 Top Clientes", buf, file_name="top_clientes_periodo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with ex2:
        if df_area is not None:
            buf2 = BytesIO()
            perf.to_excel(buf2, index=False, engine="openpyxl")
            buf2.seek(0)
            st.download_button("👥 Desempenho Consultores", buf2, file_name="desempenho_consultores.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with ex3:
        buf3 = BytesIO()
        df_g[["Data emplacamento","Placa","Chassi","NOMEPROPRIETARIO","NO_CIDADE",
              "Marca","Modelo","Concessionário"]].to_excel(buf3, index=False, engine="openpyxl")
        buf3.seek(0)
        st.download_button("📄 Base Completa Filtrada", buf3, file_name="base_filtrada.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ============================================================
# PÁGINA: OPORTUNIDADES
# ============================================================
elif pagina == "🎯 Oportunidades":
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#fff;">Central de Oportunidades</div>
        <div style="font-size:13px;color:#3a5a7a;">Reativação · Prospects quentes · Clientes no concorrente</div>
    </div>""", unsafe_allow_html=True)

    if df_emp is None:
        st.warning("⚠️ Carregue ao menos um arquivo de emplacamentos.")
        st.stop()

    today = pd.Timestamp.now()
    ano_atual = today.year

    # Filtrar por consultor se não for gestor
    df_opp = df_emp.copy()
    if perfil_atual == "vendedor" and df_area is not None:
        area_row = df_area[df_area["Consultor"] == consultor_key]
        munic_meu = area_row["Municipio_norm"].unique()
        df_opp = df_emp[df_emp["NO_CIDADE_NORM"].isin(munic_meu)].copy()
        st.info(f"📍 Exibindo oportunidades da sua área: **{consultor_key.title()}**")

    tab1, tab2, tab3 = st.tabs(["🔴 Inativos (+12 meses)", "🔥 Próxima Compra < 90 dias", "⚠️ Compraram do Concorrente"])

    with tab1:
        ultima = df_opp.groupby("CNPJ_NORM")["Data emplacamento"].max().reset_index()
        ultima.columns = ["CNPJ_NORM","UltimaCompra"]
        total_comp = df_opp.groupby("CNPJ_NORM").size().reset_index(name="TotalCompras")
        info_c = df_opp.groupby("CNPJ_NORM").agg(
            Nome=("NOMEPROPRIETARIO","first"),
            CNPJ=("CPFCNPJPROPRIETARIO","first"),
            Cidade=("NO_CIDADE","first"),
        ).reset_index()
        df_in = ultima.merge(total_comp,on="CNPJ_NORM").merge(info_c,on="CNPJ_NORM")
        df_in = df_in[df_in["UltimaCompra"].notna()]
        df_in["MesesSemCompra"] = df_in["UltimaCompra"].apply(
            lambda x: relativedelta(today,x).years*12 + relativedelta(today,x).months)
        df_in = df_in[(df_in["UltimaCompra"].dt.year < ano_atual) & (df_in["MesesSemCompra"] > 12)].copy()

        if df_cart is not None:
            vm = df_cart.set_index("CNPJ_NORM")["VENDEDOR"].to_dict()
            df_in["Vendedor"] = df_in["CNPJ_NORM"].map(vm).fillna("Sem responsável")
        if df_area is not None:
            mc = df_area.groupby("Municipio_norm")["Consultor"].first().to_dict()
            df_in["Consultor Área"] = df_in["Cidade"].apply(norm_str).map(mc).fillna("—")

        df_in = df_in.sort_values("MesesSemCompra", ascending=False)
        df_in["UltimaCompra"] = df_in["UltimaCompra"].dt.strftime("%d/%m/%Y")

        st.markdown(f'<div class="alert-hot" style="margin-bottom:16px;">🚨 <strong>{len(df_in)} clientes</strong> há mais de 12 meses sem comprar</div>', unsafe_allow_html=True)
        cols_in = ["Nome","CNPJ","Cidade","UltimaCompra","TotalCompras","MesesSemCompra"]
        if "Vendedor" in df_in.columns: cols_in.append("Vendedor")
        if "Consultor Área" in df_in.columns: cols_in.append("Consultor Área")
        st.dataframe(df_in[[c for c in cols_in if c in df_in.columns]], use_container_width=True, hide_index=True)

        buf = BytesIO()
        df_in.to_excel(buf, index=False, engine="openpyxl")
        buf.seek(0)
        st.download_button("📥 Exportar Inativos (XLSX)", buf, file_name="clientes_inativos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with tab2:
        quentes = []
        for cnpj, grp in df_opp.groupby("CNPJ_NORM"):
            datas = grp["Data emplacamento"].dropna().tolist()
            if len(datas) >= 2:
                plabel, pdate = calc_prediction(datas)
                if pdate:
                    d = relativedelta(pdate, today)
                    meses = d.years*12 + d.months
                    if -1 <= meses <= 3:
                        row = grp.sort_values("Data emplacamento",ascending=False).iloc[0]
                        vend = "—"
                        if df_cart is not None:
                            vm2 = df_cart[df_cart["CNPJ_NORM"]==cnpj]
                            if not vm2.empty: vend = vm2.iloc[0]["VENDEDOR"]
                        quentes.append({
                            "Nome": row["NOMEPROPRIETARIO"],
                            "CNPJ": row["CPFCNPJPROPRIETARIO"],
                            "Cidade": row["NO_CIDADE"],
                            "Previsão": plabel,
                            "Meses até compra": meses,
                            "Total emplacamentos": len(grp),
                            "Vendedor/Consultor": vend,
                        })
        if quentes:
            df_q = pd.DataFrame(quentes).sort_values("Meses até compra")
            st.markdown(f'<div class="alert-warm" style="margin-bottom:16px;">🔥 <strong>{len(df_q)} clientes</strong> com previsão de compra nos próximos 90 dias</div>', unsafe_allow_html=True)
            st.dataframe(df_q, use_container_width=True, hide_index=True)
            buf = BytesIO()
            df_q.to_excel(buf, index=False, engine="openpyxl")
            buf.seek(0)
            st.download_button("📥 Exportar Prospects (XLSX)", buf, file_name="prospects_quentes.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("Nenhum prospect quente identificado no momento.")

    with tab3:
        conc_df = df_opp[~is_denigris(df_opp["Concessionário"])].copy()
        if df_area is not None:
            mc2 = df_area.groupby("Municipio_norm")["Consultor"].first().to_dict()
            conc_df["Consultor Área"] = conc_df["NO_CIDADE_NORM"].map(mc2).fillna("—")

        conc_sum = conc_df.groupby(["CNPJ_NORM","NOMEPROPRIETARIO","NO_CIDADE"]).agg(
            ComprasConcorrente=("Chassi","count"),
            UltimaConcorrente=("Data emplacamento","max"),
            PrincipalConcorrente=("Concessionário", lambda x: x.mode()[0] if not x.empty else "—"),
            ConsultorArea=("Consultor Área","first") if "Consultor Área" in conc_df.columns else ("NO_CIDADE","first"),
        ).reset_index().sort_values("ComprasConcorrente",ascending=False)
        conc_sum["UltimaConcorrente"] = pd.to_datetime(conc_sum["UltimaConcorrente"]).dt.strftime("%d/%m/%Y")
        conc_sum = conc_sum.drop(columns=["CNPJ_NORM"])

        st.markdown(f'<div class="alert-hot" style="margin-bottom:16px;">⚠️ <strong>{len(conc_sum)} clientes</strong> emplacaram em concorrentes</div>', unsafe_allow_html=True)
        st.dataframe(conc_sum, use_container_width=True, hide_index=True)

        buf = BytesIO()
        conc_sum.to_excel(buf, index=False, engine="openpyxl")
        buf.seek(0)
        st.download_button("📥 Exportar Concorrente (XLSX)", buf, file_name="clientes_concorrente.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ============================================================
# PÁGINA: GERENCIAR DADOS (gestor/gerente)
# ============================================================
elif pagina == "⚙️ Gerenciar Dados":
    st.markdown("""
    <div class="page-header">
        <h1>Gerenciar Dados</h1>
        <p>Atualização de planilhas · Área operacional · Carteira · Emplacamentos</p>
    </div>""", unsafe_allow_html=True)

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        s_area = f"✅ {len(df_area)} regiões" if df_area is not None else "⚠️ Não carregada"
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Área Operacional</div><div class="kpi-value" style="font-size:18px;">{s_area}</div></div>', unsafe_allow_html=True)
    with col_s2:
        s_cart = f"✅ {len(df_cart)} clientes" if df_cart is not None else "⚠️ Não carregada"
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Carteira</div><div class="kpi-value" style="font-size:18px;">{s_cart}</div></div>', unsafe_allow_html=True)
    with col_s3:
        if df_emp is not None:
            anos_emp = sorted(df_emp["Ano"].unique())
            s_emp = f"✅ {len(df_emp):,} registros ({anos_emp[0]}–{anos_emp[-1]})"
        else:
            s_emp = "⚠️ Não carregados"
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Emplacamentos</div><div class="kpi-value" style="font-size:14px;">{s_emp}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_u1, col_u2 = st.columns(2)
    with col_u1:
        st.markdown('<div class="upload-section"><div class="upload-title">🗂️ Área Operacional</div><div style="font-size:12px;color:#6b7a99;margin-bottom:12px;">Substitui o mapa de regiões e consultores</div>', unsafe_allow_html=True)
        up_area = st.file_uploader("Arquivo de Área (.xlsx)", type=["xlsx"], key="up_area")
        if up_area:
            novo_area = load_area_operacional(BytesIO(up_area.getvalue()))
            st.session_state.df_area = novo_area
            USUARIOS = build_usuarios()
            st.success("✅ Área operacional atualizada!")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="upload-section" style="margin-top:14px;"><div class="upload-title">📋 Carteira de Clientes</div><div style="font-size:12px;color:#6b7a99;margin-bottom:12px;">Atualiza responsáveis e classificação</div>', unsafe_allow_html=True)
        up_cart = st.file_uploader("Nova Carteira (.xlsx)", type=["xlsx"], key="up_cart")
        if up_cart:
            st.session_state.df_cart = load_carteira(BytesIO(up_cart.getvalue()))
            st.success("✅ Carteira atualizada!")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_u2:
        st.markdown('<div class="upload-section"><div class="upload-title">🚚 Emplacamentos (Mensal)</div><div style="font-size:12px;color:#6b7a99;margin-bottom:12px;">Adicione arquivos mensais (2022+) — dados acumulados automaticamente</div>', unsafe_allow_html=True)
        up_emps = st.file_uploader("Selecione os arquivos (.xlsx)", type=["xlsx"],
                                   key="up_emp_multi", accept_multiple_files=True)
        if up_emps:
            novos = 0
            for f in up_emps:
                if f.name not in st.session_state.emp_fontes:
                    df_novo = load_emplacamentos_file(BytesIO(f.getvalue()), label=f.name)
                    st.session_state.df_emp_list.append(df_novo)
                    st.session_state.emp_fontes.append(f.name)
                    novos += 1
            if novos:
                st.success(f"✅ {novos} arquivo(s) adicionado(s)!")
            else:
                st.info("Arquivos já carregados.")
        if st.session_state.emp_fontes:
            st.markdown("**Arquivos carregados:**")
            for f in st.session_state.emp_fontes:
                st.markdown(f"- `{f}`")
            if st.button("🗑️ Limpar todos os emplacamentos", key="limpar_emp"):
                st.session_state.df_emp_list = []
                st.session_state.emp_fontes  = []
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


st.markdown('</div>', unsafe_allow_html=True)  # fecha page-content
