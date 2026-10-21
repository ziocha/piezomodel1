"""
27 mm PZT 유니모프 벤더 디스크 CAD 모델 생성기
piezo_hafs_108 / 유리프 압전 타일 팀

치수 기준: Murata 7BB-27-4 데이터시트 공칭값
  황동 백킹판  Ø27.0 x 0.30 mm
  PZT 세라믹   Ø19.7 x 0.22 mm
  은 전극      Ø18.5 x 0.02 mm
  총 두께      0.54 mm
  공진 주파수  4.6 +/- 0.5 kHz (참고, 모델에는 미반영)

실물 디스크를 캘리퍼스로 재서 아래 값을 바꾼 뒤 다시 실행하면
하우징 설계에 쓸 수 있는 정확한 모델이 나온다.
"""

import numpy as np
import trimesh
from trimesh.creation import cylinder, box

OUT = "/home/claude/cad"
SEG = 192  # 원기둥 분할 수. 크면 매끄럽고 파일이 커진다

# ===================== 치수 (mm) =====================
D_BRASS, T_BRASS = 27.0, 0.30   # 황동 백킹판
D_CER,   T_CER   = 19.7, 0.22   # PZT 세라믹층
D_ELEC,  T_ELEC  = 18.5, 0.02   # 은 전극

D_SOLDER, T_SOLDER = 2.2, 0.45  # 납땜 패드
R_SOLDER_CER   = 6.0            # 세라믹 위 납땜 위치 (중심에서)
R_SOLDER_BRASS = 12.0           # 황동 위 납땜 위치 (중심에서)

D_WIRE, L_WIRE = 0.6, 12.0      # 리드선 (일부만 모델링)

EXAGG = 10.0                    # 발표용 단면 모델의 두께 배율


def disc(d, t, z0, exagg=1.0):
    """지름 d, 두께 t인 원판을 z0부터 위로 쌓는다."""
    t_e = t * exagg
    m = cylinder(radius=d / 2.0, height=t_e, sections=SEG)
    m.apply_translation([0, 0, z0 + t_e / 2.0])
    return m


def build(exagg=1.0):
    """층별 메시를 딕셔너리로 반환. exagg는 두께만 배율 적용."""
    parts = {}
    z = 0.0

    parts["01_brass"] = disc(D_BRASS, T_BRASS, z, exagg)
    z += T_BRASS * exagg

    parts["02_ceramic"] = disc(D_CER, T_CER, z, exagg)
    z += T_CER * exagg

    parts["03_electrode"] = disc(D_ELEC, T_ELEC, z, exagg)
    z_top = z + T_ELEC * exagg

    # 납땜 패드 + 리드선
    leads = []
    for r_pos, z_base in [(R_SOLDER_CER, z_top),              # 적색선 - 세라믹 전극
                          (R_SOLDER_BRASS, T_BRASS * exagg)]:  # 흑색선 - 황동판
        pad = cylinder(radius=D_SOLDER / 2.0, height=T_SOLDER, sections=64)
        pad.apply_translation([r_pos, 0, z_base + T_SOLDER / 2.0])
        leads.append(pad)

        wire = cylinder(radius=D_WIRE / 2.0, height=L_WIRE, sections=32)
        wire.apply_transform(trimesh.transformations.rotation_matrix(
            np.pi / 2, [0, 1, 0]))
        wire.apply_translation([r_pos + L_WIRE / 2.0, 0,
                                z_base + T_SOLDER / 2.0])
        leads.append(wire)

    parts["04_leads"] = trimesh.util.concatenate(leads)
    return parts


def half_cut(mesh):
    """y > 0 쪽을 잘라내 단면을 드러낸다."""
    knife = box(extents=[200, 100, 200])
    knife.apply_translation([0, 50, 0])
    try:
        return mesh.difference(knife)
    except Exception:
        return trimesh.intersections.slice_mesh_plane(
            mesh, plane_normal=[0, -1, 0], plane_origin=[0, 0, 0], cap=True)


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)

    # --- 1. 실척 모델: 층별 파일 + 조립 파일 ---
    parts = build(exagg=1.0)
    for name, mesh in parts.items():
        mesh.export(f"{OUT}/disc_{name}.stl")
        print(f"{name:14s} vol={mesh.volume:8.3f} mm^3  watertight={mesh.is_watertight}")

    asm = trimesh.util.concatenate(list(parts.values()))
    asm.export(f"{OUT}/disc_assembly.stl")
    print(f"\n조립 모델 전체 치수 (x,y,z) = {np.round(asm.extents, 3)} mm")

    # --- 2. 발표용 단면 모델 (두께 10배) ---
    ex = build(exagg=EXAGG)
    cut = trimesh.util.concatenate([half_cut(m) for m in ex.values()])
    cut.export(f"{OUT}/disc_cutaway_x10.stl")
    print(f"단면 모델 전체 치수 (x,y,z) = {np.round(cut.extents, 3)} mm "
          f"(두께 {EXAGG:.0f}배 과장)")
