"""
케이스형 압전 버저(지름 22 mm) 정적 가압 지그 v2
유리프 압전 타일 팀 / 2026-10-28

v1(27 mm 맨 디스크 + 낙하추)에서 바꾼 점
  1. 실물 소자가 지름 22 mm 케이스형 버저이므로 포켓을 22.4 mm로 줄였다.
  2. 낙하추(충격, 약 70 g) 대신 받침판에 1-5 kg 추를 천천히 올리는 정적 가압으로 바꿨다.
     F = mg를 정확히 알 수 있고, 발걸음과 같은 준정적 입력이 된다.
  3. 플런저 축을 브리지의 슬리브가 잡아 주어 힘이 버저 중앙에 수직으로 들어간다.

부품
  01 base     : 하판. 버저 포켓, 배선 홈, 꺼내기 홈, M3 구멍 4개
  02 bridge   : 다리 4개 달린 상판 + 축 슬리브. 하판에 M3 볼트로 고정
  03 plunger  : 중앙 가압 돌기 + 축 + 추 받침판(원판 추 중심 맞춤 기둥)

실측 후 아래 상수만 고쳐 다시 실행한다. 특히 T_CASE(버저 두께)는 아직 가정값이다.
"""
import os
import numpy as np
import trimesh
from trimesh.creation import cylinder, box

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
SEG = 128

# ---------- 버저 (실측값으로 교체) ----------
D_CASE = 22.0     # 케이스 지름 (사용자 실측)
T_CASE = 7.0      # 케이스 두께 -- 가정값, 반드시 실측해서 고칠 것

# ---------- 하판 ----------
PLATE = 60.0
T_BASE = 8.0
D_POCKET = D_CASE + 0.4
H_POCKET = 4.0            # 버저 아래쪽 절반 정도를 잡는다
W_WIRE = 5.0              # 배선 홈 폭 (+x 방향)
W_NOTCH = 8.0             # 꺼내기 홈 폭 (-x 방향)
XY_BOLT = 24.0
D_BOLT = 3.4              # M3 통과

# ---------- 플런저 ----------
D_BOSS = 6.0              # 버저 중앙을 누르는 돌기
H_BOSS = 3.0
D_STEM = 12.0
PLAT = 80.0               # 추 받침판 한 변
T_PLAT = 5.0
D_POST = 24.0             # 원판 추 구멍에 끼우는 중심 기둥 (아령 원판 구멍 25-30 mm)
H_POST = 20.0
GAP_TRAVEL = 5.0          # 받침판 아래와 슬리브 위 사이 여유 (버저가 이보다 얇아지면 받침판이 슬리브에 걸린다)

# ---------- 브리지 ----------
CLEAR = 4.0               # 돌기 위와 브리지 아래 사이 여유
T_BRIDGE = 5.0
D_BORE = D_STEM + 0.5     # 축 구멍 (헐겁게)
D_SLEEVE = 22.0
H_SLEEVE = 25.0
LEG = 8.0                 # 다리 단면 한 변

# ---------- 높이 계산 ----------
Z_CASE_BOT = T_BASE - H_POCKET
Z_CASE_TOP = Z_CASE_BOT + T_CASE
Z_BRIDGE_BOT = Z_CASE_TOP + H_BOSS + CLEAR
Z_BRIDGE_TOP = Z_BRIDGE_BOT + T_BRIDGE
Z_SLEEVE_TOP = Z_BRIDGE_TOP + H_SLEEVE
Z_PLAT_BOT = Z_SLEEVE_TOP + GAP_TRAVEL


def cyl(d, z0, z1, seg=SEG):
    m = cylinder(radius=d / 2.0, height=z1 - z0, sections=seg)
    m.apply_translation([0, 0, (z0 + z1) / 2.0])
    return m


def blk(dx, dy, z0, z1, cx=0.0, cy=0.0):
    m = box(extents=[dx, dy, z1 - z0])
    m.apply_translation([cx, cy, (z0 + z1) / 2.0])
    return m


def bolt_holes(z0, z1):
    hs = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            h = cylinder(radius=D_BOLT / 2.0, height=z1 - z0, sections=48)
            h.apply_translation([sx * XY_BOLT, sy * XY_BOLT, (z0 + z1) / 2.0])
            hs.append(h)
    return trimesh.util.concatenate(hs)


