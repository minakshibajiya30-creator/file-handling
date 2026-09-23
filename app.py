import streamlit as st
from pathlib import Path
import datetime

# ----------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="File Manager Studio",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# All operations are sandboxed inside this folder so the app is safe to
# demo/deploy publicly (no arbitrary filesystem access).
WORKSPACE = Path("workspace")
WORKSPACE.mkdir(exist_ok=True)

# ----------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6C63FF, #3AB0FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .subtitle {
        color: #888;
        font-size: 1.05rem;
        margin-top: 0;
        margin-bottom: 1.5rem;
    }
    .stat-card {
        background: #1e1e2f0d;
        border: 1px solid rgba(120,120,150,0.15);
        border-radius: 14px;
        padding: 18px 20px;
        text-align: center;
    }
    .stat-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #6C63FF;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #888;
    }
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.5rem 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------
st.markdown('<p class="main-title">🗂️ File Manager Studio</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Create, read, update, and delete files through a clean, safe, sandboxed UI.</p>',
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# Stats row
# ----------------------------------------------------------------------
files = sorted([f for f in WORKSPACE.iterdir() if f.is_file()])
total_size = sum(f.stat().st_size for f in files)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        f'<div class="stat-card"><div class="stat-number">{len(files)}</div>'
        f'<div class="stat-label">Files in workspace</div></div>',
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f'<div class="stat-card"><div class="stat-number">{total_size}</div>'
        f'<div class="stat-label">Total bytes</div></div>',
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f'<div class="stat-card"><div class="stat-number">{datetime.datetime.now().strftime("%H:%M")}</div>'
        f'<div class="stat-label">Local time</div></div>',
        unsafe_allow_html=True,
    )

st.write("")

# ----------------------------------------------------------------------
# Sidebar file browser
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("📁 Workspace")
    if files:
        for f in files:
            st.write(f"📄 `{f.name}`  ·  {f.stat().st_size} B")
    else:
        st.caption("No files yet. Create one to get started!")
    st.divider()
    st.caption("All files live inside a local `workspace/` folder, keeping this demo safe to run.")

# ----------------------------------------------------------------------
# Main tabs
# ----------------------------------------------------------------------
tab_create, tab_read, tab_update, tab_delete = st.tabs(
    ["➕ Create", "📖 Read", "✏️ Update", "🗑️ Delete"]
)

# ---------------- CREATE ----------------
with tab_create:
    st.subheader("Create a new file")
    name = st.text_input("File name", placeholder="notes.txt", key="create_name")
    content = st.text_area("File content", height=180, key="create_content")

    if st.button("Create File", type="primary", key="create_btn"):
        if not name.strip():
            st.error("Please enter a file name.")
        else:
            path = WORKSPACE / name
            if path.exists():
                st.error(f"'{name}' already exists. Choose a different name or use Update.")
            else:
                try:
                    path.write_text(content)
                    st.success(f"'{name}' created successfully!")
                    st.rerun()
                except Exception as err:
                    st.error(f"An error occurred: {err}")

# ---------------- READ ----------------
with tab_read:
    st.subheader("Read a file")
    if not files:
        st.info("No files available yet. Create one first.")
    else:
        choice = st.selectbox("Choose a file", [f.name for f in files], key="read_choice")
        if choice:
            path = WORKSPACE / choice
            try:
                text = path.read_text()
                st.code(text if text.strip() else "(empty file)", language=None)
                st.download_button("⬇️ Download", data=text, file_name=choice)
            except Exception as err:
                st.error(f"An error occurred: {err}")

# ---------------- UPDATE ----------------
with tab_update:
    st.subheader("Update a file")
    if not files:
        st.info("No files available yet. Create one first.")
    else:
        choice = st.selectbox("Choose a file", [f.name for f in files], key="update_choice")
        action = st.radio("Action", ["Rename", "Append content", "Overwrite content"], horizontal=True)
        path = WORKSPACE / choice

        if action == "Rename":
            new_name = st.text_input("New file name", key="rename_input")
            if st.button("Rename", type="primary", key="rename_btn"):
                new_path = WORKSPACE / new_name
                if not new_name.strip():
                    st.error("Please enter a new file name.")
                elif new_path.exists():
                    st.error(f"'{new_name}' already exists.")
                else:
                    try:
                        path.rename(new_path)
                        st.success(f"Renamed to '{new_name}'!")
                        st.rerun()
                    except Exception as err:
                        st.error(f"An error occurred: {err}")

        elif action == "Append content":
            extra = st.text_area("Text to append", key="append_input")
            if st.button("Append", type="primary", key="append_btn"):
                try:
                    with open(path, "a") as fs:
                        fs.write("\n" + extra)
                    st.success("Content appended!")
                except Exception as err:
                    st.error(f"An error occurred: {err}")

        elif action == "Overwrite content":
            new_content = st.text_area("New content", key="overwrite_input")
            if st.button("Overwrite", type="primary", key="overwrite_btn"):
                try:
                    path.write_text(new_content)
                    st.success("File overwritten!")
                except Exception as err:
                    st.error(f"An error occurred: {err}")

# ---------------- DELETE ----------------
with tab_delete:
    st.subheader("Delete a file")
    if not files:
        st.info("No files available yet. Create one first.")
    else:
        choice = st.selectbox("Choose a file", [f.name for f in files], key="delete_choice")
        st.warning(f"This will permanently delete '{choice}'.")
        if st.button("🗑️ Delete File", type="primary", key="delete_btn"):
            try:
                (WORKSPACE / choice).unlink()
                st.success(f"'{choice}' deleted successfully!")
                st.rerun()
            except Exception as err:
                st.error(f"An error occurred: {err}")

st.divider()
st.caption("Built with Streamlit · A simple, sandboxed CRUD file manager.")
