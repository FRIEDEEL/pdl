"""Backend access to the shared domain conversion policy."""

from pdl.author.geometry.protocols import PathSource
from pdl.author.transform.affine import AffineTransform
from pdl.author.transform.operations import transform_geometry


def placed_geometry(geometry: PathSource, transform: AffineTransform) -> PathSource:
    result = transform_geometry(geometry, transform)
    if not isinstance(result, PathSource):
        raise TypeError("Expected path-convertible geometry.")
    return result
