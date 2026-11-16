"""Draws the FirstFlight as-is and to-be process maps.

One definition of each map (lanes, steps, arrows) is written out twice:
  process_maps/<name>.png     - picture for the README and slides
  process_maps/<name>.drawio  - editable file, open at https://app.diagrams.net
Run:  python scripts/make_process_maps.py
"""
from pathlib import Path
from xml.sax.saxutils import escape
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle

OUT = Path(__file__).resolve().parents[1] / "process_maps"
LANE_LABEL_W = 120
COL0, COLSTEP = 235, 205          # x of column 0 centre, distance between columns
BOX_W, BOX_H = 170, 74

STYLE = {  # type: (fill, border)
    "start":    ("#DCEBFA", "#1F5FA8"),
    "step":     ("#FFFFFF", "#33475B"),
    "decision": ("#FFF4D6", "#B7791F"),
    "pain":     ("#FDE4E1", "#B42318"),
    "ai":       ("#E3F4EA", "#1E7B4A"),
    "end":      ("#DCEBFA", "#1F5FA8"),
}

def X(col): return COL0 + col * COLSTEP

AS_IS = {
    "title": "As-is: how a first-time flyer gets an answer today (no assistant)",
    "note": "Baseline, 4 weeks before the pilot (simulated data): 2,428 contacts a week, about 6 minutes of agent time each.",
    "lanes": [("Passenger", 150), ("Website / app", 150), ("Contact centre", 150), ("Airport", 150)],
    "nodes": {
        "book":   (0, 0, "start", "Books a ticket"),
        "ask":    (0, 1, "step", "Has a question\n(bags, check-in time, ID)"),
        "faq":    (1, 2, "step", "Searches the FAQ pages"),
        "found":  (1, 3, "decision", "Finds a clear\nanswer?"),
        "call":   (2, 4, "pain", "Calls or emails the\ncontact centre and waits"),
        "agent":  (2, 5, "step", "Agent answers\n(about 6 min each)"),
        "checkin":(0, 6, "step", "Does web check-in"),
        "airport":(3, 7, "step", "Reaches the airport\ncounter"),
        "ok":     (3, 8, "decision", "Bag within limit\nand on time?"),
        "fee":    (3, 9, "pain", "Pays an airport fee or\nmisses counter closing"),
        "board":  (0, 9, "end", "Boards the flight"),
    },
    "edges": [
        ("book", "r", "ask", "l", "", []),
        ("ask", "b", "faq", "l", "", [("x:ask", "y:faq")]),
        ("faq", "r", "found", "l", "", []),
        ("found", "t", "checkin", "l", "Yes", [("x:found", "y:checkin")]),
        ("found", "b", "call", "l", "No", [("x:found", "y:call")]),
        ("call", "r", "agent", "l", "", []),
        ("agent", "r", "checkin", "b", "", [("x:checkin", "y:agent")]),
        ("checkin", "r", "airport", "t", "", [("x:airport", "y:checkin")]),
        ("airport", "r", "ok", "l", "", []),
        ("ok", "t", "board", "l", "Yes", [("x:ok", "y:board")]),
        ("ok", "r", "fee", "l", "No", []),
        ("fee", "t", "board", "b", "", []),
    ],
}

TO_BE = {
    "title": "To-be: FirstFlight assistant with human hand-off",
    "note": "Simulated 8-week pilot: 63.0% of chats resolved by the assistant, 30.3% handed to an agent, 6.7% abandoned.",
    "lanes": [("Passenger", 150), ("FirstFlight\nassistant", 270), ("Human agent", 150), ("QA reviewer /\nanalyst", 150)],
    "nodes": {
        "ask":     (0, 0, "start", "Asks in English, Hindi\nor Arabic (web, app,\nWhatsApp)"),
        "pd":      ((1, 0), 1, "decision", "Personal data\ninvolved?"),
        "refuse":  ((1, 1), 1, "ai", "Does not take it and\nexplains why (P11.1)"),
        "booking": ((1, 0), 2, "decision", "Booking-specific or\nlive flight status?"),
        "inbook":  ((1, 0), 3, "decision", "Answer is in the\npolicy handbook?"),
        "answer":  ((1, 0), 4, "ai", "Answers in the\npassenger's language\nfrom the handbook"),
        "notcov":  ((1, 1), 3, "ai", "Says it is not covered\nand offers an agent\n(P11.3)"),
        "handoff": (2, 3, "step", "Hand-off form goes to an\nExcel log and an agent\nemail (Power Automate)"),
        "reply":   (2, 4, "step", "Agent replies to\nthe passenger"),
        "rate":    (0, 6, "end", "Gets the answer and\nrates the chat (1 to 5)"),
        "qa":      (3, 7, "step", "Reviews a 6% sample\nof AI answers each week"),
        "improve": (3, 8, "step", "Fixes prompts and updates\nthe KPI dashboard"),
    },
    "edges": [
        ("ask", "r", "pd", "t", "", [("x:pd", "y:ask")]),
        ("pd", "b", "refuse", "t", "Yes", []),
        ("pd", "r", "booking", "l", "No", []),
        ("refuse", "r", "booking", "l", "", [("x:pd+102", "y:refuse"), ("x:pd+102", "y:pd")]),
        ("booking", "r", "inbook", "l", "No", []),
        ("inbook", "r", "answer", "l", "Yes", []),
        ("inbook", "b", "notcov", "t", "No", []),
        ("notcov", "b", "handoff", "t", "", []),
        ("booking", "b", "handoff", "l", "Yes", [("x:booking", "y:handoff")]),
        ("handoff", "r", "reply", "l", "", []),
        ("answer", "r", "rate", "b", "", [("x:rate", "y:answer")]),
        ("reply", "r", "rate", "b", "", [("x:rate", "y:reply")]),
        ("rate", "r", "qa", "t", "", [("x:qa", "y:rate")]),
        ("qa", "r", "improve", "l", "", []),
    ],
}


