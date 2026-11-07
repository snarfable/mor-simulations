#!/usr/bin/env python3
"""
load_nx.py:
PyMOL helper script to load GROMACS .ndx index files and create PyMOL selections
for each index group.

Usage in PyMOL:
    run load_nx.py
    load_ndx index.ndx
    load_ndx index.ndx, complex_amphipol
"""

def load_ndx(ndx_file, obj_name="*"):
    """
    Loads a GROMACS .ndx file and creates PyMOL selections for each group.
    
    Parameters
    ----------
    ndx_file : str
        Path to the GROMACS .ndx file.
    obj_name : str, optional
        Name of the loaded object in PyMOL to restrict selections to (default: "*").
    """
    try:
        from pymol import cmd
    except ImportError:
        print("Error: PyMOL python module not found. Run this script inside PyMOL ('run load_nx.py').")
        return

    current_group = None
    groups = {}

    with open(ndx_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("[") and line.endswith("]"):
                current_group = line.strip("[] ").replace(" ", "_")
                groups[current_group] = []
            elif current_group:
                groups[current_group].extend(line.split())

    for grp, atom_ids in groups.items():
        # GROMACS 1-based atom indices map to PyMOL 'id'
        # Chunk into batches of 500 to prevent command line length overflow
        batch_size = 500
        for i in range(0, len(atom_ids), batch_size):
            chunk = "+".join(atom_ids[i:i + batch_size])
            sel_str = f"({obj_name} and id {chunk})"
            if i == 0:
                cmd.select(grp, sel_str)
            else:
                cmd.select(grp, f"{grp} or {sel_str}")
        print(f"Created PyMOL selection '{grp}' with {len(atom_ids)} atoms")

try:
    from pymol import cmd
    cmd.extend("load_ndx", load_ndx)
except ImportError:
    pass
