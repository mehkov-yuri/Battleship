from random import choice
from random import randint
from time import sleep


class BoardException(Exception):
    pass


class OutOfBoardException(BoardException):
    def __str__(self):
        return "Введены координаты за пределом игрового поля"


class DoubleUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class ShipWrongException(BoardException):
    pass


class Ship:
    def __init__(self, head, lenght, direct=0):
        self.head = head
        self.lenght = lenght
        self.direct = direct
        self.hp = lenght

    def ship_dot(self):
        ship_dots = []
        for i in range(self.lenght):
            cord_x = self.head.x
            cord_y = self.head.y
            if self.direct == 0:
                cord_x += i
            else:
                cord_y += i
            ship_dots.append(Dot(cord_x, cord_y))
        return ship_dots


class Board:
    def __init__(self, visibl=False, size=6):
        self.visibl = visibl
        self.size = size
        self.ships = []
        self.destroy_ship_count = 0
        self.field = [['O'] * size for i in range(size)]
        self.busy_dots = []
        self.free_dots = []
        self.around = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for i in range(self.size):
            for j in range(self.size):
                self.free_dots.append(Dot(i, j))

    def __str__(self):
        fiel = ''
        fiel += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i in range(self.size):
            fiel += f'\n{i+1} | ' + ' | '.join(self.field[i]) + ' |'
        if self.visibl == False:
            fiel = fiel.replace("■", "O")
        fiel = fiel.replace("■", "\033[32m{}".format("■"))
        fiel = fiel.replace("X", "\033[31m{}".format("X"))
        fiel = fiel.replace("T", "\033[36m{}".format("T"))
        fiel = fiel.replace(".", "\033[33m{}".format("."))
        fiel = fiel.replace("O", "\033[37m{}".format("O"))
        fiel = fiel.replace("|", "\033[0m{}".format("|"))
        return fiel

    def __len__(self):
        return len(self.busy_dots)

    def contour(self, ship, vid):
        for cor in ship.ship_dot():
            for dx, dy in self.around:
                coord1 = Dot(int(cor.x) + int(dx), int(cor.y) + int(dy))
                if (coord1 not in self.busy_dots) and (coord1 in self.free_dots) and (self.coord_test(coord1)):
                    if vid:
                        self.field[coord1.x][coord1.y] = "."
                    self.busy_dots.append(coord1)
                    self.free_dots.remove(coord1)


    def ship_add(self, ship, vid):
        for i in ship.ship_dot():
            if (not self.coord_test(i)) or (i in self.busy_dots):
                raise ShipWrongException
        for i in ship.ship_dot():
            self.field[i.x][i.y] = "■"
            self.busy_dots.append(i)
            self.free_dots.remove(i)
        self.ships.append(ship)
        self.contour(ship, vid)

    def shot_uze(self, cord, vid):
        if not self.coord_test(cord):
            raise OutOfBoardException
        if cord in self.busy_dots:
            raise DoubleUsedException
        for ship in self.ships:
            if cord in ship.ship_dot():
                ship.hp -= 1
                self.field[cord.x][cord.y] = 'X'
                if ship.hp == 0:
                    self.free_dots.remove(cord)
                    self.contour(ship, vid)
                    self.destroy_ship_count += 1
                    print('Корабль уничтожен')
                    return False
                else:
                    print('Ранил')
                    self.free_dots.remove(cord)
                    return True
        self.field[cord.x][cord.y] = 'T'     # Почему именно 'T'? почему не '*', 'T' ведь выглядит не красиво
        self.free_dots.remove(cord)          # но раз так в задании то и ладно
        print('Промах')
        return False

    def coord_test(self, coord):
        return (0 <= coord.x <= self.size - 1) and (0 <= coord.y <= self.size - 1)

    def begin(self):
        self.busy_dots = []
        for i in range(self.size):
            for j in range(self.size):
                self.free_dots.append(Dot(i, j))


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def __repr__(self):
        return f'({self.x}, {self.y})'


