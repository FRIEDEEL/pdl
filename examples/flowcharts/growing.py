"""Grow a branching flowchart, then customize its feedback route."""

from pathlib import Path

from pdl import Canvas, Color, Style
from pdl.extensions.diagram import Decision, FlowNode, Terminal

start = Terminal("Start")
process = start.right(FlowNode("Process"))
check = process.right(Decision("Valid?"))
done = check.right(Terminal("Done"), gap=20, label="Yes")
retry = check.below(FlowNode("Revise"), gap=15, label="No")
retry.connect(process, start="west", end="south", label="Retry")
# A second branch joins the existing end node without repositioning it.
manual = check.above(FlowNode("Review"), gap=15, label="Check")
manual.connect(done, start="east", end="north")
check.style = Style(fill=Color(1, 0.93, 0.73), line_width=0.4)
process.style = Style(fill=Color(0.83, 0.92, 1), line_width=0.4)

canvas = Canvas(170, 110, mode="fit", padding=6)
canvas.draw(start)
output = Path(__file__).resolve().parents[1] / "output" / "flowcharts"
output.mkdir(parents=True, exist_ok=True)
canvas.save(output / "growing.svg")
canvas.save(output / "growing.tex", backend="tikz", tikz_mode="pdf")
