"""지그 v2 단면도 (y = 0 평면) -- piezo_jig_v2.py 의 치수를 그대로 가져온다."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import piezo_jig_v2 as J

fp = None
for f in font_manager.findSystemFonts():
    if "NotoSansCJK" in f or "NotoSerifCJK" in f:
        fp = font_manager.FontProperties(fname=f)
        if "Sans" in f:
            break

parts = {
    "하판": (J.build_base(), "#b8c4d6"),
    "브리지": (J.build_bridge(), "#c9d9b8"),
    "플런저": (J.build_plunger(), "#e6c9a8"),
    "버저(가정 두께)": (J.build_buzzer(), "#555555"),
}

fig, ax = plt.subplots(figsize=(8, 7))
for name, (mesh, color) in parts.items():
    sec = mesh.section(plane_origin=[0, 0, 0], plane_normal=[0, 1, 0])
    if sec is None:
        continue
    for poly in sec.to_planar(to_2D=[[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])[0].polygons_full:
        x, y = poly.exterior.xy
        ax.fill(x, y, color=color, ec="black", lw=0.6)
        for hole in poly.interiors:
            hx, hy = hole.xy
            ax.fill(hx, hy, color="white", ec="black", lw=0.6)
    ax.plot([], [], color=color, lw=8, label=name)

ax.annotate("F = mg (추 1–5 kg)", xy=(0, J.Z_PLAT_BOT + J.T_PLAT + J.H_POST + 2),
            xytext=(0, J.Z_PLAT_BOT + J.T_PLAT + J.H_POST + 14), ha="center",
            arrowprops=dict(arrowstyle="->", lw=1.2), fontproperties=fp, fontsize=10)
ax.text(J.PLATE / 2 + 2, J.Z_CASE_BOT + J.T_CASE / 2, "버저 Ø22\n두께 %.0f mm(가정)" % J.T_CASE,
        fontproperties=fp, fontsize=8.5, va="center")
ax.text(J.PLATE / 2 + 2, J.Z_SLEEVE_TOP + J.GAP_TRAVEL / 2, "여유 %.0f mm" % J.GAP_TRAVEL,
        fontproperties=fp, fontsize=8.5, va="center")
ax.set_aspect("equal")
ax.set_xlim(-48, 62)
ax.set_ylim(-4, J.Z_PLAT_BOT + J.T_PLAT + J.H_POST + 20)
ax.set_xlabel("x (mm)")
ax.set_ylabel("z (mm)")
ax.legend(prop=fp, loc="upper left", fontsize=9, frameon=False)
ax.set_title("정적 가압 지그 v2 단면 (y = 0)", fontproperties=fp, fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(J.OUT, "jig2_section.png"), dpi=200, facecolor="white")
print("saved")
