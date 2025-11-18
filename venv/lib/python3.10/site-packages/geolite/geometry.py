import json
from typing import List, Optional, Tuple, Union

import numpy as np
from shapely import box, wkt
from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry


def to_shapely(
    geom: Union[
        BaseGeometry,
        Union[List[str], Tuple[str], List[float], Tuple[float], np.ndarray],
        str,
        dict,
    ]
) -> Optional[BaseGeometry]:
    if isinstance(geom, BaseGeometry):
        return geom
    elif isinstance(geom, dict):
        return shape(geom)
    elif isinstance(geom, str):
        return shape(json.loads(geom)) if geom.startswith("{") else wkt.loads(geom)
    elif isinstance(geom, (list, tuple, np.ndarray)) and len(geom) == 4:
        return box(*[float(c) for c in geom], ccw=True)
    return None
