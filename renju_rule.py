# 렌주룰
class Renju():
    def __init__(self, pieces, enemy_pieces):
        self.pieces = pieces
        self.enemy_pieces = enemy_pieces

        # 방향 정수
        self.dxy = ((-1, 0), (1, 0), (-1, 1), (1, -1), (0, 1), (0, -1), (-1, -1), (1, 1))

    # 연결되어 있는 돌의 수 얻기
    def comp_count(self, point, direction):
        temp_p = point
        cnt = 1

        for i in range(2):
            dx = self.dxy[direction * 2 + i][0]
            dy = self.dxy[direction * 2 + i][1]
            point = temp_p

            while True:
                point = point + dx + dy * 15

                if point < 0 or 224 < point or self.pieces[point] == 0:
                    break
                else:
                    cnt += 1
        
        return cnt

    # 연결되어 있는 돌이 5개인지 확인
    def is_five(self, point):
        for i in range(4):
            cnt = self.comp_count(point, i)

            if cnt == 5:
                return True
        
        return False

    # 연결되어 있는 돌이 6개인지 확인 (6목)
    def is_six(self, point):
        for i in range(4):
            cnt = self.comp_count(point, i)

            if cnt > 5:
                return True

        return False

    # 주어진 방향에서 열린 4인지 확인
    def four(self, point, direction):
        for i in range(2):
            open = self.is_open(point, direction * 2 + i)

            if open:
                if self.five(open, direction):
                    return True
        
        return False

    # 주어진 방향에 대해서 돌이 5개 이어져 있는지 확인
    def five(self, point, direction):
        if self.comp_count(point, direction) == 5:
            return True
        
        return False

    # 입력받은 방향에 대해서 빈 곳 반화
    def is_open(self, point, direction):
        dx = self.dxy[direction][0]
        dy = self.dxy[direction][1]

        while True:
            point = point + dx + dy * 15

            if point < 0 or 224 < point or self.pieces[point] != 1:
                break
        
        if 0 <= point and point <= 224 and self.pieces[point] == 0 and self.enemy_pieces[point] == 0:
            return point
        else:
            return None

    # 한 방향에 대해 열린 3이 있는지 확인
    def open_three(self, point, direction):
        for i in range(2):
            open = self.is_open(point, direction * 2 + i)

            if open:
                self.pieces[open] = 1

                if self.open_four(open, direction) == 1:
                    if not self.forbidden_point(open):
                        self.pieces[open] = 0

                        return True
                
                self.pieces[open] = 0
        
        return False

    # 한 방향에 대해 열린 4가 있는지 확인
    def open_four(self, point, direction):
        if self.is_five(point):
            return False
        
        cnt = 0

        for i in range(2):
            open = self.is_open(point, direction * 2 + i)

            if open:
                if self.five(open, direction):
                    cnt += 1
        
        if cnt == 2:
            if self.comp_count(point, direction) == 4:
                cnt = 1
        else:
            cnt = 0
        
        return cnt

    # 열린 3이 두개 이상이면 금 수 포함
    def double_three(self, point):
        cnt = 0
        self.pieces[point] = 1

        for i in range(4):
            if self.open_three(point, i):
                cnt += 1
        
        self.pieces[point] = 0

        if cnt >= 2:
            return True
        
        return False

    # 열린 4가 두개 이상이면 굼 수 포함
    def double_four(self, point):
        cnt = 0
        self.pieces[point] = 1

        for i in range(4):
            if self.open_four(point, i) == 2: # 한줄에 44 금 수인 경우
                cnt += 2
            elif self.four(point, i):
                cnt += 1
        
        self.pieces[point] = 0

        if cnt >= 2:
            return True
        
        return False

    # 금 수 위치 찾기
    def forbidden_point(self, point):
        if self.is_five(point):
            return False
        elif self.is_six(point):
            return True
        elif self.double_three(point) or self.double_four(point):
            return True
        
        return False

    # 모든 금 수 위치 반환    
    def get_forbidden_points(self):
        points = []

        for point in range(225):
            if self.pieces[point] or self.enemy_pieces[point]:
                continue
            if self.forbidden_point(point):
                points.append(point)
        
        return points