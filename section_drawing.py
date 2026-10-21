"""27 mm PZT 유니모프 디스크 단면도 (보고서 도면용)"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.font_manager as fm

fp = fm.FontProperties(fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
plt.rcParams["axes.unicode_minus"] = False

D_BRASS, T_BRASS = 27.0, 0.30
D_CER, T_CER = 19.7, 0.22
D_ELEC, T_ELEC = 18.5, 0.02
ZS = 16.0          # 두께 방향 배율
H_SOLDER = 1.6     # 납땜 패드는 도면상 고정 높이로 그린다

fig, ax = plt.subplots(figsize=(11, 4.6))

z_br, z_ce, z_el = 0.0, T_BRASS, T_BRASS + T_CER
ztop = (z_el + T_ELEC) * ZS

layers = [
    (D_BRASS, T_BRASS, z_br, "#c9a227", "황동 백킹판 (황동 C2680)", "Ø27.0 × t0.30"),
    (D_CER,   T_CER,   z_ce, "#3b6ea5", "PZT 세라믹층",            "Ø19.7 × t0.22"),
    (D_ELEC,  T_ELEC,  z_el, "#9aa0a6", "은(Ag) 전극",             "Ø18.5 × t0.02"),
]
for d, t, z, c, _, _ in layers:
    ax.add_patch(Rectangle((-d / 2, z * ZS), d, max(t * ZS, 0.35),
                           facecolor=c, edgecolor="#222", lw=0.8, zorder=3))

# 납땜 패드 + 리드선
for xpos, zbase, col, lab in [(6.0, ztop, "#b03030", "(+) 적색 — 전극"),
                              (12.0, T_BRASS * ZS, "#1a1a1a", "(−) 흑색 — 황동")]:
    ax.add_patch(Rectangle((xpos - 1.1, zbase), 2.2, H_SOLDER,
                           facecolor="#8a8f94", edgecolor="#222", lw=0.6, zorder=4))
    ax.plot([xpos, 18.0], [zbase + H_SOLDER * 0.6] * 2, color=col, lw=3.2,
            solid_capstyle="round", zorder=5)
    ax.text(18.7, zbase + H_SOLDER * 0.6, lab, fontproperties=fp,
            fontsize=8.5, va="center")

# 왼쪽 지시선 (서로 겹치지 않게 높이 분리)
label_y = [4.2, 8.0, 11.4]   # 황동, 세라믹, 전극 순서에 맞춰 아래→위
for (d, t, z, c, name, dim), ly in zip(layers, label_y):
    x_edge = -d / 2
    y_mid = (z + t / 2) * ZS
    ax.plot([-23.0, x_edge - 2.2, x_edge], [ly, ly, y_mid],
            color="#666", lw=0.7, zorder=2)
    ax.plot([x_edge], [y_mid], "o", ms=2.5, color="#666", zorder=2)
    ax.text(-23.7, ly, f"{name}\n{dim}", fontproperties=fp, fontsize=9,
            ha="right", va="center", linespacing=1.4)

# 총 두께 치수
ax.annotate("", xy=(-16.8, 0), xytext=(-16.8, ztop),
            arrowprops=dict(arrowstyle="<->", lw=0.9, color="#333"))
ax.plot([-17.6, -13.5], [0, 0], color="#333", lw=0.5)
ax.plot([-17.6, -13.5], [ztop, ztop], color="#333", lw=0.5)
ax.text(-17.4, ztop / 2, "총 t0.54", fontproperties=fp, fontsize=8.5,
        rotation=90, ha="right", va="center")

# 가압 방향
ax.annotate("", xy=(-2, ztop + 0.6), xytext=(-2, ztop + 6.5),
            arrowprops=dict(arrowstyle="-|>", lw=1.8, color="#333"))
ax.text(-1.2, ztop + 5.2, "가압 F", fontproperties=fp, fontsize=9.5)

ax.text(0, -5.2,
        "굽힘(d31) 모드 — 세라믹이 한쪽에만 붙어 중립면이 황동 쪽으로 치우쳐 있어,\n"
        "누르면 세라믹층에 면내 변형이 생겨 전하가 발생한다. 두께 방향만 16배 확대.",
        fontproperties=fp, fontsize=8.5, ha="center", color="#444", linespacing=1.5)

ax.set_xlim(-37, 29)
ax.set_ylim(-8, 17)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("27 mm PZT 유니모프 벤더 디스크 단면 (단위 mm)",
             fontproperties=fp, fontsize=11.5, pad=6)
plt.tight_layout()
plt.savefig("/home/claude/cad/disc_section_drawing.png", dpi=200, facecolor="white")
print("saved")
