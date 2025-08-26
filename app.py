import io
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# -----------------------------
# Built-in 4×4 examples
# -----------------------------
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
    "Custom (enter below)": None,
}

# -----------------------------
# Helpers: parsing & properties
# -----------------------------

def parse_custom_matrix(txt: str):
    """
    Parse 4 lines of 4 numbers (space- or comma-separated) into a 4x4 numpy array.
    Returns (array or None, error_message or None)
    """
    if not txt.strip():
        return None, "Enter 4 lines with 4 numbers each (space/comma separated)."
    rows = [line.strip() for line in txt.strip().splitlines() if line.strip()]
    if len(rows) != 4:
        return None, "Expected exactly 4 lines."
    data = []
    for i, row in enumerate(rows):
        parts = [p for p in row.replace(",", " ").split() if p]
        if len(parts) != 4:
            return None, f"Line {i+1} has {len(parts)} entries; expected 4."
        try:
            # Keep floats, but cast to int when safe to avoid 1.0 vs 1 equality surprises
            parsed = []
            for x in parts:
                if "." in x:
                    val = float(x)
                    if val.is_integer():
                        val = int(val)
                else:
                    val = int(x)
                parsed.append(val)
            data.append(parsed)
        except ValueError:
            return None, f"Non-numeric value on line {i+1}."
    arr = np.array(data)
    if arr.shape != (4, 4):
        return None, "Parsed matrix is not 4×4."
    return arr, None


def magic_constant(A):
    return np.sum(A[0, :])


def is_magic(A):
    M = magic_constant(A)
    rows_ok = all(np.sum(A[i, :]) == M for i in range(4))
    cols_ok = all(np.sum(A[:, j]) == M for j in range(4))
    diags_ok = (np.sum(np.diag(A)) == M) and (np.sum(np.diag(np.fliplr(A))) == M)
    return rows_ok and cols_ok and diags_ok, M


def is_associative(A):
    """Associated/associative: a[i,j] + a[n-1-i, n-1-j] is constant."""
    n = A.shape[0]
    K = A[0, 0] + A[n-1, n-1]
    for i in range(n):
        for j in range(n):
            if A[i, j] + A[n-1-i, n-1-j] != K:
                return False, None
    return True, K


def is_most_perfect(A, M=None):
    """
    For 4×4: most-perfect (pandiagonal) squares are magic and satisfy:
      (1) Every 2×2 adjacent block INCLUDING wrap-around sums to M.
      (2) All broken diagonals (with wrap) sum to M.
    """
    ok_magic, Mcalc = is_magic(A)
    if not ok_magic:
        return False
    M = Mcalc if M is None else M

    n = 4
    # (1) Every 2×2 block with wrap
    for r in range(n):
        for c in range(n):
            s = A[r, c] + A[r, (c+1) % n] + A[(r+1) % n, c] + A[(r+1) % n, (c+1) % n]
            if s != M:
                return False

    # (2) All broken diagonals with wrap (both directions)
    for r0 in range(n):
        for c0 in range(n):
            s1 = sum(A[(r0 + k) % n, (c0 + k) % n] for k in range(n))
            s2 = sum(A[(r0 + k) % n, (c0 - k) % n] for k in range(n))
            if s1 != M or s2 != M:
                return False

    return True


def classify_square(A):
    ok_magic, M = is_magic(A)
    if not ok_magic:
        return "Not magic", {"magic": False}
    mp = is_most_perfect(A, M)
    if mp:
        return "Most-perfect (pandiagonal)", {"magic": True, "M": M, "most_perfect": True}
    assoc, K = is_associative(A)
    if assoc:
        return "Associative (associated)", {"magic": True, "M": M, "associative": True, "pair_sum": K}
    return "Normal magic", {"magic": True, "M": M}

# -----------------------------
# Geometry for overlays
# -----------------------------

def positions_and_order_values(A, order_mode="auto"):
    """
    Returns:
      - pos_dict: mapping step k=1..16 -> complex position (centered later)
      - order_values: list of the value placed at step k (len=16)
    order_mode:
      - "auto": if entries are exactly {1..16}, use that numeric order; else ascending by numeric value
      - "ascending": ascending by numeric value
      - "row-major": scan rows left->right, top->bottom (ignores values)
    """
    flat = A.flatten().tolist()
    if order_mode == "row-major":
        order_values = [A[r, c] for r in range(4) for c in range(4)]
    elif order_mode == "ascending":
        order_values = sorted(flat)
    else:  # auto
        order_values = list(range(1, 17)) if set(flat) == set(range(1, 17)) else sorted(flat)

    used = set()
    pos_dict = {}
    k = 1
    # Use stable assignment in row-major order to handle duplicates gracefully
    for target in order_values:
        found = False
        for r in range(4):
            for c in range(4):
                if (r, c) in used:
                    continue
                if A[r, c] == target:
                    pos_dict[k] = complex(c, -r)
                    used.add((r, c))
                    k += 1
                    found = True
                    break
            if found:
                break

    while k <= 16:
        for r in range(4):
            for c in range(4):
                if (r, c) not in used:
                    pos_dict[k] = complex(c, -r)
                    used.add((r, c))
                    k += 1
                    break
            if k > 16:
                break

    return pos_dict, order_values


def build_poly_from_positions(pos_dict):
    poly = np.array([pos_dict[k] for k in range(1, 17)], dtype=complex)
    return poly - poly.mean()


def curved_segment(p, q, curvature=0.55, samples=120, flip=False):
    m = 0.5 * (p + q)
    v = q - p
    if v == 0:
        return np.array([p, q])
    n = 1j * v
    n /= (abs(n) + 1e-9)
    c = m + (curvature * (-1 if flip else 1)) * n * abs(v) * 0.6
    t = np.linspace(0, 1, samples)
    return (1 - t) ** 2 * p + 2 * (1 - t) * t * c + t ** 2 * q


