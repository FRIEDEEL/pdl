# Changelog

## Unreleased

### Added

- Basic lines, polylines, circles, rectangles, polygons, elliptical arcs and
  quadratic/cubic paths with explicit closing and multiple subpaths.
- Solid RGB fill and stroke, fill rules, line caps and joins.
- Ordered, fixed-size millimeter canvas with SVG and standalone TikZ exports.
- TikZ-style and SVG-style arc constructors, a dual-backend gallery and tests.

### Limitations

- Generic arc lowering and rotated TikZ arcs use cubic approximation.
- Text, groups, layers, automatic layout and backend-specific options are not
  included in this stage.
