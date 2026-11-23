import QtQuick

Canvas {
    id: art
    property string kind: "dice"
    onKindChanged: requestPaint()
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()

    function path(ctx, points) {
        ctx.beginPath()
        ctx.moveTo(points[0][0], points[0][1])
        for (let index = 1; index < points.length; index++)
            ctx.lineTo(points[index][0], points[index][1])
        ctx.closePath()
    }

    function oval(ctx, x, y, w, h, fill, stroke) {
        ctx.beginPath()
        ctx.ellipse(x, y, w, h)
        if (fill) {
            ctx.fillStyle = fill
            ctx.fill()
        }
        if (stroke) {
            ctx.strokeStyle = stroke
            ctx.stroke()
        }
    }

    function line(ctx, points, color, thickness) {
        ctx.beginPath()
        ctx.moveTo(points[0][0], points[0][1])
        for (let index = 1; index < points.length; index++)
            ctx.lineTo(points[index][0], points[index][1])
        ctx.strokeStyle = color
        ctx.lineWidth = thickness
        ctx.stroke()
    }

    function dice(ctx, scale, x, y) {
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(scale, scale)
        ctx.rotate(-0.075)
        ctx.lineWidth = 1.65

        // All three faces meet at the same front corner.
        const backTop = [23, 3]
        const leftTop = [3, 13]
        const frontTop = [23, 24]
        const rightTop = [43, 13]
        const leftBottom = [3, 34]
        const frontBottom = [23, 45]
        const rightBottom = [43, 34]

        path(ctx, [backTop, leftTop, frontTop, rightTop])
        ctx.fillStyle = "#fffbf3"
        ctx.fill()
        path(ctx, [leftTop, leftBottom, frontBottom, frontTop])
        ctx.fillStyle = "#f2e4db"
        ctx.fill()
        path(ctx, [frontTop, frontBottom, rightBottom, rightTop])
        ctx.fillStyle = "#fbefe3"
        ctx.fill()

        path(ctx, [backTop, rightTop, rightBottom, frontBottom, leftBottom, leftTop])
        ctx.strokeStyle = "#3d1835"
        ctx.stroke()
        line(ctx, [leftTop, frontTop, rightTop], "#3d1835", 1.45)
        line(ctx, [frontTop, frontBottom], "#3d1835", 1.45)

        // The top, left and right faces show one, two and three pips respectively.
        oval(ctx, 20.6, 11.7, 4.8, 3.8, "#4e2445")
        oval(ctx, 7.2, 20.6, 4.0, 4.7, "#4e2445")
        oval(ctx, 14.7, 32.9, 4.0, 4.7, "#4e2445")
        oval(ctx, 34.9, 20.7, 4.0, 4.7, "#4e2445")
        oval(ctx, 31.0, 26.8, 4.0, 4.7, "#4e2445")
        oval(ctx, 27.1, 32.8, 4.0, 4.7, "#4e2445")

        line(ctx, [[44, 5], [48, -1]], "#f49378", 2.2)
        line(ctx, [[49, 11], [55, 8]], "#f49378", 2.2)
        ctx.restore()
    }

    function water(ctx) {
        ctx.translate((width - 96) / 2, (height - 90) / 2)
        oval(ctx, 1, 66, 92, 18, "#dce5ba")
        ctx.beginPath()
        ctx.moveTo(19, 20)
        ctx.lineTo(24, 68)
        ctx.quadraticCurveTo(46, 82, 68, 68)
        ctx.lineTo(73, 20)
        ctx.closePath()
        const glass = ctx.createLinearGradient(19, 0, 74, 0)
        glass.addColorStop(0, "#cce6f2")
        glass.addColorStop(0.5, "#f5fbfc")
        glass.addColorStop(1, "#bbddf2")
        ctx.fillStyle = glass
        ctx.fill()
        ctx.strokeStyle = "#50749c"
        ctx.lineWidth = 2.2
        ctx.stroke()

        ctx.beginPath()
        ctx.moveTo(23, 37)
        ctx.quadraticCurveTo(44, 47, 70, 37)
        ctx.lineTo(65, 66)
        ctx.quadraticCurveTo(49, 76, 28, 67)
        ctx.closePath()
        ctx.fillStyle = "#8ec3e7"
        ctx.fill()
        oval(ctx, 23, 33, 47, 9, "#aad7ed")
        oval(ctx, 18, 10, 56, 18, "#eff7fa", "#50749c")
        line(ctx, [[29, 44], [31, 55]], "#f8fcff", 3.3)
        oval(ctx, 30, 59, 4, 4, "#f8fcff")
        line(ctx, [[79, 13], [84, 6]], "#f49378", 2.6)
        line(ctx, [[82, 22], [90, 19]], "#f49378", 2.6)
    }

    onPaint: {
        const ctx = getContext("2d")
        ctx.reset()
        ctx.lineJoin = "round"
        ctx.lineCap = "round"

        switch (kind) {
        case "dice": {
            const scale = width > 70 ? 1.55 : 0.83
            dice(ctx, scale, width > 70 ? 25 : 6, width > 70 ? 15 : 5)
            break
        }
        case "water":
            water(ctx)
            break
        case "underline":
            ctx.beginPath()
            ctx.moveTo(3, 6)
            ctx.bezierCurveTo(42, 1, 93, 1, width - 4, 5)
            ctx.strokeStyle = "#aaba7c"
            ctx.lineWidth = 3.5
            ctx.stroke()
            break
        case "seam":
            ctx.beginPath()
            ctx.moveTo(0, 1)
            for (let x = 0; x < width; x += 14)
                ctx.quadraticCurveTo(x + 7, 9, x + 14, 1)
            ctx.strokeStyle = "#ead7c6"
            ctx.lineWidth = 1.5
            ctx.stroke()
            break
        case "tape":
            path(ctx, [[2, 2], [width - 2, 2], [width - 6, 8], [width - 2, 14],
                       [width - 6, 21], [width - 2, height - 2], [2, height - 2], [6, 21], [2, 14], [6, 8]])
            ctx.fillStyle = "#f9dfca"
            ctx.fill()
            ctx.strokeStyle = "#efc5aa"
            ctx.stroke()
            ctx.save()
            ctx.clip()
            for (let x = 12; x < width; x += 12)
                line(ctx, [[x, 2], [x, height - 2]], "#f2cdb7", 0.55)
            for (let y = 8; y < height; y += 7)
                line(ctx, [[0, y], [width, y]], "#f2cdb7", 0.55)
            ctx.restore()
            break
        case "heading":
            path(ctx, [[25, 4], [width - 28, 3], [width - 24, 8], [width - 29, 14],
                       [width - 23, 22], [width - 28, 29], [width - 24, 34], [24, 36],
                       [27, 29], [22, 23], [27, 15], [22, 9]])
            ctx.fillStyle = "#eed8f1"
            ctx.fill()
            line(ctx, [[3, 15], [13, 20]], "#aaba7c", 2)
            line(ctx, [[10, 8], [16, 15]], "#aaba7c", 2)
            line(ctx, [[width - 3, 15], [width - 13, 20]], "#aaba7c", 2)
            line(ctx, [[width - 10, 8], [width - 16, 15]], "#aaba7c", 2)
            break
        }
    }
}
