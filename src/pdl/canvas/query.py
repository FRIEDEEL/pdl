"""Immediate numerical queries under a Canvas typography and viewport policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pdl.author.entity.base import Entity
from pdl.author.entity.capture import Composite
from pdl.author.geometry.bounds import Bounds
from pdl.author.geometry.frame import WORLD, Frame, SpacePoint, SpaceVector
from pdl.author.geometry.point import Point, Position, Vector, as_point

if TYPE_CHECKING:
    from pdl.canvas.canvas import Canvas


class Query:
    def __init__(self, canvas: Canvas) -> None:
        self.canvas = canvas

    def point(self, value: Position | SpacePoint, *, in_space: Frame | None = None) -> Point:
        if isinstance(value, SpacePoint):
            world = self.canvas.frame_mapping(value.space).map(value.position)
        else:
            world = as_point(value)
        if in_space is WORLD:
            return world
        if in_space is not None:
            return self.canvas.frame_mapping(in_space).inverse().map(world)
        return self.canvas.output_transform.map(world)

    def vector(self, value: Vector | SpaceVector, *, in_space: Frame | None = None) -> Vector:
        world = (
            self.canvas.frame_mapping(value.space).apply_vector(value.vector)
            if isinstance(value, SpaceVector)
            else value
        )
        if in_space is WORLD:
            return world
        if in_space is not None:
            return self.canvas.frame_mapping(in_space).inverse().apply_vector(world)
        return self.canvas.output_transform.apply_vector(world)

    def bounds(self, value: Entity | Composite, *, in_space: Frame | None = None) -> Bounds:
        captured = self.canvas.snapshot(value)
        if in_space is WORLD:
            return captured.bounds
        transform = (
            self.canvas.frame_mapping(in_space).inverse()
            if in_space is not None
            else self.canvas.viewport(self.canvas.drawings or (captured,)).output_transform
        )
        return captured.apply_transform(transform).bounds

    def ink_bounds(self, value: Entity | Composite, *, in_space: Frame | None = None) -> Bounds:
        captured = self.canvas.snapshot(value)
        if in_space is WORLD:
            return captured.ink_bounds
        transform = (
            self.canvas.frame_mapping(in_space).inverse()
            if in_space is not None
            else self.canvas.viewport(self.canvas.drawings or (captured,)).output_transform
        )
        return captured.apply_transform(transform).ink_bounds

    def from_canvas(self, value: Position, *, in_space: Frame = WORLD) -> Point:
        world = self.canvas.output_transform.inverse().map(value)
        return (
            world if in_space is WORLD else self.canvas.frame_mapping(in_space).inverse().map(world)
        )
