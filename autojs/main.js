let Tile = function (heightType, buildableType) {
    this.heightType = heightType;
    this.buildableType = buildableType;
}

let Vector3 = function (x, y, z) {
    this.x = x;
    this.y = y;
    this.z = z;
}

let Vector2 = function (x, y) {
    this.x = x;
    this.y = y;
}

let Level = function (stageId, code, levelId, name, height, width, tiles, view) {
    this.stageId = stageId;
    this.code = code;
    this.levelId = levelId;
    this.name = name;
    this.height = height || 0;
    this.width = width || 0;
    this.tiles = tiles || null;
    this.view = view || null;


    this.from_json = function (json_data) {
        let raw_tiles = json_data['tiles'];
        let tiles = [];
        for (let row of raw_tiles) {
            let row_tiles = [];
            for (let tile of row) {
                row_tiles.push(new Tile(tile['heightType'], tile['buildableType']));
            }
            tiles.push(row_tiles);
        }
        for (let i in json_data) {
            if (this.hasOwnProperty(i)) {
                this[i] = json_data[i]
            }
        }
        return this
        /* return new Level(
            json_data['stageId'],
            json_data['code'],
            json_data['levelId'],
            json_data['name'],
            json_data['height'],
            json_data['width'],
            tiles,
            json_data['view']
            )
        */
    }


    this.get_tile = function (row, col) {
        /*
        if (0 <= row <= this.height && 0 <= col <= this.width) {
            return this.tiles[row][col];
        }
        */
        if (0 <= row && row <= this.height && 0 <= col && col <= this.width) {
            return this.tiles[row][col];
        }
        return null;
    }
}


