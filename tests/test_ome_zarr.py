import numpy as np
import tiledb

from tiledbimg.openslide import LevelInfo, TileDBOpenSlide

from . import get_path


def test_ome_zarr():
    t = TileDBOpenSlide.from_group_uri(get_path("CMU-1-Small-Region-Zarr.tiledb"))

    schemas = [
        tiledb.ArraySchema(
            domain=tiledb.Domain(
                *[
                    tiledb.Dim(name="X", domain=(0, 2219), tile=1024, dtype=np.uint64),
                    tiledb.Dim(name="Y", domain=(0, 2966), tile=1024, dtype=np.uint64),
                ]
            ),
            sparse=False,
            attrs=[
                tiledb.Attr(
                    name="rgb",
                    dtype=[("f0", "u1"), ("f1", "u1"), ("f2", "u1")],
                    var=False,
                    nullable=False,
                    filters=tiledb.FilterList([tiledb.ZstdFilter(level=0)]),
                )
            ],
            cell_order="row-major",
            tile_order="row-major",
            capacity=10000,
        ),
        tiledb.ArraySchema(
            domain=tiledb.Domain(
                *[
                    tiledb.Dim(name="X", domain=(0, 386), tile=387, dtype=np.uint64),
                    tiledb.Dim(name="Y", domain=(0, 462), tile=463, dtype=np.uint64),
                ]
            ),
            sparse=False,
            attrs=[
                tiledb.Attr(
                    name="rgb",
                    dtype=[("f0", "u1"), ("f1", "u1"), ("f2", "u1")],
                    var=False,
                    nullable=False,
                    filters=tiledb.FilterList([tiledb.ZstdFilter(level=1)]),
                )
            ],
            cell_order="row-major",
            tile_order="row-major",
            capacity=10000,
        ),
        tiledb.ArraySchema(
            domain=tiledb.Domain(
                *[
                    tiledb.Dim(name="X", domain=(0, 1279), tile=1024, dtype=np.uint64),
                    tiledb.Dim(name="Y", domain=(0, 430), tile=431, dtype=np.uint64),
                ]
            ),
            sparse=False,
            attrs=[
                tiledb.Attr(
                    name="rgb",
                    dtype=[("f0", "u1"), ("f1", "u1"), ("f2", "u1")],
                    var=False,
                    nullable=False,
                    filters=tiledb.FilterList([tiledb.ZstdFilter(level=2)]),
                )
            ],
            cell_order="row-major",
            tile_order="row-major",
            capacity=10000,
        ),
    ]

    assert (
        t.level_info[0] == LevelInfo(uri="", level=0, dimensions=schemas[0].shape)
        and t.level_info[1] == LevelInfo(uri="", level=1, dimensions=schemas[1].shape)
        and t.level_info[2] == LevelInfo(uri="", level=2, dimensions=schemas[2].shape)
    )
    assert t.level_count == 3
    assert t.dimensions == (2220, 2967)
    assert t.level_dimensions == ((2220, 2967), (387, 463), (1280, 431))
    assert t.level_downsamples == ()
