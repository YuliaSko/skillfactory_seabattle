from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class Ship:
    def __init__(self, bow, l,  v):
        self.bow = bow
        self.l = l
        self.v = v
        self.lives = l

    @property
    def dots(self):
        ship_dots = []

        for i in range(self.l):
            dir_x = self.bow.x
            dir_y = self.bow.y

            if self.v == 0:
                dir_x += i

            elif self.v == 1:
                dir_y += i

            ship_dots.append(Dot(dir_x, dir_y))

        return ship_dots

    def shooting(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size

        self.count = 0

        self.field = [['○'] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def __str__(self):
        res = ''
        res += '  | 1 | 2 | 3 | 4 | 5 | 6 |'

        for i, row in enumerate(self.field):
            res += f'\n{i + 1} | ' + ' | '.join(row) + ' |'

        if self.hid:
            res = res.replace('■', '○')

        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)
        ]

        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = '•'

                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException

        for d in ship.dots:
            self.field[d.x][d.y] = '■'
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if d in self.busy:
            raise BoardUsedException

        if self.out(d):
            raise BoardOutException

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooting(d):
                ship.lives -= 1
                self.field[d.x][d.y] = 'X'
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Поздравляю! Корабль уничтожен!")
                    return False
                else:
                    print('Корабль подбит!')
                    return True

        self.field[d.x][d.y] = '•'
        print('Увы, промах..')
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class User(Player):
    def ask(self):
        while True:
            coord = input('Введите координаты:').split()

            if len(coord) != 2:
                print('Вам нужно ввести 2 числа')
                continue

            x, y = coord

            if not (x.isdigit()) or not (y.isdigit()):
                print('Ведите числа!')
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход компьютера: {d.x+1}, {d.y+1}')
        return d


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        comp = self.random_board()
        comp.hid = True

        self.user = User(pl, comp)
        self.ai = AI(comp, pl)

    def try_board(self):
        numb_ship = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in numb_ship:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None

                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))

                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass

        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print('*' * 19)
        print(' Добро пожаловать! ')
        print('  Давайте сыграем  ')
        print('      в игру       ')
        print('    МОРСКОЙ БОЙ    ')
        print('*' * 19)
        print('Правила ввода:  x y')
        print(' х - номер строки  ')
        print(' у - номер столбца ')

    def print_board(self):
        print('-' * 20)
        print('Поле игрока:')
        print(self.user.board)
        print('-' * 20)
        print('Поле компьютера:')
        print(self.ai.board)
        print('-' * 20)

    def loop(self):
        num = 0
        while True:
            self.print_board()
            if num % 2 == 0:
                print('Ходит игрок')
                repeat = self.user.move()
            else:
                print('Ходит компьютер')
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print('Победил игрок!')
                break

            if self.user.board.count == 7:
                print('Победил компьютер!')
                break

            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
print(g.start())
