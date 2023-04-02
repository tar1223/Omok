from game import State
from pv_mcts import pv_mcts_action
from PIL import Image, ImageTk
import tensorflow as tf
import tkinter as tk
import time

# 베스트 플레이어 모델 로드
model = tf.keras.models.load_model('./model/best.h5')

# 게임 UI 정의
class GameUI(tk.Frame):
    # 초기화
    def __init__(self, master = None, model = None):
        tk.Frame.__init__(self, master)
        self.master.title('오목')

        # 게임 상태 생성
        self.state = State()
        
        # PV MCTS를 활용한 행동 선택을 따르는 함수 생성
        self.next_action = pv_mcts_action(model, 0.0)

        # 이미지 준비
        self.board = ImageTk.PhotoImage(Image.open('board.png'))
        self.black = ImageTk.PhotoImage(Image.open('black.png'))
        self.white = ImageTk.PhotoImage(Image.open('white.png'))
        self.forbidden = ImageTk.PhotoImage(Image.open('forbidden.png'))

        # 캔버스 생성
        self.c = tk.Canvas(self, width = 600, height = 600, highlightthickness = 0)
        self.c.bind('<Button-1>', self.turn_of_human)
        self.c.pack()

        # 그림 갱신
        self.on_draw()
    
    # 사람의 턴
    def turn_of_human(self, event):
        # 게임 종료 시
        if self.state.is_done():
            self.state = State()
            self.on_draw()
            return
        
        # 선 수가 아닌 경우
        if not self.state.first_player:
            return
        
        # 클릭 위치를 행동으로 변화
        x = int(event.x / 40)
        y = int(event.y / 40)

        if x < 0 or 14 < x or y < 0 or 14 < y: # 범위 외
            return

        action = x + y * 15

        # 둘 수 있는 수가 아닌 경우
        if not (action in self.state.legal_actions()):
            return

        # 다음 상태 얻기
        self.state = self.state.next(action)
        self.on_draw()

        # AI의 턴
        self.master.after(1, self.turn_of_ai)
    
    # AI의 턴
    def turn_of_ai(self):
        start = time.time()
        # 게임 종료 시
        if self.state.is_done():
            return

        # 행동 얻기
        action = self.next_action(self.state)

        print(time.time() - start)

        # 다음 상태 얻기
        self.state = self.state.next(action)
        self.on_draw()

    # 돌 그리기
    def draw_piece(self, index, first_player):
        x = (index % 15) * 40
        y = int(index / 15) * 40

        if first_player:
             self.c.create_image(x, y, image = self.black, anchor = tk.NW)
        else:
            self.c.create_image(x, y, image = self.white, anchor = tk.NW)
    
    def draw_forbidden_piece(self, index):
        x = (index % 15) * 40
        y = int(index / 15) * 40

        self.c.create_image(x, y, image = self.forbidden, anchor = tk.NW)

    # 화면 갱신
    def on_draw(self):
        self.c.delete('all')
        self.c.create_image(0, 0, image = self.board, anchor = tk.NW)

        for i in range(225):
            if self.state.pieces[i] == 1:
                self.draw_piece(i, self.state.first_player)
            elif i in self.state.forbidden_actions:
                self.draw_forbidden_piece(i)
            elif self.state.enemy_pieces[i] == 1:
                self.draw_piece(i, not self.state.first_player)

# 게임 UI 실행
f = GameUI(model = model)
f.pack()
f.mainloop()