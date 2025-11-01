import pandas as pd
import yaml
import os
import numpy as np

# --- 경로 설정 ---
# 2단계에서 생성된 미래 부하 예측 파일
FORECAST_PATH = '../02_AI_Model_Development/analytics_output/future_load_forecast.csv'
# 설정 파일 경로
CONFIG_PATH = './config.yaml'
# 시뮬레이션 결과 저장 경로
OUTPUT_PATH = './scaling_simulation_results.csv'

def load_config(config_path):
    """YAML 설정 파일을 로드합니다."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def calculate_required_servers(forecast_data, config):
    """
    AI 예측 부하를 기반으로 필요한 서버 인스턴스 수를 계산합니다.
    """
    # 설정값 로드
    capacity = config['SERVER_CAPACITY']
    threshold = config['SCALING_THRESHOLD']
    
    max_api = capacity['MAX_API_PER_SERVER']
    min_servers = capacity['MIN_SERVERS']
    max_servers = capacity['MAX_SERVERS']
    expansion_factor = threshold['EXPANSION_BUFFER_PERCENT']

    # 1. 확장 임계치 계산 (안전 버퍼 포함)
    # 실제 확장 기준 = MAX_API_PER_SERVER * 1.10 (500 * 1.10 = 550)
    expansion_threshold = max_api * expansion_factor

    # 2. 필요한 서버 수 계산 (올림 처리)
    # 필요한 서버 수 = ceil(예측 부하 / 확장 임계치)
    required_servers = np.ceil(forecast_data['yhat'] / expansion_threshold).astype(int)

    # 3. 최소/최대 제한 적용
    required_servers = np.clip(required_servers, min_servers, max_servers)

    # 4. 결과 DataFrame 생성
    results = pd.DataFrame({
        'ds': forecast_data['ds'],
        'predicted_load': forecast_data['yhat'].round(0).astype(int),
        'required_servers_raw': required_servers,
        'scaling_action': 'No Change', # 초기 액션
        'final_servers': required_servers[0] # 초기 서버 수는 첫 번째 필요한 서버 수로 설정 (단순화)
    })
    
    # 5. 동적 확장/축소 로직 적용 (시간의 흐름 시뮬레이션)
    current_servers = min_servers # 시뮬레이션 시작 시 최소 서버로 가정
    contraction_counter = 0 # 축소 지연 카운터

    for i in range(len(results)):
        required = results.loc[i, 'required_servers_raw']
        action = 'No Change'
        
        # 확장 로직
        if required > current_servers:
            action = f"SCALE_UP: {current_servers} -> {required}"
            current_servers = required
            contraction_counter = 0 # 확장 시 축소 카운터 초기화
            
        # 축소 로직 (지연 시간 적용)
        elif required < current_servers:
            # 현재 서버당 부하가 축소 임계치 미만이고,
            # 축소 임계치 시간 이상 지속될 경우에만 축소
            if results.loc[i, 'predicted_load'] / current_servers < threshold['CONTRACTION_THRESHOLD']:
                contraction_counter += 1
                if contraction_counter >= threshold['CONTRACTION_LAG_HOURS']:
                    action = f"SCALE_DOWN: {current_servers} -> {required}"
                    current_servers = required
                    contraction_counter = 0
                else:
                    action = f"Check Contraction ({contraction_counter}h)"
            else:
                # 부하는 낮지만 임계치 미만이 아닌 경우 카운터 초기화
                contraction_counter = 0 
        
        results.loc[i, 'scaling_action'] = action
        results.loc[i, 'final_servers'] = current_servers

    return results[['ds', 'predicted_load', 'final_servers', 'scaling_action']]

if __name__ == "__main__":
    
    # 1. 라이브러리 설치 확인 (yaml을 읽기 위해 필요)
    try:
        import yaml
    except ImportError:
        print("❌ 오류: yaml 라이브러리가 설치되지 않았습니다. 'pip install pyyaml'을 실행하세요.")
        exit()

    # 2. 설정 및 데이터 로드
    config = load_config(CONFIG_PATH)
    if not os.path.exists(FORECAST_PATH):
        print(f"❌ 오류: 예측 파일 '{FORECAST_PATH}'을 찾을 수 없습니다. 2단계 스크립트를 먼저 실행하세요.")
        exit()
        
    forecast_df = pd.read_csv(FORECAST_PATH)
    forecast_df['ds'] = pd.to_datetime(forecast_df['ds'])
    
    print("✅ AI 예측 데이터 및 설정 로드 완료.")
    
    # 3. 서버 계산 및 시뮬레이션 실행
    simulation_results = calculate_required_servers(forecast_df, config)
    
    # 4. 결과 저장
    simulation_results.to_csv(OUTPUT_PATH, index=False)
    
    print("\n--- 📊 시뮬레이션 결과 미리보기 (일부) ---")
    print(simulation_results.head(10))
    print(f"\n✅ 동적 확장 시뮬레이션 완료! 결과는 '{OUTPUT_PATH}'에 저장되었습니다.")