import streamlit as st
import docx
import pdfplumber
import io

# ==========================================
# 1. 页面配置与流光动画高级 CSS
# ==========================================
st.set_page_config(
    page_title="AutoJob-Agent | 智能海投系统",
    page_icon="💼",
    layout="wide"
)

# 注入动感流光动画 (Gradient Flow) 和精美样式
st.markdown("""
<style>
    /* 标题与副标题居中 */
    .title-container { text-align: center; margin-bottom: 2rem; }
    .main-header { font-size: 2.8rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1.2rem; color: #4B5563; }
    
    /* 流光动画卡片样式 */
    .flow-card {
        background: linear-gradient(-45deg, #f8fafc, #f1f5f9, #eff6ff, #f8fafc);
        background-size: 400% 400%;
        animation: gradientFlow 15s ease infinite;
        padding: 1.8rem; 
        border-radius: 1rem; 
        border: 1px solid #e2e8f0; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    
    /* 结果页并列卡片专用样式 */
    .result-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-top: 4px solid #3B82F6;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    }
    
    .card-title { font-size: 1.2rem; font-weight: 600; color: #1E3A8A; margin-bottom: 1rem; text-align: center;}

    /* 炫彩流动动画关键帧 */
    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 文本提取函数
# ==========================================
def extract_text(file):
    if file is None: return None
    file_bytes = file.read()
    ext = file.name.split(".")[-1].lower()
    try:
        text = ""
        if ext == "pdf":
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    if page.extract_text(): text += page.extract_text() + "\n"
        elif ext == "docx":
            doc = docx.Document(io.BytesIO(file_bytes))
            for p in doc.paragraphs: text += p.text + "\n"
            for table in doc.tables:
                for row in table.rows:
                    text += " | ".join([c.text.strip() for c in row.cells if c.text.strip()]) + "\n"
        return text.strip() if text.strip() else None
    except Exception:
        return None

# ==========================================
# 3. 页面多维流式交互控制 (Session State)
# ==========================================
# 使用 Streamlit 状态机，默认是输入页面（Stage 1）
if "app_stage" not in st.session_state:
    st.session_state.app_stage = "input_page"

# 顶部居中标题区
st.markdown(f"""
<div class="title-container">
    <div class="main-header">💼 AutoJob-Agent</div>
    <div class="sub-header">基于大模型的智能简历精准润色与海投一体化看板</div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------
# 页面一：数据源输入页
# ------------------------------------------
if st.session_state.app_stage == "input_page":
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown('<div class="flow-card">', unsafe_allow_html=True)
        st.markdown("### 📄 原始简历上传")
        uploaded_resume = st.file_uploader("支持 PDF 或 DOCX 格式简历", type=["pdf", "docx"], label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="flow-card">', unsafe_allow_html=True)
        st.markdown("### 🤖 智能投递意向设置")
        target_company = st.selectbox("意向公司类型", ["大厂/独角兽", "外企/跨国公司", "中小型科技公司", "不限"])
        model_provider = st.selectbox("大模型内核驱动", ["DeepSeek-V3 (推荐)", "GPT-4o", "Claude 3.5"])
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="flow-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 目标岗位 JD (Job Description)")
        jd_input_method = st.radio("选择提供方式", ["手动粘贴文本", "上传 JD 文档"], horizontal=True)
        
        jd_text_raw = ""
        if jd_input_method == "手动粘贴文本":
            jd_text_raw = st.text_area("请把招聘软件上的职位描述(JD)粘贴在这里...", height=195)
        else:
            uploaded_jd = st.file_uploader("上传 JD 文件", type=["pdf", "docx"])
            if uploaded_jd: jd_text_raw = extract_text(uploaded_jd)
        st.markdown('</div>', unsafe_allow_html=True)

    # 提交校验按钮
    st.markdown("---")
    if st.button("✨ 一键开始智能匹配与解析", type="primary", use_container_width=True):
        resume_text = extract_text(uploaded_resume)
        
        # 严密的拦截机制：必须两者都全才能跳转
        if not resume_text:
            st.error("❌ 请先上传有效的简历文件！")
        elif not jd_text_raw or len(jd_text_raw.strip()) < 10:
            st.error("❌ 请先输入或上传完整的目标岗位 JD！")
        else:
            # 校验通过，把数据存入缓存，并切换状态到解析结果页
            st.session_state.resume_content = resume_text
            st.session_state.jd_content = jd_text_raw
            st.session_state.app_stage = "result_page"
            st.rerun() # 重新刷新页面，直接切页

# ------------------------------------------
# 页面二：动态弹出的解析结果展示页
# ------------------------------------------
elif st.session_state.app_stage == "result_page":
    
    st.success("🎉 数据校验成功！Agent 已完成深度流式解析视图。")
    
    # 退出当前结果页的按钮，方便随时返回修改
    if st.button("↩️ 返回修改输入数据", type="secondary"):
        st.session_state.app_stage = "input_page"
        st.rerun()

    st.markdown("### 🔍 Agent 实时解析与视图")
    
    # 两栏布局，让简历解析结果和岗位 JD 平铺对比显示
    res_col1, res_col2 = st.columns(2, gap="large")
    
    with res_col1:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📄 简历解析结果</div>', unsafe_allow_html=True)
        st.text_area("提取的简历纯文本上下文：", value=st.session_state.resume_content, height=450, disabled=True, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with res_col2:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🎯 目标岗位 JD 视图</div>', unsafe_allow_html=True)
        st.text_area("锁定的岗位 JD 上下文：", value=st.session_state.jd_content, height=450, disabled=True, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
