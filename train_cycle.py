from dual_network import dual_network
from self_play import self_play
from train_network import train_network
from evaluate_network import evaluate_network, update_best_player

# 듀얼 네트워크 생성
dual_network()

for i in range(100):
    print('Train', i + 1, '====================')

    # 셀프 플레이 파트
    self_play()

    # 파라미터 갱신 파트
    train_network()

    # 신규 파라미터 평가 파트
    evaluate_network()