def layout(spec):
    """Returns lane boxes and node centres in pixel coordinates (y grows downwards)."""
    top = 70
    lanes, y = [], top
    for name, h in spec["lanes"]:
        lanes.append((name, y, h)); y += h
    nodes = {}
    for nid, (lane, col, kind, text) in spec["nodes"].items():
        if isinstance(lane, tuple):
            li, row = lane
            _, ly, lh = lanes[li]
            cy = ly + lh * (0.27 if row == 0 else 0.76)
        else:
            _, ly, lh = lanes[lane]
            cy = ly + lh / 2
        nodes[nid] = (X(col), cy, kind, text)
    maxcol = max(c for (_, c, _, _) in spec["nodes"].values())
    width = X(maxcol) + BOX_W / 2 + 190
    return lanes, nodes, width, y + 46


def side_point(node, side):
    x, y, kind, _ = node
    hw, hh = BOX_W / 2, BOX_H / 2
    return {"l": (x - hw, y), "r": (x + hw, y), "t": (x, y - hh), "b": (x, y + hh)}[side]


def resolve(points, nodes):
    out = []
    for px, py in points:
        def val(tok, idx):
            ref = tok.split(":")[1]
            off = 0
            for sign in ("+", "-"):
                if sign in ref:
                    ref, num = ref.split(sign); off = float(sign + num)
            return nodes[ref][idx] + off
        out.append((val(px, 0), val(py, 1)))
    return out