def make_path(poly, curved=True, curvature=0.55, samples=120, alternate=True):
    segs = []
    for i in range(len(poly) - 1):
        p, q = poly[i], poly[i + 1]
        if curved:
            segs.append(
                curved_segment(
                    p,
                    q,
                    curvature=curvature,
                    samples=samples,
                    flip=(i % 2 == 1) if alternate else False,
                )
            )
        else:
            segs.append(np.array([p, q]))
    return segs


def dihedral_transforms(points):
    def rotate(zs, k):
        return zs * ((1j) ** k)

    def reflect_y(zs):
        return np.array([-z.real + 1j * z.imag for z in zs])

    out = [rotate(points, k) for k in range(4)]
    ref = reflect_y(points)
    out += [rotate(ref, k) for k in range(4)]
    return out


def draw_overlay(
    A,
    order_mode="auto",
    curved=True,
    curvature=0.55,
    samples=120,
    labels=False,
    labels_mode="Traversal index (1..16)",
    grid=False,
    lw=1.2,
    alpha=0.3,
):
    # positions + order values
    pos_raw, order_values = positions_and_order_values(A, order_mode=order_mode)
    center = np.mean(list(pos_raw.values()))
    # centered poly
    poly = np.array([pos_raw[k] - center for k in range(1, 17)], dtype=complex)

    variants = dihedral_transforms(poly)

    fig, ax = plt.subplots(figsize=(6, 6), facecolor="black")
    ax.set_facecolor("black")

    # draw paths
    for pts in variants:
        segs = make_path(pts, curved=curved, curvature=curvature, samples=samples)
        for seg in segs:
            ax.plot(seg.real, seg.imag, color="white", lw=lw, alpha=alpha, zorder=1)

    # optional grid
    if grid:
        extent = 3.5
        xs = np.arange(-extent, extent + 1, 1)
        for x in xs:
            ax.plot([x, x], [-extent, extent], color="white", alpha=0.1, lw=0.5, zorder=0)
            ax.plot([-extent, extent], [x, x], color="white", alpha=0.1, lw=0.5, zorder=0)

    # labels
    if labels:
        for k in range(1, 17):
            zc = pos_raw[k] - center
            if labels_mode == "Traversal index (1..16)":
                text = str(k)
            elif labels_mode == "Cell values":
                text = str(order_values[k - 1])
            else:  # Both
                text = f"{k} / {order_values[k - 1]}"
            ax.text(
                zc.real,
                zc.imag,
                text,
                ha="center",
                va="center",
                color="yellow",
                fontsize=8,
                alpha=0.9,
                zorder=2,
            )

    ax.set_aspect("equal")
    ax.axis("off")
    plt.tight_layout()
    return fig


# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🔮 Hamiltonian–Dihedral Overlay Explorer (4×4 Magic Squares)")

colA, colB = st.columns([1, 1])
with colA:
    square_choice = st.selectbox("Choose a square:", list(SQUARES.keys()))
with colB:
    order_mode = st.selectbox(
        "Traversal order for 1→…→16:",
        ["auto", "ascending", "row-major"],
        help="Auto: use 1..16 if present, else ascending values. Row-major ignores values.",
    )

custom_matrix = None
if square_choice == "Custom (enter below)":
    st.markdown("**Enter a 4×4 grid (numbers separated by spaces or commas):**")
    default_txt = "1, 2, 3, 4\n5, 6, 7, 8\n9, 10, 11, 12\n13, 14, 15, 16"
    txt = st.text_area("Custom 4×4 matrix", height=140, value=default_txt)
    custom_matrix, err = parse_custom_matrix(txt)
    if err:
        st.error(err)
    else:
        A = custom_matrix
else:
    A = SQUARES[square_choice]

# Controls
curvature = st.slider("Curvature (0 = straight, 1 = braided)", 0.0, 1.0, 0.55, 0.05)
samples = st.slider("Curve smoothness (# samples)", 20, 300, 120, 10)
lw = st.slider("Line width", 0.5, 3.0, 1.2, 0.1)
alpha = st.slider("Line transparency", 0.05, 1.0, 0.3, 0.05)
labels = st.checkbox("Show labels", value=False)
labels_mode = st.selectbox(
    "Label content:", ["Traversal index (1..16)", "Cell values", "Both"], index=0
)
grid = st.checkbox("Show faint grid", value=False)

# Classification panel
if A is not None:
    cls, meta = classify_square(A)
    st.markdown(f"**Classification:** {cls}")
    if "M" in meta:
        st.markdown(f"- Magic constant **M** = {meta['M']}")
    if meta.get("associative"):
        st.markdown(f"- Associative pair sum **K** = {meta['pair_sum']}")
    if meta.get("most_perfect"):
        st.markdown(
            f"- Satisfies 2×2 wrap-around and broken-diagonal (pandiagonal) constraints"
        )

# Draw & export
if A is not None:
    fig = draw_overlay(
        A,
        order_mode=order_mode,
        curved=(curvature > 0),
        curvature=curvature,
        samples=samples,
        labels=labels,
        labels_mode=labels_mode,
        grid=grid,
        lw=lw,
        alpha=alpha,
    )
    st.pyplot(fig)

    # Download as PNG
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    st.download_button(
        label="Download image (PNG)",
        data=buf.getvalue(),
        file_name="overlay.png",
        mime="image/png",
    )
else:
    st.info("Provide a valid 4×4 custom matrix to render.")
