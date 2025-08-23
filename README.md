An **interactive Streamlit app** for exploring Hamiltonian–dihedral overlays of 4×4 magic squares.

We introduce the Hamiltonian–dihedral overlay as a new geometric method for visualizing 4×4 magic squares. Given a square, one traces the Hamiltonian path obtained by connecting consecutive integers 1→2→…→16 and then overlays all eight dihedral symmetries of the square.

We show that this procedure produces qualitatively distinct motifs depending on the algebraic type of the square. Most-perfect (pandiagonal) squares yield isotropic braided structures with circular annuli and, in the straight-line case, a central hexagon. Associative (Dürer-type) squares produce cross–diamond rosettes with strong axis–diagonal lobes, while normal, non-associative squares result in irregular, anisotropic overlays. These visual differences correspond directly to underlying combinatorial constraints, establishing a novel correspondence between square type and geometric isotropy pattern. An open-source interactive tool enables users to explore the parameter space of curvature and rendering.

**What it does**

Choose among canonical 4×4 magic squares:

Most-perfect (Chautisa / Khajuraho)

Associative (Dürer 1514)

Normal (non-associative)

Draw the Hamiltonian path (1→2→…→16).

Apply all 8 dihedral symmetries (D₄) and overlay the paths.

**Adjust parameters live**:

Curvature (0 = straight, 1 = braided)

Smoothness (# of samples per curve)

Line width & transparency

Toggle grid and number labels


**Clone this repo:**
git clone https://github.com/CKP6KOR/Dihedral_MagicSquare_Overlays.git

cd magic-square-overlays

**Install dependencies:**
pip install -r requirements.txt

**Run the app:**
streamlit run app.py
Open the local URL shown in your terminal (usually http://localhost:8501).

**Files**
app.py – main Streamlit application

requirements.txt – dependencies (streamlit, matplotlib, numpy)

README.md – this file

**Examples : **

**Most-perfect (Chautisa) magic square : Curvature = 0**
<img width="790" height="792" alt="image" src="https://github.com/user-attachments/assets/430b860b-b163-49ab-920f-eb879bc36cb0" />

**Associative (Dürer 1514) magic square : Curvature = 0**
<img width="785" height="782" alt="image" src="https://github.com/user-attachments/assets/3bda8aa8-1b3f-4c0a-a8a7-836b6ed4c520" />

**Normal (non-associative) magic square : Curvature = 0**
<img width="783" height="787" alt="image" src="https://github.com/user-attachments/assets/19139f78-c84c-4ffe-abaa-1cf0efb3903a" />
