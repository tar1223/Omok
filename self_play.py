from game import State
from pv_mcts import pv_mcts_scores
from dual_network import DN_OUTPUT_SIZE
from datetime import datetime
import tensorflow as tf
import numpy as np
import pickle
import os

# 파라미터 준비
SP_GAME_COUNT = 50 # 셀프 플레이를 수행할 게임 수
SP_TEMPERATURE = 1.0 # 볼츠만 분포의 온도 파라미터

# 선 수를 둔 플레이어의 가치
def first_player_value(ended_state):
    # 1: 선 수 플레이어 승리, -1: 선 수 플레이어 패배, 0: 무승부
    if ended_state.is_lose():
        return -1 if ended_state.first_player else 1
    
    return 0

# 학습 데이터 저장
def write_data(history):
    now = datetime.now()
    os.makedirs('./data/', exist_ok = True) # 폴더가 없는 경우에는 생성
    path = './data/{:04}{:02}{:02}{:02}{:02}{:02}.history'.format(now.year, now.month, now.day, now.hour, now.minute, now.second)
    with open(path, mode = 'wb') as f:
        pickle.dump(history, f)

# 게임 실행
def play(model):
    # 학습 데이터
    history = []

    # 상태 생성
    state = State()

    while True:
        # 게임 종료시
        if state.is_done():
            break
        
        # 둘 수 있는 수의 확률 분포 얻기
        actions, scores = pv_mcts_scores(model, state, SP_TEMPERATURE)

        # 학습 데이터에 상태와 정책 추가
        policies = [0] * DN_OUTPUT_SIZE

        for action, policy in zip(actions, scores):
            policies[action] = policy
        
        history.append([state.pieces_array(), policies, None])

        # 행동 얻기
        action = np.random.choice(actions, p = scores)

        # 다음 상태 얻기
        state = state.next(action)
    
    value = first_player_value(state)

    for i in range(len(history)):
        history[i][2] = value
        value = -value
    
    return history

# 셀프 플레이
def self_play():
    # 학습 데이터
    history = []

    # 베스트 플레이어 모델 로드
    model = tf.keras.models.load_model('./model/best.h5')

    # 여러 차례 게임 실행
    for i in range(SP_GAME_COUNT):
        # 게임 실행
        h = play(model)
        history.extend(h)

        #출력
        print('\rSelfPlay {}/{}'.format(i + 1, SP_GAME_COUNT), end = '')
    
    print('')

    # 학습 데이터 저장
    write_data(history)

    # 모델 삭제
    tf.keras.backend.clear_session()
    del model

if __name__ == '__main__':
    self_play()