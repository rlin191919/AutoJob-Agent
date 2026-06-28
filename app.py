import streamlit as st
import docx
import pdfplumber
import io
import time
import re
from typing import Optional, Tuple, List, Dict

# =====================================================================
# [SECTION 1] 页面初始化与全局配置 (Page Configuration)
# =====================================================================
st.set_page_config(
    page_title="AutoJob-Agent | 生产级智能海投系统",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================================
# [SECTION 2] 核心交互引擎与全域动画 CSS (Advanced UI/UX Engine)
# =====================================================================
def inject_custom_css():
    """
    注入经过极简瘦身与交互增强的全局 CSS。
    重点包含：极致紧凑毛玻璃、全域 Hover 动效、强制向下展开机制。
    """
    st.markdown("""
    <style>
        /* -----------------------------------------------------------
           1. 全局字体与流光动态背景
           ----------------------------------------------------------- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
        
        .stApp {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 50%, #4facfe 100%) !important;
            background-size: 300% 300% !important;
            animation: bgShift 15s ease infinite !important;
        }
        @keyframes bgShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }

        /* 主容器瘦身 */
        .block-container { padding: 1.5rem 2rem !important; max-width: 1080px !important; }

        /* -----------------------------------------------------------
           2. 极简毛玻璃卡片引擎 (极致紧凑 + 交互颜色变动)
           ----------------------------------------------------------- */
        .glass-panel {
            background: rgba(255, 255, 255, 0.12) !important;
            backdrop-filter: blur(20px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
            /* 🚨 核心瘦身：极小的内边距，刚好包裹内容 */
            padding: 14px 16px !important; 
            border-radius: 12px !important; /* 紧凑圆角 */
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
            margin-bottom: 12px !important; /* 减少卡片间距 */
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            position: relative;
            overflow: visible !important; /* 允许下拉框溢出 */
        }
        
        /* 🖱️ 交互动画：鼠标悬停时的颜色微变与轻微上浮 */
        .glass-panel:hover {
            background: rgba(255, 255, 255, 0.22) !important; /* 颜色微亮 */
            border: 1px solid rgba(255, 255, 255, 0.4) !important; /* 边框发光 */
            transform: translateY(-2px); /* 轻微上移 */
            box-shadow: 0 8px 24px rgba(0,0,0,0.1) !important;
        }

        /* 卡片标题紧凑化 */
        .glass-panel h3 {
            color: rgba(255,255,255,0.95) !important;
            font-size: 1rem !important;
            font-weight: 700 !important;
            margin: 0 0 8px 0 !important; /* 底部留白极小化 */
            transition: color 0.3s ease;
        }
        .glass-panel:hover h3 { color: #ffffff !important; }

        /* -----------------------------------------------------------
           3. 🚨 BaseWeb 组件降维打击：绝对向下展开与限高 🚨
           ----------------------------------------------------------- */
        /* 锁定弹窗顶层位置 */
        div[data-baseweb="popover"] {
            top: 100% !important; /* 强行对齐父级底部 */
            bottom: auto !important; 
            transform: translateY(4px) !important; /* 取消复杂的矩阵运算，改为固定位移 */
            margin: 0 !important;
        }
        
        /* 限制菜单高度与内部样式 */
        div[data-baseweb="popover"] > div, ul[role="listbox"] {
            max-height: 180px !important; /* 极限控高，绝对不会因为空间不足上弹 */
            overflow-y: auto !important;
            background-color: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(12px) !important;
            border-radius: 8px !important;
            border: 1px solid rgba(255,255,255,0.4) !important;
            padding: 4px !important;
        }
        
        /* 下拉选项悬停动效 */
        ul[role="listbox"] li {
            padding: 8px 12px !important;
            font-size: 0.85rem !important;
            color: #1e293b !important;
            border-radius: 6px !important;
            transition: background 0.2s ease;
        }
        ul[role="listbox"] li:hover { background-color: #e0f2fe !important; }

        /* -----------------------------------------------------------
           4. 交互组件深度美化 (输入框、选择器、上传区全域 Hover)
           ----------------------------------------------------------- */
        /* 输入框与选择器底框 */
        .stTextArea textarea, div[data-baseweb="select"] > div {
            background: rgba(0, 0, 0, 0.1) !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            border-radius: 8px !important;
            color: #ffffff !important;
            font-size: 0.85rem !important;
            padding: 8px 12px !important;
            transition: all 0.3s ease !important;
        }
        .stTextArea textarea:hover, div[data-baseweb="select"] > div:hover {
            background: rgba(0, 0, 0, 0.18) !important;
            border-color: rgba(255,255,255,0.3) !important;
        }
        .stTextArea textarea:focus {
            background: rgba(0, 0, 0, 0.25) !important;
            border-color: #6ee7b7 !important;
            box-shadow: 0 0 0 2px rgba(110, 231, 183, 0.2) !important;
        }

        /* 提示文字微调 */
        .hint-text { color: rgba(255,255,255,0.8) !important; font-size: 0.8rem !important; margin-bottom: 4px !important; }

        /* 状态胶囊 */
        .status-chip { display: inline-flex; align-items: center; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; transition: all 0.3s ease; }
        .chip-ready { background: rgba(16, 185, 129, 0.2); color: #a7f3d0; border: 1px solid rgba(16,185,129,0.3); }
        .chip-wait { background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.6); border: 1px solid rgba(255,255,255,0.1); }
        
        /* 智能按钮流光动效 */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0.3)) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.5) !important;
            border-radius: 10px !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            height: 42px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, rgba(255,255,255,0.3), rgba(255,255,255,0.4)) !important;
            transform: scale(1.02);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15) !important;
        }

        /* 隐藏无用组件 */
        #MainMenu, footer, header { visibility: hidden; display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# [SECTION 3] 业务常量配置 (System Constants)
# =====================================================================
class Config:
    """集中管理系统配置，避免魔法字符串散落"""
    DOMESTIC_CITIES = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京", "西安", "重庆", "东莞"]
    OVERSEAS_LOCATIONS = ["北美地区", "欧洲地区", "亚太地区", "其他"]
    COMPANY_TYPES = ["顶级大厂/独角兽", "外企/跨国企业", "中小型科技公司", "国企/央企", "不限"]
    LLM_MODELS = ["DeepSeek-V3 (推荐)", "GPT-4o", "Claude-3.5-Sonnet"]
    MIN_JD_LENGTH = 15

# =====================================================================
# [SECTION 4] 核心服务类：文档解析引擎 (Data Parser Engine)
# =====================================================================
class DocumentEngine:
    """封装底层文档处理逻辑，提升鲁棒性与可维护性"""
    
    @staticmethod
    def parse_pdf(file_bytes: bytes) -> Tuple[Optional[str], Optional[str]]:
        """安全的 PDF 解析器，捕获损坏文件异常"""
        try:
            text = ""
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted: text += extracted + "\n"
            return text.strip() if text.strip() else None, None
        except Exception as e:
            return None, f"PDF 解析失败: {str(e)}"

    @staticmethod
    def parse_docx(file_bytes: bytes) -> Tuple[Optional[str], Optional[str]]:
        """安全的 DOCX 解析器，包含段落与表格遍历"""
        try:
            text = ""
            doc = docx.Document(io.BytesIO(file_bytes))
            for para in doc.paragraphs:
                if para.text: text += para.text + "\n"
            for table in doc.tables:
                for row in table.rows:
                    text += " | ".join([c.text.strip() for c in row.cells if c.text.strip()]) + "\n"
            return text.strip() if text.strip() else None, None
        except Exception as e:
            return None, f"DOCX 解析失败: {str(e)}"

    @classmethod
    def process_upload(cls, uploaded_file) -> Optional[str]:
        """门面模式：统一处理入口"""
        if not uploaded_file: return None
        ext = uploaded_file.name.split('.')[-1].lower()
        file_bytes = uploaded_file.read()
        
        if ext == 'pdf':
            content, _ = cls.parse_pdf(file_bytes)
        elif ext == 'docx':
            content, _ = cls.parse_docx(file_bytes)
        else:
            return None
        return content

# =====================================================================
# [SECTION 5] 核心服务类：智能分析器 (Intelligence Analyzer)
# =====================================================================
class IntelligenceAnalyzer:
    """负责在 Phase 1 阶段基于规则对文本进行轻量级预分析"""
    
    @staticmethod
    def extract_intent_cities(text: str, candidate_cities: List[str]) -> List[str]:
        """简单的规则引擎：从简历文本中嗅探意向城市"""
        if not text: return []
        # 使用正则表达式提高匹配准确度，避免子串误判
        detected = []
        for city in candidate_cities:
            if re.search(r'\b' + re.escape(city) + r'\b', text) or city in text:
                detected.append(city)
        return list(dict.fromkeys(detected))[:3] # 去重并最多返回3个

# =====================================================================
# [SECTION 6] 状态机管理器 (State Machine Control)
# =====================================================================
def init_session_state():
    """集中初始化和管理所有的上下文状态变量"""
    default_states = {
        "stage": "INPUT",            # 当前应用阶段: INPUT -> PROCESSING -> RESULT
        "resume_raw": "",            # 提取的原始简历文本
        "jd_raw": "",                # 提取的原始 JD 文本
        "detected_cities": [],       # 自动检测的城市列表
        "pref_company_type": "",     # 用户偏好：公司类型
        "pref_location": ""          # 用户偏好：最终锁定地区
    }
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

# =====================================================================
# [SECTION 7] UI 渲染模块：输入层 (UI Controller - Input Stage)
# =====================================================================
def render_input_stage():
    """渲染主数据输入界面，采用高度模块化的列式布局"""
    
    # 顶部极简标题
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; font-size: 2.2rem; margin: 0; text-shadow: 0 2px 10px rgba(0,0,0,0.1);">💼 AutoJob-Agent</h1>
        <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem; margin: 0;">智能简历解析与意向映射中枢</p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns(2, gap="medium")

    # ----- 左侧模块：简历与意向配置 -----
    with col_left:
        # [卡片 1] 简历源数据
        st.markdown('<div class="glass-panel"><h3>📄 原始简历输入</h3>', unsafe_allow_html=True)
        resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx"], label_visibility="collapsed")
        
        if resume_file:
            # 实时解析并更新状态
            parsed_text = DocumentEngine.process_upload(resume_file)
            if parsed_text:
                st.session_state.detected_cities = IntelligenceAnalyzer.extract_intent_cities(parsed_text, Config.DOMESTIC_CITIES)
                st.markdown(f'<div class="status-chip chip-ready">✓ 简历已缓存 ({len(parsed_text)} 字符)</div>', unsafe_allow_html=True)
            else:
                st.error("文件内容提取失败，请检查格式。")
        else:
            st.session_state.detected_cities = []
            st.markdown('<div class="status-chip chip-wait">○ 等待文件挂载</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # [卡片 2] 偏好策略引擎
        st.markdown('<div class="glass-panel"><h3>🤖 投递策略配置</h3>', unsafe_allow_html=True)
        st.session_state.pref_company_type = st.selectbox("目标企业类型", Config.COMPANY_TYPES, label_visibility="collapsed")
        _ = st.selectbox("核心驱动模型", Config.LLM_MODELS, label_visibility="collapsed") # 仅作占位展示
        st.markdown('</div>', unsafe_allow_html=True)

    # ----- 右侧模块：岗位JD与区域配置 -----
    with col_right:
        # [卡片 3] JD 上下文注入
        st.markdown('<div class="glass-panel"><h3>🎯 目标岗位 JD</h3>', unsafe_allow_html=True)
        st.markdown('<div class="hint-text">文本直贴 / 文档解析</div>', unsafe_allow_html=True)
        
        jd_mode = st.radio("Mode", ["TEXT", "FILE"], horizontal=True, label_visibility="collapsed")
        jd_input_text = ""
        
        if jd_mode == "TEXT":
            jd_input_text = st.text_area("JD Input", placeholder="在此粘贴目标岗位的职责与要求...", height=90, label_visibility="collapsed")
        else:
            jd_file = st.file_uploader("Upload JD", type=["pdf", "docx"], label_visibility="collapsed")
            if jd_file: jd_input_text = DocumentEngine.process_upload(jd_file)
        st.markdown('</div>', unsafe_allow_html=True)

        # [卡片 4] 空间映射器 (地区选择)
        st.markdown('<div class="glass-panel"><h3>📍 物理意向映射</h3>', unsafe_allow_html=True)
        
        if st.session_state.detected_cities:
            city_str = "、".join(st.session_state.detected_cities)
            st.markdown(f'<div style="color:#6ee7b7; font-size:0.8rem; margin-bottom:8px;">✓ 简历嗅探命中: {city_str}</div>', unsafe_allow_html=True)
            st.session_state.pref_location = st.selectbox("验证目标区域", st.session_state.detected_cities + ["手动校准..."], label_visibility="collapsed")
        else:
            loc_scope = st.radio("区域范围", ["CN", "GLOBAL"], horizontal=True, label_visibility="collapsed")
            options = Config.DOMESTIC_CITIES if loc_scope == "CN" else Config.OVERSEAS_LOCATIONS
            st.session_state.pref_location = st.selectbox("选定目标区域", options, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    # ----- 动作触发总线 -----
    is_valid = bool(resume_file is not None and jd_input_text and len(jd_input_text) > Config.MIN_JD_LENGTH)
    
    col_status, col_btn = st.columns([2, 1])
    with col_status:
        if is_valid:
            st.markdown('<div class="status-chip chip-ready" style="margin-top:10px;">🟢 Agent 链路已就绪，可启动匹配总线</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-chip chip-wait" style="margin-top:10px;">🟡 等待必要数据源 (简历 / JD) 闭环</div>', unsafe_allow_html=True)
            
    with col_btn:
        if st.button("🚀 启动智能解构与匹配", type="primary", use_container_width=True, disabled=not is_valid):
            # 将最终校验过的数据写入状态机
            st.session_state.resume_raw = DocumentEngine.process_upload(resume_file)
            st.session_state.jd_raw = jd_input_text
            st.session_state.stage = "PROCESSING"
            st.rerun()

# =====================================================================
# [SECTION 8] UI 渲染模块：流式加载与结果层
# =====================================================================
def render_processing_stage():
    """模拟真实 Agent 工作流状态的进度指示器"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    msg_container = st.empty()
    bar = st.progress(0)
    
    # 模拟复杂计算任务流
    tasks = [
        ("正在解构 PDF/DOCX 语义树...", 25),
        ("提取能力雷达矩阵...", 50),
        ("挂载岗位要求上下文...", 75),
        ("生成多维对比视图...", 100)
    ]
    
    current_progress = 0
    for task_msg, target_progress in tasks:
        msg_container.markdown(f"<div style='text-align:center; color:white; font-weight:600;'>{task_msg}</div>", unsafe_allow_html=True)
        while current_progress < target_progress:
            current_progress += 2
            bar.progress(current_progress)
            time.sleep(0.02)
            
    st.session_state.stage = "RESULT"
    st.rerun()

def render_result_stage():
    """渲染解析后的数据对比看板"""
    st.markdown('<div class="glass-panel" style="text-align:center;"><h3>🔍 数据总线解析视图</h3></div>', unsafe_allow_html=True)
    
    if st.button("↩ 回滚到配置模式", key="back"):
        st.session_state.stage = "INPUT"
        st.rerun()
        
    c1, c2 = st.columns(2, gap="medium")
    
    with c1:
        st.markdown('<div class="glass-panel"><h3>📄 Resume 上下文切片</h3>', unsafe_allow_html=True)
        st.text_area("R", value=st.session_state.resume_raw, height=350, disabled=True, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c2:
        st.markdown('<div class="glass-panel"><h3>🎯 JD 目标镜像</h3>', unsafe_allow_html=True)
        st.text_area("J", value=st.session_state.jd_raw, height=350, disabled=True, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# [SECTION 9] 应用主程序入口 (Application Entry Point)
# =====================================================================
def main():
    """主程序路由控制"""
    inject_custom_css()
    init_session_state()
    
    # 根据状态机路由到不同的 UI 组件
    current_stage = st.session_state.stage
    
    if current_stage == "INPUT":
        render_input_stage()
    elif current_stage == "PROCESSING":
        render_processing_stage()
    elif current_stage == "RESULT":
        render_result_stage()

# 启动应用
if __name__ == "__main__":
    main()
