import streamlit as st
import docx
import pdfplumber
import io

# ==========================================
# 1. 页面基本配置
# ==========================================
st.set_page_config(
    page_title="AutoJob-Agent | 智能求职自动化",
    page_icon="💼",
    layout="wide"
)

# 自定义 CSS 样式，让界面更有现代科技感
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.5rem;}
    .sub-header {font-size: 1.1rem; color: #4B5563; margin-bottom: 2rem;}
    .card {background-color: #F8FAFC; padding: 1.5rem; border-radius: 0.75rem; border: 1px solid #E2E8F0; margin-bottom: 1rem;}
    .section-title {font-size: 1.25rem; font-weight: 600; color: #0F172A; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 文本提取核心函数
# ==========================================
def extract_text_from_pdf(file_bytes):
    try:
        text = ""
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text: text += page_text + "\n"
        return (text, None) if text.strip() else (None, "PDF文件内容空或为纯图片扫描件")
    except Exception as e:
        return None, f"PDF解析失败: {str(e)}"

def extract_text_from_docx(file_bytes):
    try:
        text = ""
        doc = docx.Document(io.BytesIO(file_bytes))
        for p in doc.paragraphs:
            if p.text: text += p.text + "\n"
        for table in doc.tables:
            for row in table.rows:
                text += " | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()]) + "\n"
        return (text, None) if text.strip() else (None, "Word文件内容为空")
    except Exception as e:
        return None, f"Word解析失败: {str(e)}"

# ==========================================
# 3. 前端 UI 交互界面
# ==========================================

# 顶部导航与品牌区
st.markdown('<div class="main-header"> AutoJob-Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">基于大模型的智能简历精准润色与海投一体化看板</div>', unsafe_allow_html=True)

# 核心功能区：采用两栏平铺布局，左侧输入，右侧输出
main_col1, main_col2 = st.columns([1, 1], gap="large")

with main_col1:
    st.markdown('<div class="section-title">📥 输入数据源</div>', unsafe_allow_html=True)
    
    # 模块一：简历上传卡片
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("📑 **第一步：提供您的原始简历**")
        uploaded_resume = st.file_uploader(
            "支持 PDF / DOCX 格式", type=["pdf", "docx"], key="resume_uploader", label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
    # 模块二：岗位 JD 输入卡片
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("🎯 **第二步：指定目标岗位 JD (Job Description)**")
        jd_input_method = st.radio("选择提供方式", ["手动粘贴文本", "上传 JD 文档"], horizontal=True)
        
        jd_text = ""
        if jd_input_method == "手动粘贴文本":
            jd_text = st.text_area("请把招聘软件上的职位描述(JD)粘贴在这里...", height=180, placeholder="例如：负责开发大模型 Agent，精通 Python...")
        else:
            uploaded_jd = st.file_uploader("支持 PDF / DOCX 格式 JD", type=["pdf", "docx"], key="jd_uploader")
            if uploaded_jd:
                jd_bytes = uploaded_jd.read()
                jd_ext = uploaded_jd.name.split(".")[-1].lower()
                if jd_ext == "pdf":
                    jd_text, _ = extract_text_from_pdf(jd_bytes)
                else:
                    jd_text, _ = extract_text_from_docx(jd_bytes)
        st.markdown('</div>', unsafe_allow_html=True)

    # 模块三：投递意向偏好
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("🤖 **第三步：智能投递意向设置**")
        pref_col1, pref_col2 = st.columns(2)
        with pref_col1:
            target_company = st.selectbox("意向公司类型", ["大厂/独角兽", "外企/跨国公司", "中小型科技公司", "不限"])
        with pref_col2:
            model_provider = st.selectbox("大模型内核驱动", ["DeepSeek-V3 (推荐)", "GPT-4o", "Claude 3.5 Sonnet"])
        
        # 激活核心优化按钮
        start_btn = st.button("✨ 一键开始智能匹配与优化", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with main_col2:
    st.markdown('<div class="section-title">🔍 Agent 实时解析与视图</div>', unsafe_allow_html=True)
    
    # 使用 Tabs 标签页让数据展示极其整洁优雅
    tab1, tab2 = st.tabs(["📄 简历解析结果", "🎯 目标岗位 JD 视图"])
    
    with tab1:
        if uploaded_resume:
            resume_bytes = uploaded_resume.read()
            resume_ext = uploaded_resume.name.split(".")[-1].lower()
            
            with st.spinner("Agent 正在深度读取简历..."):
                res_text, err = extract_text_from_pdf(resume_bytes) if resume_ext == "pdf" else extract_text_from_docx(resume_bytes)
                
                if err:
                    st.error(err)
                else:
                    st.success(f"✅ 成功解析简历 ({len(res_text)} 字)")
                    st.text_area("简历上下文数据：", value=res_text, height=350, disabled=True, key="resume_view")
        else:
            st.info("💡 请在左侧上传简历文件")
            
    with tab2:
        if jd_text:
            st.success(f"✅ 成功锁定岗位目标 ({len(jd_text)} 字)")
            st.text_area("目标岗位上下文数据：", value=jd_text, height=350, disabled=True, key="jd_view")
        else:
            st.info("💡 请在左侧粘贴或上传岗位 JD 描述")

# ==========================================
# 4. 🛠️ 纯开发者隐藏视图 (不影响普通用户交互)
# ==========================================
st.markdown("---")
with st.expander("🛠️ 开发者专用控制台 (Debug Console)"):
    st.caption("当前处于 Phase 1 开发环境。生产部署时此控制台将自动熔断隐藏。")
    dev_col1, dev_col2, dev_col3 = st.columns(3)
    dev_col1.metric("前端路由状态", "Streamlit 进程正常")
    dev_col2.metric("LLM 接口通道", "未连接 (等待 Phase 2)", delta="-100%")
    dev_col3.metric("浏览器自动化驱动", "未初始化", delta="0")
    
    if start_btn:
        st.warning("⚠️ 触发测试：您点击了优化按钮。当前后端 LLM 未绑定，已拦截本次请求。核心 Prompt 逻辑将在 Phase 2 激活。")
