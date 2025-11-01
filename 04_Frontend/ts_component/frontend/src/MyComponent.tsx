// 04_Frontend/ts_component/frontend/src/MyComponent.tsx

import React, { useEffect, useState } from "react"
import { StreamlitComponentBase, withStreamlitConnection, Streamlit } from "streamlit-component-lib"

// Streamlit에서 전달받는 인수를 props로 정의
interface ComponentProps {
  current_load: number;
}

/**
 * AI 서버 부하에 따른 실시간 자세 분석 피드백 컴포넌트입니다.
 */
class MyComponent extends StreamlitComponentBase<ComponentProps> {
  public render = (): React.ReactNode => {
    // 1. Streamlit Python 코드에서 전달받은 현재 부하 값을 가져옵니다.
    const currentLoad = this.props.args["current_load"] || 0;
    
    let feedback = "AI 자세 분석 준비 완료.";
    let style = { color: 'green', fontSize: '18px', fontWeight: 'bold' };
    let statusIcon = "✅";

    // 2. 부하 값에 따라 피드백 텍스트와 스타일을 변경하는 로직
    if (currentLoad > 1000) {
      feedback = "⚠️ 서버 부하 초과: 실시간 피드백 심각하게 지연! (장애 임박)";
      style.color = 'red';
      statusIcon = "🚨";
    } else if (currentLoad > 700) {
      feedback = "🟡 서버 부하 높음: 응답 속도 저하 예상 (피드백 지연)";
      style.color = '#FFA500'; // 주황색
      statusIcon = "🟡";
    } else {
      feedback = "🟢 양호: 실시간 피드백 원활.";
    }

    // 3. TypeScript/React 컴포넌트 렌더링
    return (
      <div style={{ padding: '15px', border: '2px solid #ddd', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
        <h4 style={{ margin: '0 0 10px 0' }}>{statusIcon} AI 자세 피드백 시뮬레이터 (TS)</h4>
        <p style={{ margin: '5px 0' }}>현재 시뮬레이션 부하: <span style={{ fontWeight: 'bold' }}>{currentLoad} Calls/h</span></p>
        <p style={style}>{feedback}</p>
        <button 
          onClick={() => {
            alert(`자세 분석 시작 명령 전송! 현재 부하: ${currentLoad}`);
            // Streamlit Python 쪽으로 상태 변경을 알릴 수도 있습니다. (선택 사항)
          }}
          style={{ padding: '8px 15px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          운동 시작 & 실시간 분석 요청
        </button>
      </div>
    )
  }
}

export default withStreamlitConnection(MyComponent)