def draw_png(spec, path):
    lanes, nodes, W, H = layout(spec)
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")
    ax.text(20, 30, spec["title"], fontsize=13, fontweight="bold", va="center", color="#102A43")
    for i, (name, y, h) in enumerate(lanes):
        ax.add_patch(Rectangle((20, y), W - 40, h, facecolor="#F7F9FB" if i % 2 == 0 else "#FFFFFF", edgecolor="#9AA5B1", lw=0.8))
        ax.add_patch(Rectangle((20, y), LANE_LABEL_W, h, facecolor="#E4E9EF", edgecolor="#9AA5B1", lw=0.8))
        ax.text(20 + LANE_LABEL_W / 2, y + h / 2, name, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#102A43")
    for src, s_side, dst, d_side, label, way in spec["edges"]:
        pts = [side_point(nodes[src], s_side)] + resolve(way, nodes) + [side_point(nodes[dst], d_side)]
        xs, ys = zip(*pts)
        ax.plot(xs[:-1], ys[:-1], color="#33475B", lw=1.1, solid_joinstyle="round", zorder=2)
        ax.annotate("", xy=pts[-1], xytext=pts[-2], arrowprops=dict(arrowstyle="-|>", color="#33475B", lw=1.1, shrinkA=0, shrinkB=0), zorder=2)
        if label:
            (x0, y0), (x1, y1) = pts[0], pts[1]
            dx = 0 if x0 != x1 else 14
            dy = -9 if y0 == y1 else (18 if y1 > y0 else -18)
            lx = x0 + (16 if x1 > x0 else -16 if x1 < x0 else 0) + dx
            ax.text(lx, y0 + (dy if x0 == x1 else -9), label, fontsize=7.5, color="#B7791F", fontweight="bold", ha="center", va="center", zorder=4)
    for nid, (x, y, kind, text) in nodes.items():
        fill, edge = STYLE[kind]
        if kind == "decision":
            ax.add_patch(Polygon([(x, y - BOX_H / 2 - 6), (x + BOX_W / 2, y), (x, y + BOX_H / 2 + 6), (x - BOX_W / 2, y)], closed=True, facecolor=fill, edgecolor=edge, lw=1.3, zorder=3))
        else:
            rounding = 30 if kind in ("start", "end") else 8
            ax.add_patch(FancyBboxPatch((x - BOX_W / 2, y - BOX_H / 2), BOX_W, BOX_H, boxstyle=f"round,pad=0,rounding_size={rounding}", facecolor=fill, edgecolor=edge, lw=1.3, zorder=3))
        ax.text(x, y, text, ha="center", va="center", fontsize=7.4 if kind == "decision" else 7.8, color="#102A43", zorder=4, linespacing=1.25)
    ax.text(20, H - 22, spec["note"], fontsize=8.2, color="#52606D", va="center")
    lx = W - 560
    for label, kind in (("Step", "step"), ("Decision", "decision"), ("Pain point", "pain"), ("Done by AI", "ai")):
        fill, edge = STYLE[kind]
        ax.add_patch(Rectangle((lx, 22), 16, 14, facecolor=fill, edgecolor=edge, lw=1))
        ax.text(lx + 22, 29, label, fontsize=8, va="center", color="#102A43"); lx += 130
    fig.savefig(path, dpi=150); plt.close(fig)


def draw_drawio(spec, path):
    lanes, nodes, W, H = layout(spec)
    cells, n = [], [1]
    def nid():
        n[0] += 1; return f"c{n[0]}"
    cells.append(f'<mxCell id="title" value="{escape(spec["title"])}" style="text;html=1;align=left;fontStyle=1;fontSize=16;" vertex="1" parent="1"><mxGeometry x="20" y="10" width="{W-40:.0f}" height="40" as="geometry"/></mxCell>')
    for name, y, h in lanes:
        cells.append(f'<mxCell id="{nid()}" value="{escape(name).replace(chr(10), "&lt;br&gt;")}" style="swimlane;horizontal=0;startSize={LANE_LABEL_W};html=1;fillColor=#E4E9EF;strokeColor=#9AA5B1;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="20" y="{y:.0f}" width="{W-40:.0f}" height="{h:.0f}" as="geometry"/></mxCell>')
    ids = {}
    for key, (x, y, kind, text) in nodes.items():
        fill, edge = STYLE[kind]
        shape = "rhombus;" if kind == "decision" else ("rounded=1;arcSize=50;" if kind in ("start", "end") else "rounded=1;arcSize=12;")
        hh = BOX_H + 12 if kind == "decision" else BOX_H
        ids[key] = nid()
        val = escape(text).replace("\n", "&lt;br&gt;")
        cells.append(f'<mxCell id="{ids[key]}" value="{val}" style="{shape}whiteSpace=wrap;html=1;fillColor={fill};strokeColor={edge};fontSize=11;" vertex="1" parent="1"><mxGeometry x="{x-BOX_W/2:.0f}" y="{y-hh/2:.0f}" width="{BOX_W}" height="{hh}" as="geometry"/></mxCell>')
    anchor = {"l": (0, 0.5), "r": (1, 0.5), "t": (0.5, 0), "b": (0.5, 1)}
    for src, s_side, dst, d_side, label, way in spec["edges"]:
        (ex, ey), (nx, ny) = anchor[s_side], anchor[d_side]
        pts = "".join(f'<mxPoint x="{px:.0f}" y="{py:.0f}"/>' for px, py in resolve(way, nodes))
        arr = f'<Array as="points">{pts}</Array>' if pts else ""
        cells.append(f'<mxCell id="{nid()}" value="{escape(label)}" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;exitX={ex};exitY={ey};entryX={nx};entryY={ny};fontColor=#B7791F;fontStyle=1;" edge="1" parent="1" source="{ids[src]}" target="{ids[dst]}"><mxGeometry relative="1" as="geometry">{arr}</mxGeometry></mxCell>')
    cells.append(f'<mxCell id="note" value="{escape(spec["note"])}" style="text;html=1;align=left;fontColor=#52606D;" vertex="1" parent="1"><mxGeometry x="20" y="{H-40:.0f}" width="{W-40:.0f}" height="30" as="geometry"/></mxCell>')
    xml = ('<mxfile host="app.diagrams.net"><diagram name="Page-1" id="p1">'
           f'<mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" page="1" pageWidth="{W:.0f}" pageHeight="{H:.0f}"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
           + "".join(cells) + "</root></mxGraphModel></diagram></mxfile>")
    path.write_text(xml, encoding="utf-8")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, spec in (("as_is_process_map", AS_IS), ("to_be_process_map", TO_BE)):
        draw_png(spec, OUT / f"{name}.png")
        draw_drawio(spec, OUT / f"{name}.drawio")
        print("wrote", name)