def build_base():
    m = blk(PLATE, PLATE, 0, T_BASE)
    m = m.difference(cyl(D_POCKET, Z_CASE_BOT, T_BASE + 1))
    # 배선 홈: 포켓 바닥 높이에서 +x 가장자리까지, 위가 열린 홈
    m = m.difference(blk(PLATE / 2.0, W_WIRE, Z_CASE_BOT, T_BASE + 1, cx=PLATE / 4.0 + 5))
    # 꺼내기 홈: -x 쪽 손가락 홈
    m = m.difference(blk(14.0, W_NOTCH, Z_CASE_BOT + 1.0, T_BASE + 1, cx=-(D_POCKET / 2.0)))
    m = m.difference(bolt_holes(-1, T_BASE + 1))
    return m


def build_bridge():
    plate = blk(PLATE, PLATE, Z_BRIDGE_BOT, Z_BRIDGE_TOP)
    legs = [blk(LEG, LEG, T_BASE, Z_BRIDGE_BOT + 0.01, cx=sx * XY_BOLT, cy=sy * XY_BOLT)
            for sx in (-1, 1) for sy in (-1, 1)]
    sleeve = cyl(D_SLEEVE, Z_BRIDGE_TOP - 0.01, Z_SLEEVE_TOP)
    m = trimesh.boolean.union([plate, sleeve] + legs)
    m = m.difference(cyl(D_BORE, Z_BRIDGE_BOT - 1, Z_SLEEVE_TOP + 1))
    m = m.difference(bolt_holes(T_BASE - 1, Z_BRIDGE_TOP + 1))
    # 버저와 배선이 보이도록 +x, -x 쪽은 다리 사이가 열려 있다
    return m


def build_plunger():
    boss = cyl(D_BOSS, Z_CASE_TOP, Z_CASE_TOP + H_BOSS + 0.01)
    stem = cyl(D_STEM, Z_CASE_TOP + H_BOSS, Z_PLAT_BOT + 0.01)
    plat = blk(PLAT, PLAT, Z_PLAT_BOT, Z_PLAT_BOT + T_PLAT)
    post = cyl(D_POST, Z_PLAT_BOT + T_PLAT - 0.01, Z_PLAT_BOT + T_PLAT + H_POST)
    return trimesh.boolean.union([boss, stem, plat, post])


def build_buzzer():
    return cyl(D_CASE, Z_CASE_BOT, Z_CASE_TOP)


def check(parts):
    """부품끼리 부피가 겹치는지 확인 (접촉면은 겹침이 아님)"""
    names = list(parts)
    ok = True
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = parts[names[i]], parts[names[j]]
            inter = a.intersection(b)
            vol = inter.volume if inter is not None and not inter.is_empty else 0.0
            flag = "OK" if vol < 1.0 else "INTERFERENCE"
            if vol >= 1.0:
                ok = False
            print(f"  {names[i]:8s} x {names[j]:8s}: {vol:8.2f} mm^3  {flag}")
    return ok


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    parts = {
        "base": build_base(),
        "bridge": build_bridge(),
        "plunger": build_plunger(),
        "buzzer": build_buzzer(),
    }
    for k, m in parts.items():
        assert m.is_watertight, k
    print("높이: 버저 윗면 z=%.1f, 브리지 %.1f-%.1f, 슬리브 위 %.1f, 받침판 아래 %.1f, 전체 높이 %.1f mm"
          % (Z_CASE_TOP, Z_BRIDGE_BOT, Z_BRIDGE_TOP, Z_SLEEVE_TOP, Z_PLAT_BOT,
             Z_PLAT_BOT + T_PLAT + H_POST))
    print("간섭 검사:")
    ok = check(parts)
    print("결과:", "간섭 없음" if ok else "간섭 있음 -- 치수 확인 필요")

    parts["base"].export(os.path.join(OUT, "jig2_01_base.stl"))
    parts["bridge"].export(os.path.join(OUT, "jig2_02_bridge.stl"))
    # 플런저는 받침판이 바닥에 오도록 뒤집어서 출력용으로 저장
    pl = parts["plunger"].copy()
    pl.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    pl.apply_translation([0, 0, -pl.bounds[0][2]])
    pl.export(os.path.join(OUT, "jig2_03_plunger.stl"))
    asm = trimesh.util.concatenate(list(parts.values()))
    asm.export(os.path.join(OUT, "jig2_00_assembly_check.stl"))
    print("플런저 부피 %.1f cm^3 (PLA 100%% 기준 약 %.0f g, 인필에 따라 가벼워짐 -- 실제 무게를 저울로 재서 F에 더할 것)"
          % (parts["plunger"].volume / 1000, parts["plunger"].volume / 1000 * 1.24))