class Game:
    def __init__(self, size=6):
        self.size = size
        self.auto = self.hello()
        self.player_board = self.create_board(True, self.auto)
        self.computer_board = self.create_board(False, True)
        self.player = Human(self.computer_board)
        self.bot = Computer(self.player_board)
        self.time = 0

    def hello(self):
        print('расставить корабли автоматически (y/n)?')
        s = input()
        if s == 'n':
            auto = False
            print('Введите координаты в формате: x y направление ')
            print('x - номер строки')
            print('у - номер столбца')
            print('направление: 1 - по горизонтали (вправо, по умолчанию), 0 - по вертикали (вниз)')
            print('направление по умолчанию - горизонтальное')
        else:
            auto = True
            print('Ввод координат осуществляется в формате: x y')
            print('x - номер строки')
            print('у - носер столбца')
        return auto

    def create_tru(self, visible, auto):
        ships_len = [3, 2, 2, 1, 1, 1, 1]
        board = Board(visible, self.size)
        for i in ships_len:
            count = 0
            while True:
                if auto:
                    vid = False
                    count += 1
                    if (count > 1000) or (len(board.free_dots) == 0):
                        return None
                    coor = choice(board.free_dots)
                    x, y = coor.x, coor.y
                    direct = randint(0, 1)
                    if (direct == 1) and (i != 1):
                        if (y + i) > self.size:
                            continue
                    else:
                        if (x + i) > self.size:
                            continue
                    ship = Ship(Dot(x, y), i, direct)
                else:
                    vid = True
                    while True:
                        print(board)
                        coor = input(f'Введите первую точку и направление {i} палубного корабля: ', ).split()
                        if len(coor) not in [2, 3]:
                            print('Ошибка ввода')
                            continue
                        elif len(coor) == 2:
                            coor.append('1')
                        x, y, direct = coor
                        if (not x.isdigit()) or (not y.isdigit()) or (not direct.isdigit()):
                            print(" Введите числа! ")
                            continue
                        x, y, direct = int(x) - 1, int(y) - 1, int(direct)
                        if direct not in [0, 1]:
                            print('Введите правильное направление')
                            continue
                        if (direct == 1) and (i != 1):
                            if (y + i) > self.size:
                                print('Корабль выходит за пределы поля')
                                continue
                        else:
                            if (x + i) > self.size:
                                print('Корабль выходит за пределы поля')
                                continue
                        ship = Ship(Dot(x, y), i, direct)
                        break
                try:
                    board.ship_add(ship, vid)
                except ShipWrongException:
                    pass
                except IndexError:
                    break
                else:
                    break
        for i in range(self.size):
            for j in range(self.size):
                if board.field[i][j] == '.':
                    board.field[i][j] = 'O'
        board.begin()
        return board

    def create_board(self, vizible, auto):
        board = None
        while board is None:
            board = self.create_tru(vizible, auto)
        return board

    def main(self):
        count = 1
        while True:
            print('*' * 30)
            print('Поде игрока:')
            print(self.player_board)
            print('Поле компьютера:')
            print(self.computer_board)
            print('')
            if count > 1: sleep(self.time)
            if count % 2 != 0:
                print("Ход человека")
                test = self.player.shot()
                if test:
                    count -= 1
            else:
                print('Ход компьютера')
                test = self.bot.shot()
                if test:
                    count -=1
            if self.player.board.destroy_ship_count == 7:
                print('*' * 30)
                print('Человек победил')
                break
            if self.bot.board.destroy_ship_count == 7:
                print('*' * 30)
                print('компьютер победил')
                break
            count += 1


class Player:
    def __init__(self, board):
        self.board = board

    def shot(self):
        while True:
            try:
                cord = self.cord_input()
                player_shot = self.board.shot_uze(cord, True)
            except BoardException as i:
                print(i)
            else:
                return player_shot

    def cord_input(self):
        pass


class Human(Player):
    def cord_input(self):
        while True:
            self.cord = input('Введите координаты: ', ).split()
            if len(self.cord) != 2:
                print('Ошибка ввода')
                continue
            x, y = self.cord
            if (not x.isdigit()) or (not y.isdigit()):
                print(" Введите числа! ")
                continue
            x, y = int(x) - 1, int(y) - 1
            return Dot(x, y)


class Computer(Player):
    def cord_input(self):
        cord = choice(self.board.free_dots)
        print(f'Компьютер атакует точку: {cord.x + 1} {cord.y + 1}')
        return cord


start = Game()
start.main()

