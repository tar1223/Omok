from renju_rule import Renju
import random

class State():
    # 초기화
    def __init__(self, pieces = None, enemy_pieces = None, depth = 0):
        # 말의 배치
        self.pieces = pieces if pieces != None else [0] * 225
        self.enemy_pieces = enemy_pieces if enemy_pieces != None else [0] * 225

        # 게임의 깊이
        self.depth = depth

        # 금수 위치 정의
        self.renju = Renju(self.pieces, self.enemy_pieces)
        self.is_first_player()
        self.get_forbidden_actions()

    # 돌의 수 얻기
    def piece_count(self, pieces):
        count = 0

        for i in pieces:
            if i == 1:
                count += 1
        
        return count
    
    # 패배 여부 판정
    def is_lose(self):
        # 돌 5개 연결 여부 판정
        def is_comp(x, y, dx, dy):
            for _ in range(5):
                if y < 0 or 14 < y or x < 0 or 14 < x or self.enemy_pieces[x + y * 15] == 0:
                    return False
        
                x = x + dx
                y = y + dy

            return True
        
        # 패배 여부 판정
        for j in range(15):
            for i in range(15):
                if is_comp(i, j, 1, 0) or is_comp(i, j, 0, 1) or is_comp(i, j, 1, -1) or is_comp(i, j, 1, 1):
                    return True
        
        return False

    # 무승부 여부 판정
    def is_draw(self):
        return self.piece_count(self.pieces) + self.piece_count(self.enemy_pieces) == 225
    
    # 게임 종료 여부 판정
    def is_done(self):
        return self.is_lose() or self.is_draw()
    
    # 듀얼 네트워크 입력 배열
    def pieces_array(self):
        table_list = []
        table_list.append(self.pieces)
        table_list.append(self.enemy_pieces)
        if self.first_player:
            table_list.append([1] * 225)
        else:
            table_list.append([0] * 225)
        
        return table_list


    # 다음 상태 얻기
    def next(self, action):
        pieces = self.pieces.copy()
        pieces[action] = 1

        return State(self.enemy_pieces, pieces, self.depth + 1)

    # 금 수 리스트 얻기
    def get_forbidden_actions(self):
        actions = self.renju.get_forbidden_points() if self.first_player else []
        
        self.forbidden_actions = actions

    # 둘 수 있는 수의 리스트 얻기
    def legal_actions(self):
        actions = []

        for i in range(225):
            if self.pieces[i] == 0 and self.enemy_pieces[i] == 0:
                if i not in self.forbidden_actions:
                    actions.append(i)
        
        return actions

    # 선 수 여부 판정
    def is_first_player(self):
        self.first_player = self.depth % 2 == 0
    
    # 문자열 표시
    def __str__(self):
        bh = ('b', 'h') if self.first_player else ('h', 'b')
        str = ''

        for i in range(225):
            if self.pieces[i] == 1:
                str += bh[0]
            elif self.enemy_pieces[i] == 1:
                str += bh[1]
            elif i in self.forbidden_actions:
                str += 'x'
            else:
                str += '-'
            
            if i % 15 == 14:
                str += '\n'
        
        return str

# 랜덤 행동 선택
def random_action(state):
    legal_actions = state.legal_actions()

    return legal_actions[random.randint(0, len(legal_actions) - 1)]

if __name__ == '__main__':
    # 상태 생성
    state = State()

    # 게임 종료 시까지 반복
    while True:
        # 게임 종료 시
        if state.is_done():
            break
        
        # 다음 상태 얻기
        state = state.next(random_action(state))

        # 문자열 표시
        print(state)
        print()