let Calc = function (screen_width, screen_height, level) {
    this.screen_width = screen_width;
    this.screen_height = screen_height;
    this.ratio = screen_height / screen_width;

    this.matrix_p = [
        [this.ratio / Math.tan(Math.PI * 20 / 180), 0, 0, 0],
        [0, 1 / Math.tan(Math.PI * 20 / 180), 0, 0],
        [0, 0, -(1000 + 0.3) / (1000 - 0.3), -(1000 * 0.3 * 2) / (1000 - 0.3)],
        [0, 0, -1, 0],
    ];
    this.matrix_x = [
        [1, 0, 0, 0],
        [0, Math.cos(Math.PI * 30 / 180), -Math.sin(Math.PI * 30 / 180), 0],
        [0, -Math.sin(Math.PI * 30 / 180), -Math.cos(Math.PI * 30 / 180), 0],
        [0, 0, 0, 1],
    ];
    this.matrix_y = [
        [Math.cos(Math.PI * 10 / 180), 0, Math.sin(Math.PI * 10 / 180), 0],
        [0, 1, 0, 0],
        [-Math.sin(Math.PI * 10 / 180), 0, Math.cos(Math.PI * 10 / 180), 0],
        [0, 0, 0, 1],
    ];

    if (level) {
        this.level = level;
        this.view = new Vector3(level.view[0][0], level.view[0][1], level.view[0][2]);
        this.view_side = new Vector3(level.view[1][0], level.view[1][1], level.view[1][2]);
    }
    this.set_level = function (level) {
        this.level = level;
        this.view = new Vector3(level.view[0][0], level.view[0][1], level.view[0][2]);
        this.view_side = new Vector3(level.view[1][0], level.view[1][1], level.view[1][2]);
    }
    this.adapter = function () {
        let fromRatio = 9 / 16;
        let toRatio = 3 / 4;
        if (this.ratio < fromRatio - 0.00001) {
            return [0, 0];
        }
        let t = (this.ratio - fromRatio) / (toRatio - fromRatio);
        return [-1.4 * t, -2.8 * t];
    }
    this.multiply_matrices = function (arr1, arr2) {
        if (arr1[0].length !== arr2.length) {
            throw new Error("矩阵维度不匹配");
        }

        let result = new Array(arr1.length).fill(0).map(() => new Array(arr2[0].length).fill(0));

        for (let i = 0; i < arr1.length; i++) {
            for (let j = 0; j < arr2[0].length; j++) {
                for (let k = 0; k < arr1[0].length; k++) {
                    result[i][j] += arr1[i][k] * arr2[k][j];
                }
            }
        }

        return result;
    }

    this.get_focus_offset = function (tile_x, tile_y) {
        const x = tile_x - (this.level.width - 1) / 2;
        const y = (this.level.height - 1) / 2 - tile_y;
        return new Vector3(x, y, 0);
    }

    this.get_character_world_pos = function (tile_x, tile_y) {
        const x = tile_x - (this.level.width - 1) / 2;
        const y = (this.level.height - 1) / 2 - tile_y;
        const tile = this.level.get_tile(tile_y, tile_x);
        if (!tile) throw new Error("Tile is null");
        const z = tile.heightType * -0.4;
        return new Vector3(x, y, z);
    }

    this.get_with_draw_world_pos = function (tile_x, tile_y) {
        const ret = this.get_character_world_pos(tile_x, tile_y);
        ret.x -= 1.3143386840820312;
        ret.y += 1.314337134361267;
        ret.z = -0.3967874050140381;
        return ret;
    }

    this.get_skill_world_pos = function (tile_x, tile_y) {
        const ret = this.get_character_world_pos(tile_x, tile_y);
        ret.x += 1.3143386840820312;
        ret.y -= 1.314337134361267;
        ret.z = -0.3967874050140381;
        return ret;
    }

    this.get_character_screen_pos = function (tile_x, tile_y, side, focus) {
        tile_x = tile_x || this.level.width - 1;
        tile_y = tile_y || this.level.height - 1;

        if (focus) {
            side = true;
        }
        const world_pos = this.get_character_world_pos(tile_x, tile_y);
        const offset = focus ? this.get_focus_offset(tile_x, tile_y) : new Vector3(0.0, 0.0, 0.0);
        return this.world_to_screen_pos(world_pos, side, offset);
    }

    this.get_withdraw_screen_pos = function (tile_x, tile_y) {
        tile_x = tile_x || this.level.width - 1;
        tile_y = tile_y || this.level.height - 1;

        const world_pos = this.get_with_draw_world_pos(tile_x, tile_y);
        const offset = this.get_focus_offset(tile_x, tile_y);

        return this.world_to_screen_pos(world_pos, true, offset);
    }

    this.get_skill_screen_pos = function (tile_x, tile_y) {
        tile_x = tile_x || this.level.width - 1;
        tile_y = tile_y || this.level.height - 1;

        const world_pos = this.get_skill_world_pos(tile_x, tile_y);
        const offset = this.get_focus_offset(tile_x, tile_y);
        return this.world_to_screen_pos(world_pos, true, offset);
    }
    this.get_lattice_screen_pos = function (side) {
        let matrix = this.world_to_screen_matrix(side);
        let h = this.level.height;
        let w = this.level.width;

        let result = [];
        for (let y = 0; y < h; y++) {
            let tmp = [];
            for (let x = 0; x < w; x++) {
                let tile = this.level.get_tile(y, x);
                if (!tile) throw new Error("Tile is null");
                let [p_x, p_y, p_z, p_w] = this.multiply_matrices(matrix, [
                    [(x - (w - 1) / 2)],
                    [((h - 1) / 2) - y],
                    [tile.heightType * -0.4],
                    [1]
                ]);
                p_x = (1 + p_x / p_w) / 2;
                p_y = (1 + p_y / p_w) / 2;
                let center = {
                    x: Math.floor(p_x * this.screen_width),
                    y: Math.floor((1 - p_y) * this.screen_height),
                    tileKey: tile.tileKey,
                    line: y,
                    column: x
                };
                //console.info(x, y, center);
                //tmp.push([[x,y], center]);
                tmp.push(center);
                //log(tmp)
            }
            result.push(tmp);
        }

        return result;
    }

    this.world_to_screen_matrix = function (side, offset) {
        if (!offset) {
            offset = new Vector3(0.0, 0.0, 0.0);
        }
        let [adapter_y, adapter_z] = this.adapter();
        if (side) {
            var x = this.view_side.x,
                y = this.view_side.y,
                z = this.view_side.z;
        } else {
            var x = this.view.x,
                y = this.view.y,
                z = this.view.z;
        }
        x += offset.x;
        y += offset.y + adapter_y;
        z += offset.z + adapter_z;
        var raw = [
            [1, 0, 0, -x],
            [0, 1, 0, -y],
            [0, 0, 1, -z],
            [0, 0, 0, 1],
        ];
        let matrix;
        if (side) {
            matrix = this.multiply_matrices(this.matrix_x, this.matrix_y);
            matrix = this.multiply_matrices(matrix, raw);
        } else {
            matrix = this.multiply_matrices(this.matrix_x, raw);
        }
        return this.multiply_matrices(this.matrix_p, matrix);
    }

    this.world_to_screen_pos = function (pos, side, offset) {
        var matrix = this.world_to_screen_matrix(side, offset);
        var [x, y, , w] = this.multiply_matrices(matrix, [
            [pos.x],
            [pos.y],
            [pos.z],
            [1]
        ]);
        x = (1 + x / w) / 2;
        y = (1 + y / w) / 2;
        return new Vector2(x * this.screen_width, (1 - y) * this.screen_height);
    }
}
const level = new Level();

