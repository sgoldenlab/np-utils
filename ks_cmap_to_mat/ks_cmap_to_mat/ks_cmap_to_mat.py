'''use `ks_cmap_to_mat <path/to/meta_file.ap.meta>` to convert a meta file into a KS channel map.
'''
import numpy as np
from . import ks_helpers as ksh
from pathlib import Path
import sys

def main(meta_file: Path):
    if isinstance(meta_file, str):
        meta_file = Path(meta_file)
    assert meta_file.exists(), f"Meta file {meta_file} not found."

    meta = ksh.readMeta(meta_file)
    AP, LF, SY = ksh.ChannelCountsIM(meta)
    channels = np.arange(AP)
    nShank, shankWidth, shankPitch, shankInd, xCoord, yCoord, connected = ksh.geomMapToGeom(meta)
    ksh.CoordsToKSChanMap(meta, channels, xCoord, yCoord, connected, shankInd, shankPitch, meta_file.stem, meta_file.parent)
    print(f"Created {meta_file.stem}_ksChanMap.mat in {meta_file.parent}")

def cli_main():
    if len(sys.argv) > 1:
        meta_file = Path(sys.argv[1])
        main(meta_file)
    else:
        print("Please provide the path to the meta file.")
        sys.exit(1)

if __name__ == "__main__":
    cli_main()