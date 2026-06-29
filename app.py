import streamlit as st
import docx
import pdfplumber
import io
import time

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
# 3. 高级 CSS - Liquid Glass + 极致瘦身 + 强制下拉
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Instrument+Serif:ital@0;1&display=swap');

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

    /* 全局背景 - 柔和蓝紫渐变流动 */
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
        background-blend-mode: luminosity;
        backdrop-filter: blur(16px) saturate(180%);
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        border: none;
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
    .title-glass::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: inherit;
        padding: 1.2px;
        background: linear-gradient(180deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0.1) 40%, rgba(255,255,255,0) 60%, rgba(255,255,255,0.1) 80%, rgba(255,255,255,0.4) 100%);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events: none;
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

    /* ===== 极致瘦身 Liquid Glass 卡片 ===== */
    .glass-panel {
        background: rgba(255, 255, 255, 0.06);
        background-blend-mode: luminosity;
        backdrop-filter: blur(20px) saturate(160%);
        -webkit-backdrop-filter: blur(20px) saturate(160%);
        border: none;
        box-shadow: inset 0 1px 1px rgba(255,255,255,0.08), 0 4px 20px rgba(0,0,0,0.06);
        position: relative;
        overflow: hidden;
        padding: 0.7rem 0.9rem !important;
        border-radius: 14px;
        margin-bottom: 0.6rem !important;
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
        animation: fadeInUp 0.5s ease-out both;
    }
    .glass-panel::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: inherit;
        padding: 1px;
        background: linear-gradient(180deg, rgba(255,255,255,0.35) 0%, rgba(255,255,255,0.08) 40%, rgba(255,255,255,0) 60%, rgba(255,255,255,0.08) 80%, rgba(255,255,255,0.35) 100%);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events: none;
        opacity: 0.6;
        transition: opacity 0.3s ease;
    }
    .glass-panel:hover::before {
        opacity: 1;
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

    /* ===== 强制下拉列表向下展开 + 限制高度 ===== */
    div[data-baseweb="popover"] {
        position: absolute !important;
        top: calc(100% + 4px) !important;
        bottom: auto !important;
        left: 0 !important;
        right: auto !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        transform: none !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15) !important;
        border-radius: 10px !important;
        max-height: 180px !important;
    }
    div[data-baseweb="popover"] > div {
        max-height: 180px !important;
        overflow-y: auto !important;
    }
    div[data-baseweb="popover"] > div > div {
        max-height: 180px !important;
        overflow-y: auto !important;
    }
    [data-baseweb="menu"] {
        background-color: rgba(255, 255, 255, 0.98) !important;
        border-radius: 10px !important;
        max-height: 180px !important;
        overflow-y: auto !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1) !important;
    }
    [data-baseweb="menu"] li {
        color: #1e293b !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 5px 12px !important;
        transition: all 0.15s ease;
        min-height: 32px !important;
    }
    [data-baseweb="menu"] li:hover {
        background-color: #e0e7ff !important;
        color: #4338ca !important;
    }
    /* 微型滚动条 */
    [data-baseweb="menu"]::-webkit-scrollbar,
    div[data-baseweb="popover"] > div::-webkit-scrollbar {
        width: 4px;
    }
    [data-baseweb="menu"]::-webkit-scrollbar-thumb,
    div[data-baseweb="popover"] > div::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.4);
        border-radius: 2px;
    }

    /* ===== 选择器样式 ===== */
    .stSelectbox > div > div {
        background: rgba(0, 0, 0, 0.12) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: rgba(255,255,255,0.9) !important;
        min-height: 36px !important;
        transition: all 0.25s ease !important;
    }
    .stSelectbox > div > div:hover {
        background: rgba(0, 0, 0, 0.2) !important;
        border-color: rgba(255,255,255,0.25) !important;
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
        background-blend-mode: luminosity !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        border: none !important;
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
    .stButton > button[kind="primary"]::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: inherit;
        padding: 1px;
        background: linear-gradient(180deg, rgba(255,255,255,0.5) 0%, rgba(255,255,255,0.15) 40%, rgba(255,255,255,0) 60%, rgba(255,255,255,0.15) 80%, rgba(255,255,255,0.5) 100%);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events: none;
        opacity: 0.7;
        transition: opacity 0.3s ease;
    }
    .stButton > button[kind="primary"]:hover::before { opacity: 1; }
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
    }
    .stButton > button[kind="primary"]:disabled::before { opacity: 0.2; }

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
        background-blend-mode: luminosity;
        backdrop-filter: blur(20px) saturate(180%);
        border: none;
        box-shadow: inset 0 1px 1px rgba(255,255,255,0.1), 0 4px 20px rgba(0,0,0,0.06);
        position: relative;
        overflow: hidden;
        padding: 0.8rem; border-radius: 14px;
        margin-bottom: 1.2rem; text-align: center;
        transition: all 0.4s ease;
    }
    .result-header-glass::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: inherit;
        padding: 1px;
        background: linear-gradient(180deg, rgba(255,255,255,0.35) 0%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0.35) 100%);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events: none;
        opacity: 0.5;
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
        background-blend-mode: luminosity;
        backdrop-filter: blur(16px) saturate(150%);
        border: none;
        box-shadow: inset 0 1px 1px rgba(255,255,255,0.08), 0 4px 16px rgba(0,0,0,0.05);
        position: relative;
        overflow: hidden;
        padding: 1rem; border-radius: 14px;
        transition: all 0.4s ease;
        animation: slideInUp 0.5s ease-out both;
    }
    .result-glass::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: inherit;
        padding: 1px;
        background: linear-gradient(180deg, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0.3) 100%);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events: none;
        opacity: 0.4;
        transition: opacity 0.3s ease;
    }
    .result-glass:hover::before { opacity: 0.7; }
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
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. 文本解析函数
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
        return text.strip() if text.strip() else None
    except Exception: return None

