"""
27 mm PZT 디스크 실험 지그 — 하우징 + 가압 플런저 + 낙하추 가이드
유리프 압전 타일 팀

설계 원칙
  1. 디스크 테두리만 지지하고 가운데는 비운다 (유니모프 벤더는 휘어야 전하가 난다)
  2. 플런저가 디스크 중앙을 누르되, 테두리는 동시에 눌러 경계조건을 고정한다
  3. 추를 같은 높이에서 떨어뜨려 가한 힘을 재현 가능하게 만든다

치수는 Murata 7BB-27-4 공칭값 기준. 실측 후 아래 상수만 고쳐 재실행.
"""
import os
import numpy as np
import trimesh
from trimesh.creation import cylinder, box

OUT = "/home/claude/cad"
SEG = 128

# ---------- 디스크 (실측 후 수정할 값) ----------
D_DISC   = 27.0    # 황동판 외경
T_BRASS  = 0.30    # 황동판 두께 (= 테두리 접촉 높이)
T_DISC   = 0.54    # 총 두께 (= 중앙 접촉 높이)
R_SOLDER = 12.0    # 황동판 위 납땜 패드 중심 반경

# ---------- 지그 ----------
PLATE    = 44.0    # 하판·플랜지 한 변
T_BASE   = 6.0
D_POCKET = D_DISC + 0.4   # 디스크 안착 포켓 (헐겁게)
H_POCKET = 2.0
D_RELIEF = 22.0    # 중앙 관통 구멍 — 디스크가 아래로 휠 공간
D_BOLT   = 3.4     # M3 통과
XY_BOLT  = 17.0

D_PLUNGER = D_POCKET - 0.4
D_RING_IN = 24.0   # 플런저 테두리 링 안지름
D_BOSS    = 9.0    # 중앙 가압 돌기 (납땜 패드 r=6 을 피함)
H_PLUNGER = 4.0
D_STEM, H_STEM = 12.0, 20.0

D_TUBE_OUT, D_TUBE_IN = 20.0, 12.4
H_TUBE = 100.0
T_FLANGE = 9.0
D_CBORE, H_CBORE = 28.0, 5.0   # 플런저 몸통이 드나들 공간 (플랜지 밑면)


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
    """하판: 디스크 포켓 + 중앙 릴리프 + 배선 홈 + 체결 홀"""
    m = blk(PLATE, PLATE, 0, T_BASE)
    m = m.difference(cyl(D_POCKET, T_BASE - H_POCKET, T_BASE + 1))
    m = m.difference(cyl(D_RELIEF, -1, T_BASE - H_POCKET + 0.1))
    # 배선 홈: 포켓 바닥 높이에서 바깥으로
    z_floor = T_BASE - H_POCKET
    m = m.difference(blk(26, 5.0, z_floor, z_floor + 1.2, cx=18))
    m = m.difference(bolt_holes(-1, T_BASE + 1))
    return m


def build_plunger():
    """플런저: 테두리 링 + 중앙 돌기 (높이차 = 세라믹 두께) + 추 받는 스템"""
    z_rim = 0.0                    # 황동 테두리에 닿는 면
    z_boss = T_DISC - T_BRASS      # 중앙은 세라믹만큼 높다

    ring = cyl(D_PLUNGER, z_rim, H_PLUNGER).difference(
        cyl(D_RING_IN, -1, H_PLUNGER - 2.0))
    boss = cyl(D_BOSS, z_boss, H_PLUNGER)
    plate = cyl(D_PLUNGER, H_PLUNGER - 2.0, H_PLUNGER)
    stem = cyl(D_STEM, H_PLUNGER, H_PLUNGER + H_STEM)

    m = trimesh.boolean.union([ring, boss, plate, stem])
    # 납땜 패드 도피 슬롯 (링을 반경 방향으로 끊는다)
    m = m.difference(blk(14, 4.6, -0.5, H_PLUNGER - 1.6, cx=R_SOLDER + 3))
    return m


def build_guide():
    """낙하추 가이드: 플랜지 + 관 + 높이 확인용 창"""
    flange = blk(PLATE, PLATE, 0, T_FLANGE)
    tube = cyl(D_TUBE_OUT, 0, H_TUBE)
    m = trimesh.boolean.union([flange, tube])
    m = m.difference(cyl(D_TUBE_IN, -1, H_TUBE + 1))
    m = m.difference(cyl(D_CBORE, -1, H_CBORE))      # 플런저 도피 공간
    m = m.difference(bolt_holes(-1, T_FLANGE + 1))
    # 관찰 창
    m = m.difference(blk(20, 6.0, T_FLANGE + 6, H_TUBE - 4, cx=8))
    return m


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    parts = {
        "jig_01_base": build_base(),
        "jig_02_plunger": build_plunger(),
        "jig_03_guide_tube": build_guide(),
    }
    for name, m in parts.items():
        m.export(f"{OUT}/{name}.stl")
        print(f"{name:18s} {np.round(m.extents,2)} mm  "
              f"vol={m.volume:9.1f} mm^3  watertight={m.is_watertight}")

    # 조립 확인용 (출력하지 말 것)
    asm = [parts["jig_01_base"]]
    p = parts["jig_02_plunger"].copy()
    p.apply_translation([0, 0, T_BASE - H_POCKET + T_BRASS])
    asm.append(p)
    g = parts["jig_03_guide_tube"].copy()
    g.apply_translation([0, 0, T_BASE])
    asm.append(g)
    trimesh.util.concatenate(asm).export(f"{OUT}/jig_00_assembly_check.stl")
    print("조립 확인 모델 저장")