const levelsPath = files.path("../") + "levels.json";
const levelTable = JSON.parse(files.read(levelsPath));

for (let data of levelTable) {
    log(data.name, data.code);
    //if (!data.name || data.code !== "2-10") {
    //    continue;
    //}
    let level_code = data.code;
    if (data.code === "???") {
        level_code = data.name;
    }

    let calc = new Calc(2712, 1220, level.from_json(data));
    //原型是需要传入tile_x/y的，但是我测试了，只要不大于level_width/height，没什么影响
    let points = calc.get_skill_screen_pos()
    console.info("撤退坐标", points);

    points = calc.get_withdraw_screen_pos();
    console.warn("技能坐标", points);

    //是否是放置干员时的视角
    let side_ = true;
    points = calc.get_lattice_screen_pos(side_)
    console.error(JSON.stringify(points))

    if (files.exists("./" + level_code + side_ + ".png")) {
        var superMario = images.read("./" + level_code + side_ + ".png");
        var canvas = new Canvas(superMario);
        var paint = new Paint();

        paint.setStrokeWidth(20)
        paint.setTextAlign(Paint.Align.CENTER);

        paint.setTextSize(35);
        paint.setStyle(Paint.Style.FILL);
        points.forEach(point => {
            point.forEach(point_ => {
                switch (point_.tileKey) {
                    case 'tile_wall':
                        paint.setColor(colors.parseColor("#00ff00"))
                        break;

                    case 'tile_road':
                        paint.setColor(colors.parseColor("#0000ff"))
                        break;
                    default:
                        paint.setColor(colors.parseColor("#000000"));
                        // code
                        break
                }
                canvas.drawPoint(point_.x, point_.y, paint);
                canvas.drawText(
                    point_.line + "，" + point_.column,
                    point_.x,
                    point_.y + Math.abs(paint.getFontMetrics().top - 10),
                    paint
                );
            })
        });
        var image = canvas.toImage();
        images.save(image, "./tmp.png");

        app.viewFile("./tmp.png");

        superMario.recycle();
        image.recycle();
    } else {
        let fileName = files.join(files.path("./"), level_code + ".txt");
        files.write(fileName, JSON.stringify(points));
    }
    break;
}