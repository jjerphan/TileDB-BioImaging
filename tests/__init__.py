import multiprocessing
import os
from pathlib import Path

import numpy as np

import tiledb

if os.name == "posix":
    multiprocessing.set_start_method("forkserver")


DATA_DIR = Path(__file__).parent / "data"


def get_schema(x_size, y_size, c_size=3, compressor=tiledb.ZstdFilter(level=0)):
    dims = []
    x_tile = min(x_size, 1024)
    y_tile = min(y_size, 1024)
    if isinstance(compressor, tiledb.WebpFilter):
        x_size *= c_size
        x_tile *= c_size
    else:
        dims.append(tiledb.Dim("C", (0, c_size - 1), tile=c_size, dtype=np.uint32))
    dims.append(tiledb.Dim("Y", (0, y_size - 1), tile=y_tile, dtype=np.uint32))
    dims.append(tiledb.Dim("X", (0, x_size - 1), tile=x_tile, dtype=np.uint32))

    return tiledb.ArraySchema(
        domain=tiledb.Domain(*dims),
        attrs=[tiledb.Attr(dtype=np.uint8, filters=tiledb.FilterList([compressor]))],
    )


def get_path(uri):
    return DATA_DIR / uri
