# 04_Frontend/ts_component/__init__.py

import os
import streamlit.components.v1 as components

# TypeScript 컴포넌트의 빌드 경로 설정
_RELEASE = True 
if not _RELEASE:
    _component_func = components.declare_component(
        "my_component",
        url="http://localhost:1234", # Parcel 개발 서버 주소
    )
else:
    # 최종 빌드된 파일 (index.html) 경로 설정
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/dist")
    _component_func = components.declare_component("my_component", path=build_dir)


def ts_feedback_simulator(current_load: int, key=None):
    """
    TypeScript 컴포넌트를 Streamlit 앱에 렌더링하고 서버 부하를 전달합니다.
    """
    component_value = _component_func(current_load=current_load, key=key, default=0)
    return component_value