"""A closed washer with an open bore and smooth vector boundaries."""

from pdl import Canvas, Color
from pdl.author.transform import Translation
from pdl.extensions.spatial import AnnularCylinder, OrthographicCamera, Scene3D

# tutorial-start
washer = AnnularCylinder(outer_radius=18, inner_radius=10, height=7, color=Color(0.65, 0.77, 0.84))
camera = OrthographicCamera(25, 35)
washer_2d = Scene3D((washer,), camera, sort_faces=False).project()
canvas = Canvas(70, 55)
canvas.draw(washer_2d.copy().apply_transform(Translation(35, 25)))
# tutorial-end

if __name__ == "__main__":
    from examples._shared import export

    export(canvas, __file__, tikz_mode="pdf")
