import pygame as pg
from random import *

ROM = "C:\\Users\\robin\\Desktop\\MyFiles\\MySpace\\RobinPython\\chip-8 emulator\\games\\Pong.ch8"

# ------variables------

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 320
color = pg.Color
clock = pg.time.Clock()
time_delay = pg.time.delay
draw = pg.draw
running = True
Rect = pg.Rect
pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


class CPU:

    def __init__(self):
        self.waitforkey = -1
        self.dt = 60
        self.st = 60

        self.RAM = [0] * 4096
        self.REG = [0] * 16
        self.STACK = [0] * 16
        self.SCREEN = [[0] * 64 for i in range(32)]
        self.KEYS = [0] * 16

        self.pc = 0x200
        self.sp = -1
        self.I = 0

        font = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,
            0x20, 0x60, 0x20, 0x20, 0x70,
            0xF0, 0x10, 0xF0, 0x80, 0xF0,
            0xF0, 0x10, 0xF0, 0x10, 0xF0,
            0x90, 0x90, 0xF0, 0x10, 0x10,
            0xF0, 0x80, 0xF0, 0x10, 0xF0,
            0xF0, 0x80, 0xF0, 0x90, 0xF0,
            0xF0, 0x10, 0x20, 0x40, 0x40,
            0xF0, 0x90, 0xF0, 0x90, 0xF0,
            0xF0, 0x90, 0xF0, 0x10, 0xF0,
            0xF0, 0x90, 0xF0, 0x90, 0x90,
            0xE0, 0x90, 0xE0, 0x90, 0xE0,
            0xF0, 0x80, 0x80, 0x80, 0xF0,
            0xE0, 0x90, 0x90, 0x90, 0xE0,
            0xF0, 0x80, 0xF0, 0x80, 0xF0,
            0xF0, 0x80, 0xF0, 0x80, 0x80
        ]

        for i in range(len(font)):
            self.RAM[i] = font[i]

    def loadROM(self, gamefile):
        with open(gamefile, 'rb') as file:
            index = 0x200
            for i in file.read():
                self.RAM[index] = i
                index += 1

    def cycle(self):
        if self.waitforkey > 0:
            for i in range(len(self.KEYS)):
                if self.KEYS[i] == 1:
                    self.REG[self.waitforkey] = i
                    self.waitforkey = -1
                    return
            return
        self.execute(self.fetch())

        self.dt -= 1
        self.st -= 1
        if self.dt < 0:
            self.dt = 60
        if self.st < 0:
            self.st = 60

    def fetch(self):
        op = self.RAM[self.pc] << 8
        op |= self.RAM[self.pc + 1]
        self.pc += 2
        return op

    def execute(self, opcode):

        # cls
        if opcode == 0x00e0:
            self.SCREEN = [[0] * 64 for i in range(32)]
            drawscr(self.SCREEN)
            return
        # ret
        if opcode == 0x00ee:
            self.pc = self.STACK[self.sp]
            self.sp -= 1
            return

        pfx = opcode >> 12
        nnn = opcode & 0x0fff

        # jp add
        if pfx == 1:
            self.pc = nnn
            return

        # CALL add
        if pfx == 2:
            self.sp += 1
            self.STACK[self.sp] = self.pc
            self.pc = nnn
            return

        x = nnn >> 8
        kk = nnn & 0xff

        # se vx, byte
        if pfx == 3:

            if self.REG[x] == kk:
                self.pc += 2
            return

        # sne vx byte

        # sne vx, byte
        if pfx == 4:
            if self.REG[x] != kk:
                self.pc += 2
            return

        y = kk >> 4

        # se vx, vy
        if pfx == 5:
            if self.REG[x] == self.REG[y]:
                self.pc += 2
            return

        # ld vx, vy
        if pfx == 6:

            self.REG[x] = kk
            return

        # add vx, byte
        if pfx == 7:
            self.REG[x] += kk
            if self.REG[x] >= 256:
                self.REG[x] -= 256

            return

        sfx = kk & 0xf

        if pfx == 8:

            # ld vx, vy
            if sfx == 0:
                self.REG[x] = self.REG[y]
                return

            # or vx, vy
            if sfx == 1:
                self.REG[x] |= self.REG[y]
                return

            # and vx, vy
            if sfx == 2:
                self.REG[x] &= self.REG[y]
                return

            # xor vx, vy
            if sfx == 3:
                self.REG[x] = self.REG[x] ^ self.REG[y]
                return

            # add vx, vy
            if sfx == 4:
                self.REG[x] += self.REG[y]
                if self.REG[x] > 255:
                    self.REG[15] = 1
                    self.REG[x] -= 256
                else:
                    self.REG[15] = 0
                return

            # sub vx, vy
            if sfx == 5:
                self.REG[x] -= self.REG[y]
                if self.REG[x] > 0:
                    self.REG[15] = 1
                else:
                    self.REG[15] = 0
                    self.REG[x] += 256
                return

            # SHR Vx {, Vy}
            if sfx == 6:
                self.REG[15] = self.REG[x] & 0x1
                self.REG[x] >>= 1
                return

            # SUBN Vx, Vy
            if sfx == 7:
                if self.REG[y] > self.REG[x]:
                    self.REG[15] = 1
                else:
                    self.REG[15] = 0
                self.REG[x] = self.REG[y] - self.REG[x]
                return

            # SHL Vx {, Vy}
            if sfx == 0xe:
                self.REG[15] = self.REG[x] >> 7
                self.REG[x] = (self.REG[x] << 1) & 0xff
                return

        # SNE Vx, Vy
        if pfx == 9:
            if self.REG[x] != self.REG[y]:
                self.pc += 2
            return

        # LD I, addr
        if pfx == 0xa:
            self.I = nnn
            return

        # JP V0, addr
        if pfx == 0xb:
            self.pc = nnn + self.REG[0]
            return

        # RND Vx, byte
        if pfx == 0xc:
            self.REG[x] = randint(0, 256) & kk
            return

        # DRW Vx, Vy, nibble
        if pfx == 0xd:
            n = sfx
            sy = self.REG[y]
            self.REG[15] = 0
            i = 0
            while i < n:
                byte = self.RAM[self.I+i]
                j = 0
                sx = self.REG[x]
                sy %= 32
                while j < 8:
                    bit = (byte >> (7 -j)) & 0x1
                    sx %= 64
                    if self.SCREEN[sy][sx] == 1 and bit == 1:
                        self.REG[15] = 1
                    self.SCREEN[sy][sx] ^= bit
                    sx += 1
                    j += 1
                sy += 1
                i += 1
            drawscr(self.SCREEN)
            return

        if pfx == 0xe:
            # SKP Vx
            if sfx == 0xe:
                if self.KEYS[self.REG[x]]:
                    self.pc += 2
                return

            # SKNP Vx
            if sfx == 1:
                if self.KEYS[self.REG[x]] == 0:
                    self.pc += 2
                return

        if pfx == 0xf:
            # LD Vx, DT
            if kk == 0x07:
                self.REG[x] = self.dt
                return

            # LD Vx, K
            if kk == 0xa:
                self.waitforkey = x
                return

            # LD DT, Vx
            if kk == 0x15:
                self.dt = self.REG[x]
                return

            # LD ST, Vx
            if kk == 0x18:
                self.st = self.REG[x]
                return

            # ADD I, Vx
            if kk == 0x1e:
                self.I += self.REG[x]
                return

            # LD F, Vx
            if kk == 0x29:
                self.I = self.REG[x] * 5
                return

            # LD B, Vx
            if kk == 0x33:
                self.RAM[self.I] = self.REG[x] // 100
                self.RAM[self.I + 1] = (self.REG[x] // 10) % 10
                self.RAM[self.I + 2] = (self.REG[x] % 10)
                return

            # LD [I], Vx
            if kk == 0x55:
                i = 0
                while i <= x:
                    self.RAM[i + self.I] = self.REG[i]
                    i += 1
                return

            # LD Vx, [I]
            if kk == 0x65:
                i = 0
                while i <= x:
                    self.REG[i] = self.RAM[self.I + i]
                    i += 1
                return

        raise Exception(hex(opcode))




keymap = {
    pg.K_1: 1, pg.K_2: 2, pg.K_3: 3, pg.K_4: 0xc,

    pg.K_q: 4, pg.K_w: 5, pg.K_e: 6, pg.K_r: 0xd,

    pg.K_a: 7, pg.K_s: 8, pg.K_d: 9, pg.K_f: 0xe,

    pg.K_z: 0xa, pg.K_x: 0, pg.K_c: 0xb, pg.K_v: 0xf
}

cpu = CPU()


def drawscr(scr):
    screen.fill(color('black'))

    for y in range(len(scr)):
        for x in range(len(scr[0])):
            if scr[y][x] == 1:
                draw.rect(screen, color('white'), Rect((x * 10) + 1, (y * 10) + 1, 10 - 1, 10 - 1))

cpu.loadROM(ROM)

# ------mainloop------
while running:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        keys = pg.key.get_pressed()

        for i in keymap.keys():
            cpu.KEYS[keymap[i]] = keys[i]

    cpu.cycle()
    pg.display.flip()
    time_delay(1000//180)


pg.quit()
