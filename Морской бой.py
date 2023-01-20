from random import randint


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Не стреляйте за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Не стреляйте в одну и ту же клетку"


class BoardWrongShipException(BoardException):
    def __str__(self):
        return "Выберите другую позицию корабля"


class Ship:
    def __init__(self, position, length, direction):
        self.position = position
        self.length = length
        self.direction = direction
        self.live = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            current_x = self.position.x
            current_y = self.position.y

            if self.direction == 0:
                current_x += i

            elif self.direction == 1:
                current_y += i

            ship_dots.append(Dot(current_x, current_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hide=False, size=6):
        self.size = size
        self.hide = hide

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def add_ship(self, ship):

        for point in ship.dots:
            if self.out(point) or point in self.busy:
                raise BoardWrongShipException()
        for point in ship.dots:
            self.field[point.x][point.y] = "■"
            self.busy.append(point)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        around = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for point in ship.dots:
            for pointx, pointy in around:
                current = Dot(point.x + pointx, point.y + pointy)
                if not (self.out(current)) and current not in self.busy:
                    if verb:
                        self.field[current.x][current.y] = "*"
                    self.busy.append(current)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hide:
            res = res.replace("■", "O")
        return res

    def out(self, point):
        return not ((0 <= point.x < self.size) and (0 <= point.y < self.size))

    def shot(self, point):
        if self.out(point):
            raise BoardOutException()

        if point in self.busy:
            raise BoardUsedException()

        self.busy.append(point)

        for ship in self.ships:
            if point in ship.dots:
                ship.live -= 1
                self.field[point.x][point.y] = "X"
                if ship.live == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожена!")
                    return False
                else:
                    print("Есть попадание!")
                    return True

        self.field[point.x][point.y] = "T"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        point = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход противника: {point.x + 1} {point.y + 1}")
        return point


class User(Player):
    def ask(self):
        while True:
            cords = input("Цельтесь: ").split()

            if len(cords) != 2:
                print(" Введите координаты выстрела! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        gamer = self.random_board()
        enemy = self.random_board()
        enemy.hide = True

        self.ai = AI(enemy, gamer)
        self.us = User(gamer, enemy)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
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

    def greet(self):
        print("-------------------")
        print("  Морской Бой ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


game = Game()
game.start()