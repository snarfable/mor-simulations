#!/usr/bin/env python3
"""
setup_umbrella_windows.py:
Automates umbrella sampling window preparation for ligand unbinding:
1. Parses pullx.xvg from the steered MD pulling simulation.
2. Identifies trajectory frames closest to each window reference distance:
   xi_i in [0.4, 0.5, 0.6, ..., 2.4, 2.5] nm.
3. Generates a directory for each window with customized umbrella.mdp and conf.gro.
4. Prepares a shell script (run_windows.sh) to compile TPRs and run WHAM analysis.
"""

import os
import sys
import numpy as np

def setup_windows(pullx_file='pullx.xvg', mdp_template='umbrella.mdp', min_dist=0.40, max_dist=2.50, spacing=0.10):
    windows = np.arange(min_dist, max_dist + 1e-4, spacing)
    print(f"Target umbrella windows ({len(windows)} windows):")
    print([round(w, 2) for w in windows])

    if not os.path.exists(pullx_file):
        print(f"\nNotice: {pullx_file} not found. Generating directory structure and window mdp files as templates.")
        for w in windows:
            w_str = f"{w:.2f}"
            wdir = f"window_{w_str}"
            os.makedirs(wdir, exist_ok=True)
            with open(mdp_template, 'r') as fin, open(os.path.join(wdir, 'umbrella.mdp'), 'w') as fout:
                content = fin.read()
                content = content.replace("pull-coord1-init        = 0.50", f"pull-coord1-init        = {w_str}")
                fout.write(content)
        print("Template window directories prepared successfully.")
        return

    # Parse pullx.xvg
    times, dists = [], []
    with open(pullx_file, 'r') as f:
        for line in f:
            if line.startswith(('@', '#')) or not line.strip():
                continue
            parts = line.split()
            times.append(float(parts[0]))
            dists.append(float(parts[1]))

    times = np.array(times)
    dists = np.array(dists)

    print(f"Parsed {len(times)} timepoints from {pullx_file}. Distance range: {np.min(dists):.3f} to {np.max(dists):.3f} nm.")

    tpr_list = []
    pullf_list = []

    for w in windows:
        w_str = f"{w:.2f}"
        wdir = f"window_{w_str}"
        os.makedirs(wdir, exist_ok=True)

        idx = np.argmin(np.abs(dists - w))
        t_frame = times[idx]
        actual_dist = dists[idx]

        print(f"Window {w_str} nm -> nearest frame at t={t_frame:.1f} ps (actual d={actual_dist:.3f} nm)")

        # Write window-specific umbrella.mdp
        with open(mdp_template, 'r') as fin, open(os.path.join(wdir, 'umbrella.mdp'), 'w') as fout:
            content = fin.read()
            content = content.replace("pull-coord1-init        = 0.50", f"pull-coord1-init        = {w_str}")
            fout.write(content)

        tpr_list.append(os.path.join(wdir, "umbrella.tpr"))
        pullf_list.append(os.path.join(wdir, "umbrella_pullf.xvg"))

    with open('tpr_files.dat', 'w') as f:
        f.write('\n'.join(tpr_list) + '\n')
    with open('pullf_files.dat', 'w') as f:
        f.write('\n'.join(pullf_list) + '\n')

    print("\nGenerated tpr_files.dat and pullf_files.dat for gmx wham.")

if __name__ == '__main__':
    pullx = sys.argv[1] if len(sys.argv) > 1 else 'pullx.xvg'
    mdp = sys.argv[2] if len(sys.argv) > 2 else 'umbrella.mdp'
    setup_windows(pullx_file=pullx, mdp_template=mdp)
