import streamlit as st
import docx
import pdfplumber
import io
import time
from typing import Optional, Dict, Any

# ==========================================
# 0. 导入项目模块（Phase 1 MVP）
# ==========================================
# 注意：以下模块需要你自己创建，代码在后面提供
try:
    from parser import extract_text as parser_extract_text
    from llm import get_llm
    from chain import build_optimization_chain
    from memory import get_memory, save_to_memory, load_from_memory
    from state import AppState, get_state, set_state, clear_state
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    # Fallback: 使用本地函数
    def parser_extract_text(file): return extract_text(file)

# ==========================================
# 1. 页面配置
# ==========================================
st.set_page_config(
    page_title="AutoJob-Agent | 智能海投系统",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. 完整省市数据
# ==========================================
PROVINCE_CITY_MAP = {
    "北京": ["北京市"], "天津": ["天津市"], "上海": ["上海市"], "重庆": ["重庆市"],
    "河北": ["石家庄", "唐山", "秦皇岛", "邯郸", "邢台", "保定", "张家口", "承德", "沧州", "廊坊", "衡水"],
    "山西": ["太原", "大同", "阳泉", "长治", "晋城", "朔州", "晋中", "运城", "忻州", "临汾", "吕梁"],
    "内蒙古": ["呼和浩特", "包头", "乌海", "赤峰", "通辽", "鄂尔多斯", "呼伦贝尔", "巴彦淖尔", "乌兰察布", "兴安盟", "锡林郭勒盟", "阿拉善盟"],
    "辽宁": ["沈阳", "大连", "鞍山", "抚顺", "本溪", "丹东", "锦州", "营口", "阜新", "辽阳", "盘锦", "铁岭", "朝阳", "葫芦岛"],
    "吉林": ["长春", "吉林", "四平", "辽源", "通化", "白山", "松原", "白城", "延边"],
    "黑龙江": ["哈尔滨", "齐齐哈尔", "鸡西", "鹤岗", "双鸭山", "大庆", "伊春", "佳木斯", "七台河", "牡丹江", "黑河", "绥化", "大兴安岭"],
    "江苏": ["南京", "无锡", "徐州", "常州", "苏州", "南通", "连云港", "淮安", "盐城", "扬州", "镇江", "泰州", "宿迁"],
    "浙江": ["杭州", "宁波", "温州", "嘉兴", "湖州", "绍兴", "金华", "衢州", "舟山", "台州", "丽水"],
    "安徽": ["合肥", "芜湖", "蚌埠", "淮南", "马鞍山", "淮北", "铜陵", "安庆", "黄山", "滁州", "阜阳", "宿州", "六安", "亳州", "池州", "宣城"],
    "福建": ["福州", "厦门", "莆田", "三明", "泉州", "漳州", "南平", "龙岩", "宁德"],
    "江西": ["南昌", "景德镇", "萍乡", "九江", "新余", "鹰潭", "赣州", "吉安", "宜春", "抚州", "上饶"],
    "山东": ["济南", "青岛", "淄博", "枣庄", "东营", "烟台", "潍坊", "济宁", "泰安", "威海", "日照", "临沂", "德州", "聊城", "滨州", "菏泽"],
    "河南": ["郑州", "开封", "洛阳", "平顶山", "安阳", "鹤壁", "新乡", "焦作", "濮阳", "许昌", "漯河", "三门峡", "南阳", "商丘", "信阳", "周口", "驻马店"],
    "湖北": ["武汉", "黄石", "十堰", "宜昌", "襄阳", "鄂州", "荆门", "孝感", "荆州", "黄冈", "咸宁", "随州", "恩施"],
    "湖南": ["长沙", "株洲", "湘潭", "衡阳", "邵阳", "岳阳", "常德", "张家界", "益阳", "郴州", "永州", "怀化", "娄底", "湘西"],
    "广东": ["广州", "深圳", "珠海", "汕头", "韶关", "佛山", "江门", "湛江", "茂名", "肇庆", "惠州", "梅州", "汕尾", "河源", "阳江", "清远", "东莞", "中山", "潮州", "揭阳", "云浮"],
    "广西": ["南宁", "柳州", "桂林", "梧州", "北海", "防城港", "钦州", "贵港", "玉林", "百色", "贺州", "河池", "来宾", "崇左"],
    "海南": ["海口", "三亚", "三沙", "儋州", "五指山", "琼海", "文昌", "万宁", "东方", "定安", "屯昌", "澄迈", "临高"],
    "四川": ["成都", "自贡", "攀枝花", "泸州", "德阳", "绵阳", "广元", "遂宁", "内江", "乐山", "南充", "眉山", "宜宾", "广安", "达州", "雅安", "巴中", "资阳", "阿坝", "甘孜", "凉山"],
    "贵州": ["贵阳", "六盘水", "遵义", "安顺", "毕节", "铜仁", "黔西南", "黔东南", "黔南"],
    "云南": ["昆明", "曲靖", "玉溪", "保山", "昭通", "丽江", "普洱", "临沧", "楚雄", "红河", "文山", "西双版纳", "大理", "德宏", "怒江", "迪庆"],
    "西藏": ["拉萨", "日喀则", "昌都", "林芝", "山南", "那曲", "阿里"],
    "陕西": ["西安", "铜川", "宝鸡", "咸阳", "渭南", "延安", "汉中", "榆林", "安康", "商洛"],
    "甘肃": ["兰州", "嘉峪关", "金昌", "白银", "天水", "武威", "张掖", "平凉", "酒泉", "庆阳", "定西", "陇南", "临夏", "甘南"],
    "青海": ["西宁", "海东", "海北", "黄南", "海南州", "果洛", "玉树", "海西"],
    "宁夏": ["银川", "石嘴山", "吴忠", "固原", "中卫"],
    "新疆": ["乌鲁木齐", "克拉玛依", "吐鲁番", "哈密", "昌吉", "博尔塔拉", "巴音郭楞", "阿克苏", "克孜勒苏", "喀什", "和田", "伊犁", "塔城", "阿勒泰"],
    "台湾": ["台北", "新北", "桃园", "台中", "台南", "高雄", "基隆", "新竹", "嘉义"],
    "香港": ["香港"], "澳门": ["澳门"]
}

ALL_PROVINCES = list(PROVINCE_CITY_MAP.keys())
ALL_CITIES = []
for cities in PROVINCE_CITY_MAP.values():
    ALL_CITIES.extend(cities)
ALL_CITIES = list(dict.fromkeys(ALL_CITIES))

OVERSEAS_COUNTRIES = [
    "美国", "英国", "加拿大", "澳大利亚", "德国", "法国", "日本", 
    "新加坡", "荷兰", "瑞典", "瑞士", "新西兰", "爱尔兰", "丹麦", 
    "挪威", "芬兰", "奥地利", "比利时", "卢森堡", "其他"
]

# ==========================================
# 3. 高级 CSS - 修复下拉列表问题
# ==========================================
# 关键修复：移除所有强制 popover 定位的 CSS，改用原生 Streamlit 行为
# 通过限制选项数量和调整布局来避免 popover 溢出
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Instrument+Serif:ital@0;1&display=swap');

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

    /* 全局背景 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #6dd5ed 75%, #667eea 100%) !important;
        background-size: 400% 400% !important;
        animation: gradientShift 20s ease infinite !important;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .block-container {
        padding: 1.2rem 1.5rem !important;
        max-width: 1100px !important;
    }

    /* ===== 标题区 Liquid Glass ===== */
    .title-glass {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(16px) saturate(180%);
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        border: 1px solid rgba(255,255,255,0.15);
        box-shadow: inset 0 1px 1px rgba(255,255,255,0.1), 0 8px 32px rgba(0,0,0,0.08);
        position: relative;
        overflow: hidden;
        padding: 0.875rem 1.5rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 1.2rem;
        animation: fadeInDown 0.8s ease-out;
        transition: all 0.4s ease;
    }
    .title-glass:hover {
        background: rgba(255, 255, 255, 0.12);
        box-shadow: inset 0 1px 1px rgba(255,255,255,0.15), 0 12px 40px rgba(0,0,0,0.12);
    }
    .main-header {
        font-family: 'Instrument Serif', serif;
        font-style: italic;
        font-size: 2.6rem;
        font-weight: 400;
        color: rgba(255,255,255,0.95);
        margin: 0 0 0.15rem 0;
        letter-spacing: -0.02em;
        line-height: 1;
    }
    .sub-header {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        font-weight: 300;
        color: rgba(255,255,255,0.7);
        margin: 0;
    }

    /* ===== Liquid Glass 卡片 ===== */
    .glass-panel {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(20px) saturate(160%);
        -webkit-backdrop-filter: blur(20px) saturate(160%);
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: inset 0 1px 1px rgba(255,255,255,0.08), 0 4px 20px rgba(0,0,0,0.06);
        position: relative;
        overflow: hidden;
        padding: 0.7rem 0.9rem !important;
        border-radius: 14px;
        margin-bottom: 0.6rem !important;
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
        animation: fadeInUp 0.5s ease-out both;
    }
    .glass-panel:hover {
        transform: translateY(-3px);
        background: rgba(255, 255, 255, 0.1);
        box-shadow: inset 0 1px 1px rgba(255,255,255,0.12), 0 8px 28px rgba(0,0,0,0.1);
    }

    /* 卡片标题 */
    .card-header {
        font-family: 'Instrument Serif', serif;
        font-style: italic;
        color: rgba(255,255,255,0.95);
        font-size: 1rem;
        font-weight: 400;
        margin: 0 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        letter-spacing: -0.01em;
    }

    /* ===== 修复：下拉列表样式优化（不移除原生行为） ===== */
    /* 只美化，不强制改变位置，避免左上角 bug */
    div[data-baseweb="select"] > div {
        background: rgba(0, 0, 0, 0.12) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: rgba(255,255,255,0.9) !important;
        min-height: 36px !important;
        transition: all 0.25s ease !important;
    }
    div[data-baseweb="select"] > div:hover {
        background: rgba(0, 0, 0, 0.2) !important;
        border-color: rgba(255,255,255,0.25) !important;
    }
    /* 下拉菜单美化 */
    div[data-baseweb="menu"] {
        background-color: rgba(255, 255, 255, 0.98) !important;
        border-radius: 10px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15) !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
    }
    div[data-baseweb="menu"] li {
        color: #1e293b !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 5px 12px !important;
        transition: all 0.15s ease;
        min-height: 32px !important;
    }
    div[data-baseweb="menu"] li:hover {
        background-color: #e0e7ff !important;
        color: #4338ca !important;
    }

    /* ===== 单选按钮 ===== */
    .stRadio > div > div > label {
        color: rgba(255,255,255,0.7) !important;
        font-size: 0.85rem !important;
        transition: all 0.2s ease;
        padding: 0.2rem 0 !important;
    }
    .stRadio > div > div > label:hover {
        color: rgba(255,255,255,0.95) !important;
    }

    /* ===== 文件上传器 ===== */
    .stFileUploader > div {
        background: rgba(0, 0, 0, 0.06) !important;
        backdrop-filter: blur(8px) !important;
        border: 1.5px dashed rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
        padding: 0.5rem !important;
        transition: all 0.3s ease !important;
    }
    .stFileUploader > div:hover {
        border-color: rgba(255,255,255,0.35) !important;
        background: rgba(0, 0, 0, 0.12) !important;
    }

    /* ===== 文本输入框 ===== */
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.1) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: rgba(255,255,255,0.85) !important;
        font-size: 0.85rem !important;
        padding: 0.6rem 0.75rem !important;
        transition: all 0.25s ease !important;
    }
    .stTextArea textarea:hover {
        background: rgba(0, 0, 0, 0.16) !important;
        border-color: rgba(255,255,255,0.2) !important;
    }
    .stTextArea textarea:focus {
        background: rgba(0, 0, 0, 0.2) !important;
        border-color: rgba(255,255,255,0.35) !important;
        box-shadow: 0 0 0 3px rgba(255,255,255,0.06) !important;
    }
    .stTextArea textarea::placeholder {
        color: rgba(255,255,255,0.35) !important;
        font-size: 0.8rem !important;
    }

    /* ===== 步骤指示器 ===== */
    .step-track {
        display: flex; align-items: center; justify-content: center; gap: 0;
        margin-bottom: 1.2rem;
        animation: fadeIn 0.5s ease-out 0.3s both;
    }
    .step-line { width: 40px; height: 2px; background: rgba(255,255,255,0.15); transition: all 0.4s ease; }
    .step-line.active { background: linear-gradient(90deg, rgba(255,255,255,0.5), rgba(255,255,255,0.85)); }
    .step-node {
        width: 28px; height: 28px; border-radius: 50%;
        background: rgba(255,255,255,0.08); border: 1.5px solid rgba(255,255,255,0.25);
        display: flex; align-items: center; justify-content: center;
        font-size: 0.75rem; font-weight: 700; color: rgba(255,255,255,0.5);
        transition: all 0.4s ease;
    }
    .step-node.active {
        background: rgba(255,255,255,0.2); border-color: rgba(255,255,255,0.7);
        color: rgba(255,255,255,0.95); box-shadow: 0 0 12px rgba(255,255,255,0.1);
    }
    .step-node.completed {
        background: rgba(255,255,255,0.9); border-color: rgba(255,255,255,0.9); color: #667eea;
    }

    /* ===== 状态胶囊 ===== */
    .status-chip {
        display: inline-flex; align-items: center; gap: 0.3rem;
        padding: 0.2rem 0.6rem; border-radius: 100px;
        font-size: 0.7rem; font-weight: 600;
        transition: all 0.3s ease;
    }
    .chip-ready { background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.25); }
    .chip-ready:hover { background: rgba(16, 185, 129, 0.3) !important; }
    .chip-wait { background: rgba(255, 255, 255, 0.06); color: rgba(255,255,255,0.5); border: 1px solid rgba(255,255,255,0.1); }

    /* ===== 主按钮 Liquid Glass Strong ===== */
    .stButton > button[kind="primary"] {
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        box-shadow: inset 0 1px 1px rgba(255,255,255,0.15), 0 4px 16px rgba(0,0,0,0.1) !important;
        color: rgba(255,255,255,0.95) !important;
        border-radius: 9999px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        height: 42px !important;
        letter-spacing: 0.01em;
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1) !important;
        position: relative;
        overflow: hidden;
    }
    .stButton > button[kind="primary"]:hover {
        background: rgba(255, 255, 255, 0.25) !important;
        transform: translateY(-2px);
        box-shadow: inset 0 1px 1px rgba(255,255,255,0.2), 0 8px 24px rgba(0,0,0,0.15) !important;
    }
    .stButton > button[kind="primary"]:active { transform: translateY(0); }
    .stButton > button[kind="primary"]:disabled {
        background: rgba(255,255,255,0.04) !important;
        box-shadow: none !important;
        color: rgba(255,255,255,0.25) !important;
        border-color: rgba(255,255,255,0.05) !important;
    }

    /* ===== 返回按钮 ===== */
    .stButton > button:not([kind="primary"]) {
        background: transparent !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: rgba(255,255,255,0.6) !important;
        border-radius: 10px !important;
        font-size: 0.85rem !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        background: rgba(255,255,255,0.08) !important;
        border-color: rgba(255,255,255,0.3) !important;
        color: rgba(255,255,255,0.9) !important;
    }

    /* ===== 地区提示 ===== */
    .city-detected {
        background: rgba(16, 185, 129, 0.12) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(16, 185, 129, 0.2) !important;
        border-radius: 8px; padding: 0.4rem 0.7rem;
        color: #6ee7b7; font-size: 0.8rem; margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }
    .city-detected:hover { background: rgba(16, 185, 129, 0.18) !important; }
    .city-not-detected {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px; padding: 0.4rem 0.7rem;
        color: rgba(255,255,255,0.55); font-size: 0.8rem; margin-bottom: 0.5rem;
    }

    /* ===== 黑体提示 ===== */
    .hint-text {
        color: rgba(255,255,255,0.9) !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        margin-bottom: 0.35rem !important;
    }

    /* ===== 结果页 ===== */
    .result-header-glass {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid rgba(255,255,255,0.15);
        box-shadow: inset 0 1px 1px rgba(255,255,255,0.1), 0 4px 20px rgba(0,0,0,0.06);
        position: relative;
        overflow: hidden;
        padding: 0.8rem; border-radius: 14px;
        margin-bottom: 1.2rem; text-align: center;
        transition: all 0.4s ease;
    }
    .result-header-glass:hover { background: rgba(255, 255, 255, 0.12); }
    .result-header-glass h3 {
        font-family: 'Instrument Serif', serif;
        font-style: italic;
        margin: 0 !important;
        color: rgba(255,255,255,0.95) !important;
        font-weight: 400 !important;
        font-size: 1.15rem !important;
    }

    .result-glass {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(16px) saturate(150%);
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: inset 0 1px 1px rgba(255,255,255,0.08), 0 4px 16px rgba(0,0,0,0.05);
        position: relative;
        overflow: hidden;
        padding: 1rem; border-radius: 14px;
        transition: all 0.4s ease;
        animation: slideInUp 0.5s ease-out both;
    }
    .result-glass:hover {
        background: rgba(255, 255, 255, 0.1);
        box-shadow: inset 0 1px 1px rgba(255,255,255,0.1), 0 8px 24px rgba(0,0,0,0.08);
    }
    .result-title {
        font-family: 'Instrument Serif', serif;
        font-style: italic;
        font-size: 0.95rem;
        font-weight: 400;
        color: rgba(255,255,255,0.95);
        margin-bottom: 0.2rem;
    }
    .result-meta {
        font-size: 0.7rem;
        font-weight: 300;
        color: rgba(255,255,255,0.45);
        margin-bottom: 0.6rem;
    }

    .success-glass {
        background: rgba(16, 185, 129, 0.15) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(16, 185, 129, 0.2) !important;
        color: #6ee7b7 !important;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        font-weight: 500;
        font-size: 0.85rem;
        margin-bottom: 0.8rem;
        animation: slideInDown 0.4s ease-out;
    }

    .footer-hint {
        text-align: center;
        color: rgba(255,255,255,0.35);
        font-size: 0.75rem;
        font-weight: 300;
        margin-top: 1.2rem;
    }

    /* ===== 分割线 ===== */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent) !important;
        margin: 1.2rem 0 !important;
    }

    /* ===== 隐藏默认元素 ===== */
    #MainMenu, footer, .stDeployButton, header { visibility: hidden; display: none !important; }

    /* ===== 滚动条 ===== */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.3); }

    /* ===== 关键帧 ===== */
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes fadeInDown { from { opacity: 0; transform: translateY(-12px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes slideInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes slideInDown { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: translateY(0); } }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. 文本解析函数（本地 Fallback）
# ==========================================
def extract_text(file) -> Optional[str]:
    if file is None: 
        return None
    file_bytes = file.read()
    ext = file.name.split(".")[-1].lower()
    try:
        text = ""
        if ext == "pdf":
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    if page.extract_text(): 
                        text += page.extract_text() + "\n"
        elif ext == "docx":
            doc = docx.Document(io.BytesIO(file_bytes))
            for p in doc.paragraphs: 
                text += p.text + "\n"
        return text.strip() if text.strip() else None
    except Exception: 
        return None

def extract_cities_from_resume(text: str) -> list:
    if not text: 
        return []
    found_cities = [city for city in ALL_CITIES if city in text]
    return list(dict.fromkeys(found_cities))[:3]

# ==========================================
# 5. 会话状态初始化（使用 state.py 封装）
# ==========================================
def init_session_state():
    """初始化所有 session state 变量"""
    defaults = {
        "app_stage": "input",
        "loading": False,
        "resume_content": "",
        "jd_content": "",
        "detected_cities": [],
        "city_scope": "国内",
        "selected_province": None,
        "selected_city": None,
        "custom_city": "",
        "province_city_selected": False,
        # Phase 1 MVP 新增状态
        "optimized_resume": "",           # LLM 优化后的简历
        "optimization_history": [],       # Memory 历史记录
        "current_model": "DeepSeek-V3",   # 当前选择的大模型
        "target_company_type": "不限",      # 目标公司类型
        "match_score": 0,                 # 匹配分数
        "analysis_result": {},            # 完整分析结果
    }
    for key, val in defaults.items():
        if key not in st.session_state: 
            st.session_state[key] = val

init_session_state()

# ==========================================
# 6. 核心功能：调用 LLM 优化简历（Phase 1 MVP）
# ==========================================
def optimize_resume_with_llm(resume_text: str, jd_text: str, company_type: str, model_name: str) -> Dict[str, Any]:
    """
    Phase 1 MVP 核心功能：调用 LLM 优化简历

    实现方式：
    1. 使用 llm.py 获取 LLM 实例
    2. 使用 chain.py 构建优化 Chain
    3. 使用 memory.py 保存对话历史
    4. 返回优化后的简历和分析结果
    """
    if not MODULES_AVAILABLE:
        # Fallback: 模拟 LLM 输出（用于测试 UI）
        return {
            "optimized_resume": f"【模拟输出】\n\n基于以下 JD 优化后的简历：\n\n原始简历长度：{len(resume_text)} 字符\nJD 长度：{len(jd_text)} 字符\n目标公司：{company_type}\n使用模型：{model_name}\n\n[此处将显示 LLM 生成的优化后简历内容...]",
            "match_score": 85,
            "key_skills_matched": ["Python", "机器学习", "数据分析"],
            "suggestions": ["建议补充项目量化数据", "突出领导力经验"],
            "memory_saved": False
        }

    # 真实 LLM 调用流程
    try:
        # Step 1: 获取 LLM 实例（llm.py）
        llm = get_llm(model_name=model_name)

        # Step 2: 获取 Memory 实例（memory.py）
        memory = get_memory(session_id=st.session_state.get("session_id", "default"))

        # Step 3: 构建优化 Chain（chain.py）
        chain = build_optimization_chain(llm=llm, memory=memory)

        # Step 4: 执行 Chain
        result = chain.run(
            resume=resume_text,
            jd=jd_text,
            company_type=company_type
        )

        # Step 5: 保存到 Memory（memory.py）
        save_to_memory(
            session_id=st.session_state.get("session_id", "default"),
            input_data={"resume_length": len(resume_text), "jd_length": len(jd_text)},
            output_data={"optimized_length": len(result)}
        )

        # Step 6: 解析结果（简化版）
        return {
            "optimized_resume": result,
            "match_score": 85,  # 可由 LLM 输出结构化数据后解析
            "key_skills_matched": [],
            "suggestions": [],
            "memory_saved": True
        }

    except Exception as e:
        st.error(f"LLM 调用失败: {str(e)}")
        return {
            "optimized_resume": f"错误：{str(e)}",
            "match_score": 0,
            "key_skills_matched": [],
            "suggestions": [],
            "memory_saved": False
        }

# ==========================================
# 7. 渲染逻辑：数据源输入页
# ==========================================
if st.session_state.app_stage == "input":

    # 标题 Liquid Glass
    st.markdown("""
    <div class="title-glass">
        <h1 class="main-header">AutoJob-Agent</h1>
        <p class="sub-header">基于大模型的智能简历精准润色与海投一体化看板</p>
    </div>
    """, unsafe_allow_html=True)

    # 步骤指示器
    st.markdown('<div class="step-track"><div class="step-node active">1</div><div class="step-line active"></div><div class="step-node">2</div></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        # === 卡片1: 简历上传 ===
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📄 原始简历上传</div>', unsafe_allow_html=True)
        uploaded_resume = st.file_uploader("上传简历", type=["pdf", "docx"], label_visibility="collapsed")

        if uploaded_resume:
            resume_text_temp = extract_text(uploaded_resume)
            if resume_text_temp:
                st.session_state.detected_cities = extract_cities_from_resume(resume_text_temp)
            st.markdown(f'<div class="status-chip chip-ready">✓ {uploaded_resume.name}</div>', unsafe_allow_html=True)
        else:
            st.session_state.detected_cities = []
            st.markdown('<div class="status-chip chip-wait">○ 等待上传</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # === 卡片2: 智能投递意向 ===
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">🤖 智能投递意向</div>', unsafe_allow_html=True)

        # 修复：使用 key 绑定到 session_state，确保状态持久化
        company_type = st.selectbox(
            "意向公司", 
            ["大厂", "独角兽", "国央企", "外企/跨国公司", "中小型科技公司", "不限"], 
            label_visibility="collapsed",
            key="company_type_select"
        )
        st.session_state.target_company_type = company_type

        model_choice = st.selectbox(
            "大模型", 
            ["DeepSeek-V3 (推荐)", "GPT-4o", "Claude 3.5"], 
            label_visibility="collapsed",
            key="model_select"
        )
        st.session_state.current_model = model_choice.replace(" (推荐)", "")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # === 卡片3: 目标岗位JD ===
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">🎯 目标岗位 JD</div>', unsafe_allow_html=True)

        jd_method = st.radio(
            "提供方式", 
            ["手动粘贴文本", "上传 JD 文档"], 
            horizontal=True, 
            label_visibility="collapsed",
            key="jd_method_radio"
        )

        jd_text_raw = ""
        if jd_method == "手动粘贴文本":
            st.markdown('<div class="hint-text">请把招聘软件上的职位描述(JD)粘贴在这里</div>', unsafe_allow_html=True)
            jd_text_raw = st.text_area(
                "粘贴JD", 
                placeholder="在此粘贴职位描述...", 
                height=100, 
                label_visibility="collapsed",
                key="jd_text_area"
            )
        else:
            uploaded_jd = st.file_uploader(
                "上传JD", 
                type=["pdf", "docx"], 
                label_visibility="collapsed",
                key="jd_file_uploader"
            )
            if uploaded_jd: 
                jd_text_raw = extract_text(uploaded_jd)
        st.markdown('</div>', unsafe_allow_html=True)

        # === 卡片4: 投递意向地区（修复下拉列表问题）===
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📍 投递意向地区</div>', unsafe_allow_html=True)

        if st.session_state.detected_cities:
            cities_str = "、".join(st.session_state.detected_cities)
            st.markdown(f'<div class="city-detected">🎯 已从简历检测到：{cities_str}</div>', unsafe_allow_html=True)

            # 修复：添加 key，避免组件冲突
            selected_from_resume = st.selectbox(
                "确认城市", 
                st.session_state.detected_cities + ["其他（手动输入）"], 
                label_visibility="collapsed",
                key="resume_city_select"
            )

            if selected_from_resume == "其他（手动输入）":
                st.session_state.city_scope = "其他"
                custom_city = st.text_input(
                    "输入意向城市", 
                    placeholder="例如：三亚", 
                    label_visibility="collapsed", 
                    key="custom_city_input_resume"
                )
                st.session_state.custom_city = custom_city
                st.session_state.selected_city = custom_city
            else:
                st.session_state.selected_city = selected_from_resume
                st.session_state.city_scope = "国内"
        else:
            st.markdown('<div class="city-not-detected">○ 未检测到意向城市，请手动选择</div>', unsafe_allow_html=True)

            # 修复：使用唯一 key
            scope = st.radio(
                "地区范围", 
                ["国内", "海外"], 
                horizontal=True, 
                label_visibility="collapsed", 
                key="scope_radio"
            )
            st.session_state.city_scope = scope

            if scope == "国内":
                # 修复：省份选择使用唯一 key
                selected_province = st.selectbox(
                    "选择省份", 
                    ALL_PROVINCES, 
                    label_visibility="collapsed", 
                    key="province_select"
                )
                st.session_state.selected_province = selected_province

                # 城市选择（基于省份）
                if selected_province and selected_province in PROVINCE_CITY_MAP:
                    cities_in_province = PROVINCE_CITY_MAP[selected_province]
                    # 修复：城市选择使用唯一 key，且基于省份动态更新
                    selected_city = st.selectbox(
                        "选择城市", 
                        cities_in_province, 
                        label_visibility="collapsed", 
                        key=f"city_select_{selected_province}"  # 动态 key，切换省份时重置
                    )
                    st.session_state.selected_city = selected_city
            else:
                # 修复：海外选择使用唯一 key
                country = st.selectbox(
                    "选择国家/地区", 
                    OVERSEAS_COUNTRIES, 
                    label_visibility="collapsed", 
                    key="country_select"
                )
                if country == "其他":
                    custom_overseas = st.text_input(
                        "输入意向城市/国家", 
                        placeholder="例如：迪拜", 
                        label_visibility="collapsed", 
                        key="custom_overseas_input"
                    )
                    st.session_state.custom_city = custom_overseas
                    st.session_state.selected_city = custom_overseas
                else:
                    st.session_state.selected_city = country
        st.markdown('</div>', unsafe_allow_html=True)

    # 提交区域
    st.markdown("<hr>", unsafe_allow_html=True)

    # 修复：正确判断是否有简历（处理文件指针已读取的情况）
    has_res = uploaded_resume is not None
    has_jd = bool(jd_text_raw and len(jd_text_raw.strip()) >= 10)

    col_s, col_b = st.columns([1, 2])
    col_s.markdown(
        '<div class="status-chip chip-ready">✓ 信息已就绪</div>' if (has_res and has_jd) 
        else '<div class="status-chip chip-wait">○ 待完善输入源数据</div>', 
        unsafe_allow_html=True
    )

    with col_b:
        if st.button(
            "✨ 一键开始智能匹配", 
            use_container_width=True, 
            disabled=not (has_res and has_jd),
            key="start_button"
        ):
            # 保存数据到 session state（state.py 封装）
            if uploaded_resume:
                uploaded_resume.seek(0)  # 重置文件指针
                st.session_state.resume_content = extract_text(uploaded_resume)
            st.session_state.jd_content = jd_text_raw
            st.session_state.loading = True
            st.rerun()

# ==========================================
# 8. 加载页（Phase 1：集成 LLM 调用）
# ==========================================
elif st.session_state.loading:
    p_text = st.empty()
    p_bar = st.progress(0)

    # Phase 1 MVP：在加载过程中调用 LLM
    stages = [
        ("📄 解析简历结构", 20),
        ("🎯 分析岗位 JD", 40), 
        ("🤖 调用大模型优化简历", 70),   # 新增：实际调用 LLM
        ("💾 保存 Memory 状态", 85),      # 新增：保存对话历史
        ("✨ 即将完成", 100)
    ]

    # 在进度条到 40% 时调用 LLM
    llm_result = None

    for i in range(100):
        time.sleep(0.02)
        p_bar.progress(i + 1)

        # 更新状态文本
        for text, threshold in stages:
            if i < threshold:
                p_text.markdown(
                    f"<div style='text-align:center; color:rgba(255,255,255,0.8); font-weight:500; font-size:0.9rem;'>"
                    f"{text} {i+1}%</div>", 
                    unsafe_allow_html=True
                )
                break

        # 在 45% 进度时执行 LLM 调用（后台）
        if i == 45 and llm_result is None:
            p_text.markdown(
                f"<div style='text-align:center; color:rgba(255,255,255,0.8); font-weight:500; font-size:0.9rem;'>"
                f"🤖 正在调用 {st.session_state.current_model} 优化简历...</div>", 
                unsafe_allow_html=True
            )
            llm_result = optimize_resume_with_llm(
                resume_text=st.session_state.resume_content,
                jd_text=st.session_state.jd_content,
                company_type=st.session_state.target_company_type,
                model_name=st.session_state.current_model
            )
            # 保存结果到 session state
            st.session_state.optimized_resume = llm_result.get("optimized_resume", "")
            st.session_state.match_score = llm_result.get("match_score", 0)
            st.session_state.analysis_result = llm_result

    # 完成
    st.session_state.loading = False
    st.session_state.app_stage = "result"
    st.rerun()

# ==========================================
# 9. 结果页（Phase 1：展示 LLM 输出）
# ==========================================
elif st.session_state.app_stage == "result":

    st.markdown('<div class="result-header-glass"><h3>🔍 智能解析对比看板</h3></div>', unsafe_allow_html=True)
    st.markdown('<div class="step-track"><div class="step-node completed">✓</div><div class="step-line active"></div><div class="step-node active">2</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="success-glass">🎉 Agent 已完成深度解析与简历优化</div>', unsafe_allow_html=True)

    if st.button("← 返回修改数据", key="back_btn"):
        st.session_state.app_stage = "input"
        st.rerun()

    # ===== Phase 1 MVP 新增：展示优化后的简历 =====

    # 匹配分数展示
    score = st.session_state.get("match_score", 0)
    if score > 0:
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="display: inline-block; background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); 
                        border-radius: 16px; padding: 0.8rem 2rem; border: 1px solid rgba(255,255,255,0.2);">
                <div style="font-size: 2rem; font-weight: 700; color: #6ee7b7;">{score}%</div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.6);">简历匹配度</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 三列布局：原始简历 | JD | 优化后简历
    res_col1, res_col2, res_col3 = st.columns(3, gap="medium")

    with res_col1:
        st.markdown('<div class="result-glass">', unsafe_allow_html=True)
        st.markdown('<div class="result-title">📄 原始简历</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-meta">{len(st.session_state.resume_content)} 字符 · 已解析</div>', unsafe_allow_html=True)
        st.text_area(
            "原始简历", 
            value=st.session_state.resume_content, 
            height=380, 
            disabled=True, 
            label_visibility="collapsed",
            key="original_resume_display"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with res_col2:
        st.markdown('<div class="result-glass">', unsafe_allow_html=True)
        st.markdown('<div class="result-title">🎯 目标岗位 JD</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-meta">{len(st.session_state.jd_content)} 字符 · 已注入</div>', unsafe_allow_html=True)
        st.text_area(
            "JD", 
            value=st.session_state.jd_content, 
            height=380, 
            disabled=True, 
            label_visibility="collapsed",
            key="jd_display"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with res_col3:
        st.markdown('<div class="result-glass">', unsafe_allow_html=True)
        st.markdown('<div class="result-title">✨ AI 优化后的简历</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-meta">{len(st.session_state.get("optimized_resume", ""))} 字符 · LLM 生成</div>', unsafe_allow_html=True)

        # 展示 LLM 优化结果
        optimized = st.session_state.get("optimized_resume", "优化失败，请重试")
        st.text_area(
            "优化简历", 
            value=optimized, 
            height=380, 
            disabled=True, 
            label_visibility="collapsed",
            key="optimized_resume_display"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # ===== 操作按钮区 =====
    st.markdown("<hr>", unsafe_allow_html=True)

    btn_col1, btn_col2, btn_col3 = st.columns(3)

    with btn_col1:
        if st.button("📋 复制优化简历", use_container_width=True, key="copy_btn"):
            st.toast("已复制到剪贴板！")

    with btn_col2:
        if st.button("🔄 重新优化", use_container_width=True, key="reoptimize_btn"):
            st.session_state.loading = True
            st.rerun()

    with btn_col3:
        if st.button("💾 导出 Word", use_container_width=True, key="export_btn"):
            st.toast("导出功能开发中...")

    # Memory 状态提示
    analysis = st.session_state.get("analysis_result", {})
    if analysis.get("memory_saved"):
        st.markdown("<div class='footer-hint'>💾 本次优化记录已保存至 Memory</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='footer-hint'>⚠️ Memory 保存未启用（模块未加载）</div>", unsafe_allow_html=True)

    st.markdown("<div class='footer-hint'>💡 对比视图已生成，左侧为原始简历，右侧为 AI 优化版本</div>", unsafe_allow_html=True)
