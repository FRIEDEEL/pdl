"""Geometric invariants and independent perspective ray visibility regressions."""

from dataclasses import replace

import pytest

from pdl import Color
from pdl.extensions.spatial import Point3D, Vector3D
from playground.visibility.bsp import Face, distances, project, split
from playground.visibility.oracle import area, check
from playground.visibility.scenes import CAMERA, crossing, max_trap, random_faces, world


@pytest.mark.parametrize("seed", [17, 29, 71])
def test_random_visibility(seed: int) -> None:
    faces = random_faces(24, 0.35, seed)
    author, metrics, fragments = project(faces, CAMERA)
    assert len(author.children) == len(fragments) == len(faces) + metrics.splits
    result = check(faces, fragments, CAMERA, 1500, seed)
    assert result.covered > 0
    assert result.mismatches == 0
    for source in faces:
        pieces = tuple(f for f in fragments if f.source == source.source)
        assert sum(area(f.vertices) for f in pieces) == pytest.approx(
            area(source.vertices), rel=1e-8
        )
        # All original boundary lengths are preserved exactly once; new cuts carry no ink.
        boundary = sum(
            (f.vertices[(i + 1) % len(f.vertices)] - p).length
            for f in pieces
            for i, p in enumerate(f.vertices)
            if f.boundary[i]
        )
        perimeter = sum(
            (source.vertices[(i + 1) % len(source.vertices)] - p).length
            for i, p in enumerate(source.vertices)
        )
        assert boundary == pytest.approx(perimeter, rel=1e-8)
        for piece in pieces:
            for i, a in enumerate(piece.vertices):
                if not piece.boundary[i]:
                    continue
                b = piece.vertices[(i + 1) % len(piece.vertices)]

                # Every drawn edge must lie on a real source boundary segment.
                def on_source_segment(start: Point3D, end: Point3D) -> bool:
                    direction = end - start
                    for point in (a, b):
                        offset = point - start
                        if offset.cross(direction).length > 1e-6:
                            return False
                        if not -1e-6 <= offset.dot(direction) <= direction.dot(direction) + 1e-6:
                            return False
                    return True

                assert any(
                    on_source_segment(start, source.vertices[(j + 1) % len(source.vertices)])
                    for j, start in enumerate(source.vertices)
                )


@pytest.mark.parametrize("faces", [crossing(), max_trap()])
def test_reference_scenes(faces: tuple[Face, ...]) -> None:
    _, _, fragments = project(faces, CAMERA)
    assert check(faces, fragments, CAMERA, 4000).mismatches == 0


def test_crossing_requires_split() -> None:
    faces = crossing()
    _, metrics, _ = project(faces, CAMERA)
    assert metrics.splits == 1


def test_coplanar_later_source_wins() -> None:
    face = crossing()[0]
    faces = (face, replace(face, source=1, color=Color(0, 1, 0)))
    _, _, fragments = project(faces, CAMERA)
    assert tuple(f.source for f in fragments) == (0, 1)
    assert check(faces, fragments, CAMERA, 500).mismatches == 0


def test_cut_through_existing_vertex_has_no_duplicate_or_fake_edges() -> None:
    face = Face(
        (Point3D(-1, 0, 0), Point3D(0, -1, 0), Point3D(1, 0, 0), Point3D(0, 1, 0)),
        Color(1, 0, 0),
        0,
    )
    a, b = split(face, distances(face, Point3D(0, 0, 0), Vector3D(1, 0, 0)), 1e-8)
    assert len(a.vertices) == len(b.vertices) == 3
    assert area(a.vertices) + area(b.vertices) == pytest.approx(area(face.vertices))
    assert sum(a.boundary) == sum(b.boundary) == 2


def test_near_plane_and_budget_fail_explicitly() -> None:
    bad = Face(tuple(world(x, y, 0.01) for x, y in ((0, 0), (1, 0), (0, 1))), Color(1, 0, 0), 0)
    with pytest.raises(ValueError, match="near plane"):
        project((bad,), CAMERA)
    with pytest.raises(ValueError, match="budget"):
        project(crossing(), CAMERA, fragment_limit=2)


def test_disjoint_occlusion_cycle() -> None:
    from playground.visibility.scenes import cycle

    faces = cycle()
    _, metrics, fragments = project(faces, CAMERA)
    assert metrics.splits > 0
    assert check(faces, fragments, CAMERA, 4000).mismatches == 0
    # No permutation of whole faces can reproduce visibility in this scene.
    from itertools import permutations

    assert all(check(faces, order, CAMERA, 500).mismatches > 0 for order in permutations(faces))
