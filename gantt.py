def draw_gantt(canvas, timeline):
    canvas.delete("all")
    if not timeline:
        return

    comp = []
    for seg in timeline:
        if not comp:
            comp.append(seg)
            continue
        s, e, p = seg
        ps = comp[-1]
        if ps[2] == p and ps[1] == s:
            comp[-1] = (ps[0], e, p)
        else:
            comp.append(seg)

    timeline = comp

    st = min(s for s, _, _ in timeline)
    et = max(e for _, e, _ in timeline)
    total = max(1, et - st)

    W = max(760, canvas.winfo_width() - 20)
    x0 = 20
    y0 = 40
    bh = 50

    canvas.create_line(x0, y0 + bh + 10, x0 + W, y0 + bh + 10)

    colors = {}
    pal = [
        "#7fc97f", "#beaed4", "#fdc086", "#ffff99", "#386cb0",
        "#f0027f", "#bf5b17", "#666666", "#1b9e77", "#d95f02",
        "#7570b3", "#e7298a", "#66a61e", "#e6ab02", "#a6761d",
    ]
    ci = 0

    for s, e, p in timeline:
        if p not in colors and p != "IDLE":
            colors[p] = pal[ci % len(pal)]
            ci += 1

        fs = (s - st) / total
        fe = (e - st) / total
        X1 = int(x0 + fs * W)
        X2 = int(x0 + fe * W)

        if p == "IDLE":
            canvas.create_rectangle(X1, y0, X2, y0 + bh, outline="#999", dash=(3, 2))
            canvas.create_text((X1 + X2) // 2, y0 + bh // 2, text="IDLE", fill="#666")
        else:
            canvas.create_rectangle(X1, y0, X2, y0 + bh, fill=colors[p], outline="black")
            canvas.create_text((X1 + X2) // 2, y0 + bh // 2, text=p)

        canvas.create_text(X1, y0 + bh + 20, text=str(s), anchor="n")

    canvas.create_text(int(x0 + W), y0 + bh + 20, text=str(et), anchor="ne")
