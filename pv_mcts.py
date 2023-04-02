from game import State
from dual_network import DN_INPUT_SHAPE
from math import sqrt
from pathlib import Path
import tensorflow as tf
import numpy as np

# MCTS 트리 반복 횟수
PV_EVALUATE_COUNT = 800 # 추론 1회당 시물레이션 횟수

# Dual Network로 예측
def predict(model, state):
    # 예측을 위한 입력 데이터 형태 변환
    a, b, c = DN_INPUT_SHAPE
    x = np.array(state.pieces_array())
    x = x.reshape(c, a, b).transpose(1, 2, 0).reshape(1, a, b, c) # 첫번째 채널에는 pieces, 두번째 채널에는 enemy_pieces, 세번째 채널에는 흑돌 백돌 판별

    # 예측
    y = model.predict(x, batch_size = 1, verbose = 0)

    # 정책 얻기
    policies = y[0][0][list(state.legal_actions())] # 둘 수 있는 수만
    policies /= sum(policies) if sum(policies) else 1 # 합계 1의 확률 분포로 변환

    # 가치 얻기
    value = y[1][0][0]
    return policies, value

# 노드 리스트를 시행 횟수 리스트로 반환
def nodes_to_scores(nodes):
    scores = []

    for c in nodes:
        scores.append(c.n)

    return scores

# 몬테카를로 트리 탐색 스코어 얻기
def pv_mcts_scores(model, state, temperature):
    # 몬테카를로 트리 탐색 노드 정의
    class Node:
        # 노드 초기화
        def __init__(self, state, p, depth = 0):
            self.state = state # 상태
            self.p = p # 정책
            self.w = 0 # 가치 누계
            self.n = 0 # 시행 횟수
            self.depth = depth
            self.child_nodes = None # 자식 노드군
        
        # 국면 가치 계산
        def evaluate(self):
            # 게임 종료시
            if self.state.is_done():
                # 승패 결과로 가치 얻기
                value = -1 if self.state.is_lose() else 0

                # 누계 가치와 시행 횟수 갱신
                self.w += value
                self.n += 1

                return value

            # 자식 노드가 존재하지 않는 경우
            if not self.child_nodes:
                # 뉴럴 네트워크 추론을 활용한 정책과 가치 얻기
                policies, value = predict(model, self.state)

                # 누계 가치와 시행 횟수 갱신
                self.w += value
                self.n += 1

                # 자식 노드 전개
                self.child_nodes = {}
                for action, policy in zip(self.state.legal_actions(), policies):
                    self.child_nodes[action] = Node(self.state.next(action), policy, self.depth + 1)

                return value
            # 자식 노드가 존재하는 경우
            else:
                # 아크 평가값이 가장 큰 자식 노드의 평가로 가치 얻기
                value = -self.next_child_node().evaluate()

                # 누계 가치와 시행 횟수 갱신
                self.w += value
                self.n += 1

                return value
        
        '''
        아크 평가값
        식: (-child_node.w / child_node.n if child_node.n else 0.0) + C_PUCT * child_node.p * sqrt(t) / (1 + child_node.n)
        (-child_node.w / child_node.n if child_node.n else 0.0): 성공률
        C_PUCT: 밸런스 조정 정수
        child_node.p * sqrt(t) / (1 + child_node.n): 바이어스
        w: 이 노드의 누계 가치
        n: 이 노드의 시행 횟수
        Cpuct: 승률과 수의 예측 확률 * 바이어스 균형을 조정하기 위한 상수
        p: 수의 확률 분포
        t: 시행 횟수 누계
        아크 평가값이 가장 큰 자식 노드를 선택하면서 수를 진행
        '''
        # 아크 평가가 가장 큰 자식 노드 얻기
        def next_child_node(self):
            # 아크 평가 계산
            C_PUCT = 1.0
            t = sum(nodes_to_scores(self.child_nodes.values()))
            pucb_values = {}

            for action, child_node in self.child_nodes.items():
                pucb_values[action] = (-child_node.w / child_node.n if child_node.n else 0.0) + C_PUCT * child_node.p * sqrt(t) / (1 + child_node.n)
            
            # 아크 평가값이 가장 큰 자식 노드 반환
            return self.child_nodes[max(pucb_values, key = pucb_values.get)]

    # 현재 국면의 노드 생성
    root_node = Node(state, 0)

    # 여러 차례 평가 실행
    for _ in range(PV_EVALUATE_COUNT):
        root_node.evaluate()

    actions = list(root_node.child_nodes.keys())

    # 둘 수 있는 수의 확률 분포
    scores = nodes_to_scores(root_node.child_nodes.values())

    if temperature == 0: # 최댓값인 경우에만 1
        action = np.argmax(scores)
        scores = np.zeros(len(scores))
        scores[action] = 1
    else: # 볼츠만 분포를 기반으로 분산 추가
        scores = boltzman(scores, temperature)
    
    return actions, scores

# 몬테카를로 트리 탐색을 활용한 행동 선택
def pv_mcts_action(model, temperature = 0):
    def pv_mcts_action(state):
        actions, scores = pv_mcts_scores(model, state, temperature)

        return np.random.choice(actions, p = scores)
            
    return pv_mcts_action

'''
boltzman: 둘 수 있는 수의 확률 분포에 분산을 부가한 값을 반환
식: xs = [x ** (1 / temperature) for x in xs]
    return [x / sum(xs) for x in xs]
x: 특정한 상태에서 특정한 행동을 선책할 확률의 1/γ 제곱
sum(xs): 특정한 상태에서 특정한 행동을 선책할 확률의 1/γ 제곱의 누계
γ: 온도 파라미터
'''
# 볼츠만 분포 # 확률을 낮추어 다른 자식 노드로 갈 확률 높이기
def boltzman(xs, temperature):
    xs = [x ** (1 / temperature) for x in xs]

    return [x / sum(xs) for x in xs]

# 동작 확인
if __name__ == '__main__':
    # 모델 로드
    path = sorted(Path('./model').glob('*.h5'))[-1]
    model = tf.keras.models.load_model(str(path))

    # 상태 생성
    state = State()

    # 몬테카를로 트리 탐색을 활용해 행동을 얻는 함수 생성
    next_action = pv_mcts_action(model, 1.0)

    # 게임 종료 시까지 반복
    while True:
        # 게임 종료 시
        if state.is_done():
            break

        # 행동 얻기
        action = next_action(state)

        # 다음 상태 얻기
        state = state.next(action)

        # 문자열 출력
        print(state)