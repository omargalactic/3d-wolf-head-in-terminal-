#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
رأس ذئب واقعي بالـ ASCII + ألوان RGB (truecolor)
الرأس بيلف يمين وشمال، والرسم بيتحسب 3D حقيقي (إضاءة + فرو + ظلال).

التشغيل:   python wolf_head.py            (الحجم الافتراضي 110x52 = 5720 حرف)
مثال:      python wolf_head.py 90 42      (حجم أصغر)
الخروج:    CTRL + C
"""
import sys, math, time, shutil, colorsys

W = int(sys.argv[1]) if len(sys.argv) > 1 else 110
H = int(sys.argv[2]) if len(sys.argv) > 2 else 52
FRAMES = 60          # عدد فريمات دورة اللف كاملة
DELAY = 0.07         # الوقت بين الفريمات

# ───────────────────────── رياضيات بسيطة ─────────────────────────
def mm(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

def tr(a):
    return [[a[j][i] for j in range(3)] for i in range(3)]

def mv(a, v):
    return [sum(a[i][k] * v[k] for k in range(3)) for i in range(3)]

def rx(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    return [[1, 0, 0], [0, c, -s], [0, s, c]]

def ry(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]

def rz(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]

def hn(ix, iy, iz=0):
    """هاش عشوائي ثابت (للفرو والنجوم)"""
    h = (ix * 374761393 + iy * 668265263 + iz * 1442695041) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    h ^= h >> 16
    return (h & 0xFFFF) / 65535.0

# ───────────────────────── بناء الموديل ─────────────────────────
GRAY = (150, 150, 160); DARK = (96, 96, 110); MID = (126, 126, 140)
LIGHT = (208, 203, 197); TAN = (170, 162, 156); PINK = (205, 120, 128)

PRIMS = []

def add(c, r, rot=(0, 0, 0), col=GRAY, kind='fur', mirror=False, face=False):
    items = [(c, r, rot)]
    if mirror:
        items.append(((-c[0], c[1], c[2]), r, (rot[0], -rot[1], -rot[2])))
    for cc, rr, rt in items:
        R = mm(rz(rt[2]), mm(ry(rt[1]), rx(rt[0])))
        PRIMS.append(dict(c=cc, r=rr, R=R, col=col, kind=kind, face=face))

def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))

def build():
    # الرقبة والصدر
    add((0, -0.70, -0.50), (0.78, 0.75, 0.62), col=GRAY)
    # الجمجمة
    add((0, 0.22, 0.0), (0.66, 0.60, 0.66), col=GRAY, face=True)
    add((0, 0.56, 0.08), (0.38, 0.24, 0.42), col=MID, face=True)      # الجبهة الغامقة
    # الخطم (الأنف الطويل)
    add((0, -0.02, 0.70), (0.26, 0.23, 0.62), rot=(10, 0, 0), col=TAN, face=True)
    add((-0.15, -0.17, 0.72), (0.17, 0.17, 0.55), rot=(10, 0, 0), col=LIGHT, mirror=True)
    add((0, -0.40, 0.66), (0.22, 0.11, 0.44), rot=(6, 0, 0), col=LIGHT)   # الفك السفلي
    add((0, -0.285, 0.74), (0.235, 0.028, 0.55), rot=(8, 0, 0), col=(40, 20, 26), kind='lip')
    add((-0.12, -0.335, 1.10), (0.026, 0.085, 0.026), col=(245, 240, 225), kind='fang', mirror=True)
    add((0, -0.075, 1.27), (0.15, 0.11, 0.12), rot=(10, 0, 0), col=(30, 28, 32), kind='nose')
    # الحواجب والعيون
    add((-0.30, 0.40, 0.52), (0.15, 0.065, 0.15), rot=(0, 0, -18), col=DARK, mirror=True, face=True)
    add((-0.29, 0.28, 0.57), (0.115, 0.068, 0.085), rot=(0, 0, -18), col=(255, 190, 20), kind='eye', mirror=True)
    # الودان
    add((-0.42, 0.88, -0.10), (0.20, 0.52, 0.09), rot=(0, 0, 14), col=(140, 140, 154), mirror=True)
    add((-0.536, 1.346, -0.10), (0.085, 0.24, 0.055), rot=(0, 0, 14), col=(120, 120, 134), mirror=True)
    add((-0.415, 0.86, -0.03), (0.12, 0.40, 0.055), rot=(0, 0, 14), col=PINK, kind='earin', mirror=True)
    # الخدود
    add((-0.55, -0.25, 0.05), (0.32, 0.36, 0.42), col=LIGHT, mirror=True)
    # شعر الرقبة والخدود (فرو بارز حوالين الراس من تحت)
    for ring, (rad, ln, zz, off, n) in enumerate([(1.00, 0.24, -0.05, 0.0, 28), (0.80, 0.21, -0.25, 1.0, 24)]):
        for k in range(n):
            a = math.radians(150 + 240 * (k + off * 0.5) / n)
            cx = 0.88 * rad * math.cos(a)
            cy = -0.12 + 0.82 * rad * math.sin(a)
            t = hn(k, ring, 5)
            add((cx, cy, zz), (0.085 + 0.035 * t, ln + 0.07 * t, 0.08),
                rot=(0, 0, math.degrees(a) - 90), col=lerp(GRAY, LIGHT, 0.25 + 0.75 * t))
    # لحية تحت الفك
    for k, x in enumerate((-0.24, -0.12, 0.0, 0.12, 0.24)):
        add((x, -0.58 - 0.03 * (k % 2), 0.42), (0.075, 0.24, 0.075), rot=(0, 0, -x * 40), col=LIGHT)
    # شعر الجبهة بين الودان
    for k, x in enumerate((-0.28, -0.14, 0.0, 0.14, 0.28)):
        add((x, 0.74, 0.12), (0.07, 0.17, 0.07), rot=(0, 0, -x * 45), col=lerp(MID, GRAY, hn(k, 3, 1)))

build()
LV = (-0.45, 0.62, 0.64)
_l = math.sqrt(sum(v * v for v in LV))
LX, LY, LZ = (v / _l for v in LV)

RAMP = [" ", ".'`", ",:;-", "~=+i", "l!I|/\\", "txjfr", "oO0Zz", "XYUJC", "#%&", "@8BM$W"]
NB = len(RAMP)

def clamp(v):
    return 0 if v < 0 else (255 if v > 255 else int(v))

# ───────────────────────── الرسم ─────────────────────────
def render(i):
    ph = 2 * math.pi * i / FRAMES
    yaw = 40 * math.sin(ph)
    pitch = 5 * math.sin(2 * ph + 0.8) - 2
    roll = 6 * math.sin(ph + 0.6)
    bob = 0.035 * math.sin(2 * ph)
    Rv = mm(ry(yaw), mm(rx(pitch), rz(roll)))
    Rvt = tr(Rv)
    rim = tuple(int(c * 255) for c in colorsys.hsv_to_rgb((i / FRAMES) % 1.0, 0.85, 1.0))

    sx = min(W / 3.1, 2 * H / 3.35)
    sy = sx / 2
    ox = W / 2
    oy = H / 2 + 0.12 * sy

    N = W * H
    zbuf = [-1e9] * N
    hit = [None] * N
    pdata = []

    for pi, p in enumerate(PRIMS):
        Rt = mm(Rv, p['R'])
        rr = p['r']
        A = [[sum(Rt[a][k] * Rt[b][k] / (rr[k] * rr[k]) for k in range(3)) for b in range(3)] for a in range(3)]
        M0 = sum(Rt[0][k] ** 2 * rr[k] ** 2 for k in range(3))
        M1 = sum(Rt[1][k] ** 2 * rr[k] ** 2 for k in range(3))
        cv = mv(Rv, p['c'])
        cv[1] += bob
        pdata.append((A, Rt, rr, cv))
        cxs = ox + cv[0] * sx
        cys = oy - cv[1] * sy
        hx = math.sqrt(M0) * sx
        hy = math.sqrt(M1) * sy
        c0 = max(0, int(cxs - hx)); c1 = min(W - 1, int(cxs + hx) + 1)
        r0 = max(0, int(cys - hy)); r1 = min(H - 1, int(cys + hy) + 1)
        A00, A01, A02 = A[0]; A11, A12 = A[1][1], A[1][2]; A22 = A[2][2]
        for row in range(r0, r1 + 1):
            qy = (oy - (row + 0.5)) / sy - cv[1]
            for col in range(c0, c1 + 1):
                qx = (col + 0.5 - ox) / sx - cv[0]
                b = A02 * qx + A12 * qy
                c = A00 * qx * qx + 2 * A01 * qx * qy + A11 * qy * qy - 1
                disc = b * b - A22 * c
                if disc < 0:
                    continue
                qz = (-b + math.sqrt(disc)) / A22
                z = cv[2] + qz
                idx = row * W + col
                if z > zbuf[idx]:
                    zbuf[idx] = z
                    hit[idx] = (pi, qx, qy, qz)

    rows = []
    for row in range(H):
        parts = []
        last = None
        for col in range(W):
            idx = row * W + col
            h = hit[idx]
            if h is None:
                ch, rgb = background(col, row, sx, sy, ox, oy, i)
            else:
                ch, rgb = shade(h, pdata, Rvt, rim, col, row)
            if ch == ' ':
                parts.append(' ')
                continue
            q = ((rgb[0] >> 3) << 3, (rgb[1] >> 3) << 3, (rgb[2] >> 3) << 3)
            if q != last:
                parts.append("\033[38;2;%d;%d;%dm" % q)
                last = q
            parts.append(ch)
        rows.append(''.join(parts) + "\033[0m")
    return "\033[H" + "\n".join(rows)


def pick(l, f):
    bi = min(NB - 1, max(0, int((l ** 0.85) * NB)))
    s = RAMP[bi]
    return s[int(f * 977) % len(s)]


def shade(h, pdata, Rvt, rim, col, row):
    pi, qx, qy, qz = h
    p = PRIMS[pi]
    A, Rt, rr, cv = pdata[pi]
    nx = A[0][0] * qx + A[0][1] * qy + A[0][2] * qz
    ny = A[1][0] * qx + A[1][1] * qy + A[1][2] * qz
    nz = A[2][0] * qx + A[2][1] * qy + A[2][2] * qz
    inv = 1.0 / math.sqrt(nx * nx + ny * ny + nz * nz)
    nx *= inv; ny *= inv; nz *= inv
    diff = max(0.0, nx * LX + ny * LY + nz * LZ)
    kind = p['kind']
    base = p['col']

    # موضع النقطة في فراغ الموديل (عشان الفرو يلزق في السطح ويلف معاه)
    pv = (cv[0] + qx, cv[1] + qy, cv[2] + qz)
    mx = Rvt[0][0] * pv[0] + Rvt[0][1] * pv[1] + Rvt[0][2] * pv[2]
    my = Rvt[1][0] * pv[0] + Rvt[1][1] * pv[1] + Rvt[1][2] * pv[2]
    mz = Rvt[2][0] * pv[0] + Rvt[2][1] * pv[1] + Rvt[2][2] * pv[2]
    f1 = hn(int(mx * 40 + 500), int(my * 40 + 500), int(mz * 40 + 500))
    f2 = hn(int(mx * 24 + 500), int(my * 7 + 500), int(mz * 24 + 500))
    f = 0.6 * f1 + 0.4 * f2

    rimf = (1.0 - max(0.0, nz)) ** 3

    if kind == 'eye':
        loc = [sum(Rt[k][j] * (qx, qy, qz)[k] for k in range(3)) / rr[j] for j in range(3)]
        lx, ly = loc[0], loc[1]
        if (lx / 0.17) ** 2 + (ly / 0.80) ** 2 < 1:
            return '@', (12, 8, 4)                       # بؤبؤ العين
        if (lx + 0.45) ** 2 + (ly - 0.45) ** 2 < 0.035:
            return '@', (255, 255, 255)                  # لمعة
        d = min(1.0, math.sqrt(lx * lx + ly * ly))
        c = lerp((255, 225, 70), (225, 110, 5), d)
        bb = 0.75 + 0.25 * diff
        rgb = (clamp(c[0] * bb), clamp(c[1] * bb), clamp(c[2] * bb))
        return ('O' if d > 0.55 else '@'), rgb

    if kind == 'nose':
        hx_, hy_, hz_ = LX, LY, LZ + 1.0
        hl = math.sqrt(hx_ ** 2 + hy_ ** 2 + hz_ ** 2)
        spec = max(0.0, (nx * hx_ + ny * hy_ + nz * hz_) / hl) ** 18
        v = 22 + 40 * diff + 220 * spec
        return ('@' if spec > 0.3 else '#'), (clamp(v), clamp(v), clamp(v + 6))

    if kind == 'lip':
        return '#', (clamp(34 + 40 * diff), 14, 20)

    if kind == 'fang':
        bb = 0.45 + 0.7 * diff
        return 'A', (clamp(250 * bb), clamp(245 * bb), clamp(230 * bb))

    # فرو عادي
    b = 0.34 + 1.05 * diff
    b *= 0.80 + 0.40 * f
    r, g, bl = base[0] * b, base[1] * b, base[2] * b

    if p['face']:
        for ex in (-0.29, 0.29):
            d = math.sqrt(((mx - ex) / 0.24) ** 2 + ((my - 0.28) / 0.15) ** 2)
            if d < 1.0:
                k = 0.40 + 0.60 * d * d
                r *= k; g *= k; bl *= k

    r += rim[0] * rimf * 0.75
    g += rim[1] * rimf * 0.75
    bl += rim[2] * rimf * 0.75
    r, g, bl = clamp(r), clamp(g), clamp(bl)
    l = (0.30 * r + 0.59 * g + 0.11 * bl) / 255.0
    ch = pick(l, f1 if f1 > 0.5 else f2)
    if ch == ' ':
        ch = '.'
    return ch, (r, g, bl)


def background(col, row, sx, sy, ox, oy, i):
    x = (col + 0.5 - ox) / sx
    y = (oy - (row + 0.5)) / sy
    dx, dy = x - 0.02, y - 0.38
    d = math.sqrt(dx * dx + dy * dy)
    R = 1.42
    if d < R:
        n1 = hn(int((x + 5) * 7), int((y + 5) * 7), 3)
        n2 = hn(int((x + 5) * 19), int((y + 5) * 19), 9)
        crater = 0.55 + 0.35 * n1 + 0.20 * n2
        limb = 0.80 + 0.20 * (1 - d / R)
        v = crater * limb * 0.36
        c = (clamp(120 * v * 2), clamp(140 * v * 2), clamp(200 * v * 2))
        s_ = RAMP[1 + int(v * 6) % 3] if v > 0.08 else '.'
        return s_[int(n2 * 977) % len(s_)], c
    if d < R * 1.28:
        t = (R * 1.28 - d) / (R * 0.28)
        v = 0.22 * t * t
        if v > 0.045:
            return ('.' if v < 0.11 else ':'), (clamp(80 * v * 4), clamp(100 * v * 4), clamp(170 * v * 4))
    s = hn(col, row, 77)
    if s < 0.017:
        tw = 0.45 + 0.55 * hn(col, row, 13 + (i // 7) % 4)
        v = clamp(230 * tw)
        return ('*' if s < 0.004 else ('+' if s < 0.009 else '.')), (v, v, clamp(v + 20))
    # ضباب خفيف في الخلفية (أقوى ناحية الأرض)
    m = hn(col, row, 31)
    if m < 0.93:
        fog = 0.5 + 0.5 * max(0.0, min(1.0, (0.2 - y) / 1.6))
        v = clamp((26 + 30 * hn(col, row, 5)) * fog)
        return ".,`'-:;"[int(m * 977) % 7], (v, clamp(v * 1.15), clamp(v * 1.7))
    return ' ', (0, 0, 0)

# ───────────────────────── التشغيل ─────────────────────────
def wait_for_size():
    while True:
        cols, rows = shutil.get_terminal_size()
        if cols >= W + 1 and rows >= H + 1:
            return
        sys.stdout.write("\033[2J\033[H\033[0m")
        sys.stdout.write(
            "الشاشة صغيرة: %dx%d  والمطلوب %dx%d\n"
            "صغّر الخط (zoom out بإصبعين) أو لف الموبايل أفقي\n"
            "أو شغّل بحجم أصغر:  python wolf_head.py 80 38\n" % (cols, rows, W + 1, H + 1))
        sys.stdout.flush()
        time.sleep(0.6)


def main():
    cache = {}
    sys.stdout.write("\033[?25l")
    try:
        wait_for_size()
        sys.stdout.write("\033[2J")
        t = 0
        while True:
            k = t % FRAMES
            if k not in cache:
                cache[k] = render(k)
            t0 = time.time()
            sys.stdout.write(cache[k])
            sys.stdout.flush()
            left = DELAY - (time.time() - t0)
            if left > 0:
                time.sleep(left)
            t += 1
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[0m\033[?25h\033[2J\033[H")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
