import pygame
import math

from queue import PriorityQueue

#screen size
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Pathfinding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width # kocka
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self): # index lekérés
        return self.row, self.col

    def is_closed(self): # piros -> már megvizsgáltuk
        return self.color == RED

    def is_open(self): # zöld -> jó útvonal
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK
    
    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
       return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win): # hol akarjuk kirajzolni az útvonalat win = windows
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        # megnézzük fel, le, jobbra, balra hogy egy barrier van-e ott vagy sem (valid lehet a szomszéd vagy sem)
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # le
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # fel
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # jobbra
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # balra
            self.neighbors.append(grid[self.row][self.col - 1])


    def __lt__(self, other): # megvizsgálja, hogy az egyik objektum nagyobb-e az other objektummal
        return False

def h(p1, p2): # row, coloumn, manhattan distance, L distance, heurisztikus funkció
    x1,y1 = p1
    x2,y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw() 

def algorithm(draw, grid, start, end):
    #draw = Lambda: print("Hello")
    #draw()

    count = 0
    open_set = PriorityQueue() # halmaz, effektív mód arra hogy a legkisebb elemet szedjük ki, keep sort algo
    open_set.put((0, count, start)) # (f score, count, node) adjuk a kezdő node-ot
    came_from = {} # melyik node(ok) honnan jött(ek)
    g_score = {node: float("inf") for row in grid for node in row} # követi a jelenlegi a start node-tól a jelenlegi nodeba legrövidebb távolságot
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row} # ezen az útvonalon keresztül KB mennyi a távolság a végéig
    f_score[start] = h(start.get_pos(), end.get_pos()) # becsült távolság

    open_set_hash = {start} # követi milyen nodeok vannak az open_setben

    while not open_set.empty(): # megnéztünk minden lehetséges node-ot, és ha nem talált útvonalat eddig akkor nem létezik
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2] # node associated with the minimum element
        open_set_hash.remove(current) # a legkisebb F értékű node-t kivonjuk az open_setben

        if current == end: # megvan a legrövidebb útvonal
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors: # ha nincs meg az útvonal, akkor nézd meg az összes szomszédot
            temp_g_score = g_score[current] + 1 # számold ki a következő node g_score-ját

            if temp_g_score < g_score[neighbor]: # van jobb útvonal
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor)) # ennek a neighbornak jobb az útvonala mint ami eddig volt
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False

def make_grid(rows, width):
    grid = []
    gap = width // rows # integer division
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows) # node = Node(row, col, width, total_rows)
            grid[i].append(node)

    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE) # újrarajzoljuk az ablakot

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y,x = pos
    
    row = y // gap
    col = x // gap # hol a kurzorunk és hova kattintottunk

    return row, col

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    started = False
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False # ha x-et nyomunk akkor állítsa le a játékot

            if started:
                continue

            if pygame.mouse.get_pressed()[0]: # 0 = bal klikk
                pos = pygame.mouse.get_pos() # kurzor x,y koordináta
                row, col = get_clicked_pos(pos, ROWS, width) # melyik nodra kattintottunk
                node = grid[row][col]

                if not start and node != end:
                    start = node
                    start.make_start()
                elif not end and node != start:
                    end = node
                    end.make_end()
                elif node != end and node != start: # véletlenszerű node-ra kattintottunk
                    node.make_barrier()

            elif pygame.mouse.get_pressed()[2]: # 2 = jobb klikk
                pos = pygame.mouse.get_pos() # kurzor x,y koordináta
                row, col = get_clicked_pos(pos, ROWS, width) # melyik nodra kattintottunk
                node = grid[row][col]
                node.reset()

                if node == start:
                    start = None

                if node == end:
                    end = None

            #visualizáció vége
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    # update all the neighbours in the node class
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
                    #x = lambda: print("hello")
                    #x = def func():s
                    #        print ("hello") 
                    #x()

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)


    pygame.quit()

main(WIN, WIDTH)