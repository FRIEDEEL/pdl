"""Core two-dimensional authoring API, independent of canvas and extensions."""

from pdl.author.composition import Drawing as Drawing
from pdl.author.composition import Group as Group
from pdl.author.composition import bounds as bounds
from pdl.author.entity import Entity as Entity
from pdl.author.frames import Frame as Frame
from pdl.author.frames import ReferencePoint as ReferencePoint
from pdl.author.gather import Gather as Gather
from pdl.author.image import Image as Image
from pdl.author.layers import Layer as Layer
from pdl.author.shapes import Arc as Arc
from pdl.author.shapes import Circle as Circle
from pdl.author.shapes import Line as Line
from pdl.author.shapes import Path as Path
from pdl.author.shapes import Polygon as Polygon
from pdl.author.shapes import Polyline as Polyline
from pdl.author.shapes import Rectangle as Rectangle
from pdl.author.style import Color as Color
from pdl.author.style import ColorStop as ColorStop
from pdl.author.style import LinearGradient as LinearGradient
from pdl.author.style import RadialGradient as RadialGradient
from pdl.author.style import Style as Style
from pdl.author.tex import TeX as TeX
from pdl.author.text import Text as Text
