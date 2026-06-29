"""
state.py - SessionState 封装
Phase 1 MVP：统一管理 Streamlit session_state，提供类型安全的访问接口
"""

from typing import Any, Optional, Dict
import streamlit as st

# ==========================================
# 1. 状态定义（类型安全）
# ==========================================
class AppState:
    """应用状态枚举，避免硬编码字符串"""
    APP_STAGE = "app_stage"                    # 当前页面: input / loading / result
    LOADING = "loading"                        # 是否加载中
    RESUME_CONTENT = "resume_content"          # 简历文本
    JD_CONTENT = "jd_content"                  # JD 文本
    DETECTED_CITIES = "detected_cities"        # 检测到的城市
    CITY_SCOPE = "city_scope"                  # 地区范围: 国内/海外
    SELECTED_PROVINCE = "selected_province"    # 选中省份
    SELECTED_CITY = "selected_city"              # 选中城市
    CUSTOM_CITY = "custom_city"                # 自定义城市
    PROVINCE_CITY_SELECTED = "province_city_selected"  # 是否已选择省市

    # Phase 1 MVP 新增状态
    OPTIMIZED_RESUME = "optimized_resume"      # LLM 优化后的简历
    OPTIMIZATION_HISTORY = "optimization_history"  # 优化历史记录
    CURRENT_MODEL = "current_model"            # 当前大模型
    TARGET_COMPANY_TYPE = "target_company_type" # 目标公司类型
    MATCH_SCORE = "match_score"                # 匹配分数
    ANALYSIS_RESULT = "analysis_result"          # 完整分析结果
    SESSION_ID = "session_id"                  # 会话 ID（用于 Memory）

# ==========================================
# 2. 获取状态值（带默认值）
# ==========================================
def get_state(key: str, default: Any = None) -> Any:
    """
    安全获取 session_state 值

    实现方式：
    1. 检查 key 是否在 session_state 中
    2. 如果存在，返回对应值
    3. 如果不存在，返回默认值（不写入 session_state）

    Args:
        key: 状态键名
        default: 默认值

    Returns:
        状态值或默认值
    """
    return st.session_state.get(key, default)

# ==========================================
# 3. 设置状态值
# ==========================================
def set_state(key: str, value: Any) -> None:
    """
    安全设置 session_state 值

    实现方式：
    1. 直接赋值给 session_state[key]
    2. Streamlit 会自动持久化到浏览器会话

    Args:
        key: 状态键名
        value: 状态值
    """
    st.session_state[key] = value

# ==========================================
# 4. 批量设置状态
# ==========================================
def set_states(state_dict: Dict[str, Any]) -> None:
    """
    批量设置多个状态值

    Args:
        state_dict: 状态字典 {key: value}
    """
    for key, value in state_dict.items():
        set_state(key, value)

# ==========================================
# 5. 清空状态（保留指定键）
# ==========================================
def clear_state(keep_keys: Optional[list] = None) -> None:
    """
    清空 session_state，可选保留指定键

    Args:
        keep_keys: 需要保留的键列表
    """
    keep = keep_keys or []
    keys_to_remove = [k for k in list(st.session_state.keys()) if k not in keep]
    for key in keys_to_remove:
        del st.session_state[key]

# ==========================================
# 6. 初始化所有状态（幂等操作）
# ==========================================
def init_all_state() -> None:
    """
    初始化所有应用状态（仅在不存在时设置）

    实现方式：
    1. 遍历所有默认状态
    2. 如果 session_state 中不存在，则设置默认值
    3. 保证应用启动时状态完整
    """
    defaults = {
        AppState.APP_STAGE: "input",
        AppState.LOADING: False,
        AppState.RESUME_CONTENT: "",
        AppState.JD_CONTENT: "",
        AppState.DETECTED_CITIES: [],
        AppState.CITY_SCOPE: "国内",
        AppState.SELECTED_PROVINCE: None,
        AppState.SELECTED_CITY: None,
        AppState.CUSTOM_CITY: "",
        AppState.PROVINCE_CITY_SELECTED: False,
        AppState.OPTIMIZED_RESUME: "",
        AppState.OPTIMIZATION_HISTORY: [],
        AppState.CURRENT_MODEL: "DeepSeek-V3",
        AppState.TARGET_COMPANY_TYPE: "不限",
        AppState.MATCH_SCORE: 0,
        AppState.ANALYSIS_RESULT: {},
        AppState.SESSION_ID: "default_session",
    }

    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# ==========================================
# 7. 获取完整状态快照（用于调试/日志）
# ==========================================
def get_state_snapshot() -> Dict[str, Any]:
    """
    获取当前所有状态的快照（排除敏感信息）

    Returns:
        状态字典（敏感内容截断）
    """
    snapshot = {}
    sensitive_keys = [AppState.RESUME_CONTENT, AppState.JD_CONTENT, AppState.OPTIMIZED_RESUME]

    for key in st.session_state.keys():
        value = st.session_state[key]
        if key in sensitive_keys and isinstance(value, str):
            snapshot[key] = f"{value[:50]}... ({len(value)} chars)"
        else:
            snapshot[key] = value

    return snapshot
