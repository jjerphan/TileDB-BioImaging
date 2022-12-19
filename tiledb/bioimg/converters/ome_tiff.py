from typing import Any, Dict, Mapping

import jsonpickle as json
import numpy as np
import tifffile

from .base import Axes, ImageConverter, ImageReader, ImageWriter


class OMETiffReader(ImageReader):
    def __init__(self, input_path: str):
        """
        OME-TIFF image reader

        :param input_path: The path to the TIFF image
        """
        self._tiff = tifffile.TiffFile(input_path)
        # XXX ignore all but the first series
        self._levels = self._tiff.series[0].levels

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._tiff.close()

    @property
    def axes(self) -> Axes:
        return Axes(self._levels[0].axes.replace("S", "C"))

    @property
    def level_count(self) -> int:
        return len(self._levels)

    def level_image(self, level: int) -> np.ndarray:
        return self._levels[level].asarray()

    def level_metadata(self, level: int) -> Dict[str, Any]:
        series = self._levels[level]
        if level == 0:
            omexml = self._tiff.ome_metadata
            metadata = tifffile.xml2dict(omexml) if omexml else {}
            metadata["axes"] = series.axes
        else:
            metadata = None

        keyframe = series.keyframe
        write_kwargs = dict(
            subifds=len(series.levels) - 1 if level == 0 else None,
            metadata=metadata,
            photometric=keyframe.photometric,
            planarconfig=keyframe.planarconfig,
            extrasamples=keyframe.extrasamples,
            rowsperstrip=keyframe.rowsperstrip,
            bitspersample=keyframe.bitspersample,
            compression=keyframe.compression,
            predictor=keyframe.predictor,
            subsampling=keyframe.subsampling,
            jpegtables=keyframe.jpegtables,
            colormap=keyframe.colormap,
            subfiletype=keyframe.subfiletype or None,
            software=keyframe.software,
            tile=keyframe.tile,
            datetime=keyframe.datetime,
            resolution=keyframe.resolution,
            resolutionunit=keyframe.resolutionunit,
        )
        return {"json_write_kwargs": json.dumps(write_kwargs)}

    @property
    def group_metadata(self) -> Dict[str, Any]:
        writer_kwargs = dict(
            bigtiff=self._tiff.is_bigtiff,
            byteorder=self._tiff.byteorder,
            append=self._tiff.is_appendable,
            imagej=self._tiff.is_imagej,
            ome=self._tiff.is_ome,
        )
        return {"json_tiffwriter_kwargs": json.dumps(writer_kwargs)}


class OMETiffWriter(ImageWriter):
    def __init__(self, output_path: str):
        self._output_path = output_path

    def write_group_metadata(self, metadata: Mapping[str, Any]) -> None:
        tiffwriter_kwargs = json.loads(metadata["json_tiffwriter_kwargs"])
        self._writer = tifffile.TiffWriter(self._output_path, **tiffwriter_kwargs)

    def write_level_image(
        self, level: int, image: np.ndarray, metadata: Mapping[str, Any]
    ) -> None:
        write_kwargs = json.loads(metadata["json_write_kwargs"])
        self._writer.write(image, **write_kwargs)

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._writer.close()


class OMETiffConverter(ImageConverter):
    """Converter of Tiff-supported images to TileDB Groups of Arrays"""

    _ImageReaderType = OMETiffReader
    _ImageWriterType = OMETiffWriter