def extract_cities_from_resume(text):
    if not text: return []
    found_cities = [city for city in ALL_CITIES if city in text]
    return list(dict.fromkeys(found_cities))[:3]

# ==========================================
# 5. 会话状态初始化
# ==========================================
for key, val in [
    ("app_stage", "input"), ("loading", False),
    ("resume_content", ""), ("jd_content", ""),
    ("detected_cities", []), ("city_scope", "国内"),
    ("selected_province", None), ("selected_city", None),
    ("custom_city", ""), ("province_city_selected", False)
]:
    if key not in st.session_state: st.session_state[key] = val

# ==========================================
# 6. 渲染逻辑：数据源输入页
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
        st.selectbox("意向公司", ["大厂", "独角兽", "国央企", "外企/跨国公司", "中小型科技公司", "不限"], label_visibility="collapsed")
        st.selectbox("大模型", ["DeepSeek-V3 (推荐)", "GPT-4o", "Claude 3.5"], label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # === 卡片3: 目标岗位JD ===
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">🎯 目标岗位 JD</div>', unsafe_allow_html=True)
        jd_method = st.radio("提供方式", ["手动粘贴文本", "上传 JD 文档"], horizontal=True, label_visibility="collapsed")
        jd_text_raw = ""
        if jd_method == "手动粘贴文本":
            st.markdown('<div class="hint-text">请把招聘软件上的职位描述(JD)粘贴在这里</div>', unsafe_allow_html=True)
            jd_text_raw = st.text_area("粘贴JD", placeholder="在此粘贴职位描述...", height=100, label_visibility="collapsed")
        else:
            uploaded_jd = st.file_uploader("上传JD", type=["pdf", "docx"], label_visibility="collapsed")
            if uploaded_jd: jd_text_raw = extract_text(uploaded_jd)
        st.markdown('</div>', unsafe_allow_html=True)

        # === 卡片4: 投递意向地区（省份-城市级联）===
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📍 投递意向地区</div>', unsafe_allow_html=True)

        if st.session_state.detected_cities:
            cities_str = "、".join(st.session_state.detected_cities)
            st.markdown(f'<div class="city-detected">🎯 已从简历检测到：{cities_str}</div>', unsafe_allow_html=True)
            selected_from_resume = st.selectbox("确认城市", st.session_state.detected_cities + ["其他（手动输入）"], label_visibility="collapsed")
            if selected_from_resume == "其他（手动输入）":
                st.session_state.city_scope = "其他"
                st.text_input("输入意向城市", placeholder="例如：三亚", label_visibility="collapsed", key="custom_city_input_resume")
            else:
                st.session_state.selected_city = selected_from_resume
                st.session_state.city_scope = "国内"
        else:
            st.markdown('<div class="city-not-detected">○ 未检测到意向城市，请手动选择</div>', unsafe_allow_html=True)

            scope = st.radio("地区范围", ["国内", "海外"], horizontal=True, label_visibility="collapsed", key="scope_radio")
            st.session_state.city_scope = scope

            if scope == "国内":
                # 省份选择
                selected_province = st.selectbox("选择省份", ALL_PROVINCES, label_visibility="collapsed", key="province_select")
                st.session_state.selected_province = selected_province

                # 城市选择（基于省份）
                if selected_province and selected_province in PROVINCE_CITY_MAP:
                    cities_in_province = PROVINCE_CITY_MAP[selected_province]
                    selected_city = st.selectbox("选择城市", cities_in_province, label_visibility="collapsed", key="city_select")
                    st.session_state.selected_city = selected_city
            else:
                country = st.selectbox("选择国家/地区", OVERSEAS_COUNTRIES, label_visibility="collapsed", key="country_select")
                if country == "其他":
                    custom_overseas = st.text_input("输入意向城市/国家", placeholder="例如：迪拜", label_visibility="collapsed", key="custom_overseas_input")
                    st.session_state.custom_city = custom_overseas
                    st.session_state.selected_city = custom_overseas
                else:
                    st.session_state.selected_city = country
        st.markdown('</div>', unsafe_allow_html=True)

    # 提交区域
    st.markdown("---")
    has_res = uploaded_resume is not None
    has_jd = bool(jd_text_raw and len(jd_text_raw.strip()) >= 10)

    col_s, col_b = st.columns([1, 2])
    col_s.markdown('<div class="status-chip chip-ready">✓ 信息已就绪</div>' if (has_res and has_jd) else '<div class="status-chip chip-wait">○ 待完善输入源数据</div>', unsafe_allow_html=True)

    with col_b:
        if st.button("✨ 一键开始智能匹配", use_container_width=True, disabled=not (has_res and has_jd)):
            st.session_state.resume_content = extract_text(uploaded_resume)
            st.session_state.jd_content = jd_text_raw
            st.session_state.loading = True
            st.rerun()

# ==========================================
# 7. 加载页
# ==========================================
elif st.session_state.loading:
    p_text, p_bar = st.empty(), st.progress(0)
    stages = [("📄 解析简历结构", 30), ("🎯 分析岗位 JD", 60), ("🤖 生成匹配策略", 90), ("✨ 即将完成", 100)]
    for i in range(100):
        time.sleep(0.015)
        p_bar.progress(i + 1)
        for text, threshold in stages:
            if i < threshold:
                p_text.markdown(f"<div style='text-align:center; color:rgba(255,255,255,0.8); font-weight:500; font-size:0.9rem;'>{text} {i+1}%</div>", unsafe_allow_html=True)
                break
    st.session_state.loading, st.session_state.app_stage = False, "result"
    st.rerun()

# ==========================================
# 8. 结果页
# ==========================================
elif st.session_state.app_stage == "result":

    st.markdown('<div class="result-header-glass"><h3>🔍 智能解析对比看板</h3></div>', unsafe_allow_html=True)
    st.markdown('<div class="step-track"><div class="step-node completed">✓</div><div class="step-line active"></div><div class="step-node active">2</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="success-glass">🎉 Agent 已完成深度解析，以下是实时多维对比视图</div>', unsafe_allow_html=True)

    if st.button("← 返回修改数据", key="back_btn"):
        st.session_state.app_stage = "input"
        st.rerun()

    res_col1, res_col2 = st.columns(2, gap="large")

    with res_col1:
        st.markdown('<div class="result-glass">', unsafe_allow_html=True)
        st.markdown('<div class="result-title">📄 简历解析结果</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-meta">{len(st.session_state.resume_content)} 字符 · 数据已完全解构</div>', unsafe_allow_html=True)
        st.text_area("R", value=st.session_state.resume_content, height=380, disabled=True, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    with res_col2:
        st.markdown('<div class="result-glass">', unsafe_allow_html=True)
        st.markdown('<div class="result-title">🎯 目标岗位 JD</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-meta">{len(st.session_state.jd_content)} 字符 · 上下文已注入容器</div>', unsafe_allow_html=True)
        st.text_area("J", value=st.session_state.jd_content, height=380, disabled=True, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='footer-hint'>💡 对比视图已生成，后续可接入大模型进行智能润色与匹配分析</div>", unsafe_allow_html=True)
