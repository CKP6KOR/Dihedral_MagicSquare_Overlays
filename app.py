import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# ============================================================
# Define canonical 4×4 squares
# ============================================================

CHAUTISA = np.array([
    [7, 12, 1, 14],
    [2, 13, 8, 11],
    [16, 3, 10, 5],
    [9, 6, 15, 4]
], dtype=int)

DURER = np.array([
    [16, 3, 2, 13],
    [5, 10, 11, 8],
    [9, 6, 7, 12],
    [4, 15, 14, 1]
], dtype=int)

NORMAL = np.array([
    [1, 15, 14, 4],
    [12, 6, 7, 9],
    [8, 10, 11, 5],
    [13, 3, 2, 16]
], dtype=int)

SQUARES = {
    "Most-perfect (Chautisa)": CHAUTISA,
    "Associative (Dürer 1514)": DURER,
    "Normal (non-associative)": NORMAL,
}

# ============================================================
# Utilities
# ============================================================

def positions_from_square(square):
    pos = {}
    for r in range(4):
        for c in range(4):
            pos[int(square[r, c])] = complex(c, -r)
    return pos

def build_ordered_polyline(square):
    pos = positions_from_square(square)
    poly = np.array([pos[k] for k in range(1, 17)], dtype=complex)
    return poly - poly.mean()

def curved_segment(p, q, curvature=0.55, samples=120, flip=False):
    m = 0.5*(p+q)
    v = q - p
    if v == 0:
        return np.array([p, q])
    n = 1j*v
    n /= (abs(n) + 1e-9)
    c = m + (curvature * (-1 if flip else 1)) * n * abs(v) * 0.6
    t = np.linspace(0, 1, samples)
    return (1-t)**2*p + 2*(1-t)*t*c + t**2*q

def make_path(poly, curved=True, curvature=0.55, samples=120, alternate=True):
    segs = []
    for i in range(len(poly)-1):
        p, q = poly[i], poly[i+1]
        if curved:
            segs.append(curved_segment(p, q, curvature=curvature, samples=samples,
                                       flip=(i%2==1) if alternate else False))
        else:
            segs.append(np.array([p, q]))
    return segs

def dihedral_transforms(points):
    def rotate(zs, k): return zs * ((1j)**k)
    def reflect_y(zs): return np.array([-z.real + 1j*z.imag for z in zs])
    out = [rotate(points, k) for k in range(4)]
    ref = reflect_y(points)
    out += [rotate(ref, k) for k in range(4)]
    return out

def draw_overlay(square, curved=True, curvature=0.55, samples=120,
                 labels=False, grid=False, lw=1.2, alpha=0.3):
    poly = build_ordered_polyline(square)
    variants = dihedral_transforms(poly)

    fig, ax = plt.subplots(figsize=(6,6), facecolor="black")
    ax.set_facecolor("black")
    for pts in variants:
        segs = make_path(pts, curved=curved, curvature=curvature, samples=samples)
        for seg in segs:
            ax.plot(seg.real, seg.imag, color="white", lw=lw, alpha=alpha)

    if grid:
        extent = 3.5
        xs = np.arange(-extent, extent+1, 1)
        for x in xs:
            ax.plot([x, x], [-extent, extent], color="white", alpha=0.1, lw=0.5)
            ax.plot([-extent, extent], [x, x], color="white", alpha=0.1, lw=0.5)

    if labels:
        pos = positions_from_square(square)
        center = np.mean(list(pos.values()))
        for val, z in pos.items():
            x, y = (z - center).real, (z - center).imag
            ax.text(x, y, str(val), ha="center", va="center",
                    color="yellow", fontsize=8, alpha=0.7)

    ax.set_aspect("equal")
    ax.axis("off")
    plt.tight_layout()
    return fig

# ============================================================
# Streamlit UI
# ============================================================

st.title("🔮 Hamiltonian–Dihedral Overlay Explorer (4×4 Magic Squares)")

square_choice = st.selectbox("Choose a 4×4 magic square type:", list(SQUARES.keys()))

curvature = st.slider("Curvature (0 = straight, 1 = very curved)", 0.0, 1.0, 0.55, 0.05)
samples = st.slider("Curve smoothness (# of samples)", 20, 300, 120, 10)
lw = st.slider("Line width", 0.5, 3.0, 1.2, 0.1)
alpha = st.slider("Line transparency", 0.05, 1.0, 0.3, 0.05)

labels = st.checkbox("Show numbers", value=False)
grid = st.checkbox("Show faint 4×4 grid", value=False)

fig = draw_overlay(SQUARES[square_choice],
                   curved=(curvature>0),
                   curvature=curvature,
                   samples=samples,
                   labels=labels,
                   grid=grid,
                   lw=lw,
                   alpha=alpha)

st.pyplot(fig)
