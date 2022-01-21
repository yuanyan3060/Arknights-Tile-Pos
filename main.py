import numpy as np
import cv2
from typing import List, Optional, Tuple
from dataclasses import dataclass
import json
import pathlib
import math


@dataclass
class Tile:
    heightType: int
    buildableType: int


@dataclass
class Stage:
    stageId: str
    code: str
    levelId: Optional[str]


class MapData:
    tiles: List[List[Tile]]
    height: int = 0
    width: int = 0
    view: int = 0

    def __init__(self, code: str):
        self.tiles = []
        for stage in stage_list:
            if stage.code == code:
                path = gamedata_path / "levels" / f"{stage.levelId}.json"
                with open(path, encoding="UTF-8") as fp:
                    raw_data = json.loads(fp.read())
                    for row in raw_data["mapData"]["map"]:
                        tmp: List[Tile] = []
                        for index in row:
                            tile_data = raw_data["mapData"]["tiles"][index]
                            tile = Tile(heightType=tile_data["heightType"], buildableType=tile_data["buildableType"])
                            tmp.append(tile)
                        self.tiles.append(tmp)
                    self.width = raw_data["mapData"]["width"]
                    self.height = raw_data["mapData"]["height"]
                    self.view = view_table[path.stem]

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_tile(self, row: int, col: int) -> Optional[Tile]:
        if 0 <= row <= self.height and 0 <= col <= self.width:
            return self.tiles[row][col]
        return None


class Calc:
    width: int
    height: int
    ratio: float
    matrix_p: np.array = None

    def __init__(self, width: Optional[int], height: Optional[int]):
        if width is not None and height is not None:
            self.init(width, height)

    def init(self, width: int, height: int):
        self.width = width
        self.height = height
        self.ratio = height / width
        self.matrix_p = np.array([
            [self.ratio / math.tan(math.pi * 20 / 180), 0, 0, 0],
            [0, 1 / math.tan(math.pi * 20 / 180), 0, 0],
            [0, 0, -(1000 + 0.3) / (1000 - 0.3), -(1000 * 0.3 * 2) / (1000 - 0.3)],
            [0, 0, -1, 0],
        ])

    def adapter(self) -> Tuple[float, float]:
        fromRatio = 9 / 16
        toRatio = 3 / 4
        if self.ratio < fromRatio - 0.00001:
            return 0, 0

        t = (self.ratio - fromRatio) / (toRatio - fromRatio)

        return -1.4 * t, -2.8 * t

    def run(self, code: str, side: bool = False) -> List[List[Tuple[Tile, Tuple[int, int]]]]:
        result: List[List[Tuple[Tile, Tuple[int, int]]]] = []
        map_data = MapData(code)
        if map_data.view == 0:
            x, y, z = 0.0, -4.81, - 7.76
            if side:
                x += 0.5975104570388794
                y -= 0.5
                z -= 0.882108688354492
        elif map_data.view == 1:
            x, y, z = 0.0, -5.60, -8.92
            if side:
                x += 0.7989424467086792
                y -= 0.5
                z -= 0.86448486328125
        elif map_data.view == 2:
            x, y, z = 0.0, -5.08, -8.04
            if side:
                x += 0.6461319923400879
                y -= 0.5
                z -= 0.877854309082031
        else:
            x, y, z = 0.0, -6.1, -9.78
            if side:
                x += 0.948279857635498
                y -= 0.5
                z -= 0.85141918182373
        adapter_y, adapter_z = self.adapter()
        y += adapter_y
        z += adapter_z
        raw = np.array([
            [1, 0, 0, -x],
            [0, 1, 0, -y],
            [0, 0, 1, -z],
            [0, 0, 0, 1],
        ])
        matrix_x = np.array([
            [1, 0, 0, 0],
            [0, math.cos(math.pi * 30 / 180), -math.sin(math.pi * 30 / 180), 0],
            [0, -math.sin(math.pi * 30 / 180), -math.cos(math.pi * 30 / 180), 0],
            [0, 0, 0, 1],
        ])
        matrix_y = np.array([
            [math.cos(math.pi * 10 / 180), 0, math.sin(math.pi * 10 / 180), 0],
            [0, 1, 0, 0],
            [-math.sin(math.pi * 10 / 180), 0, math.cos(math.pi * 10 / 180), 0],
            [0, 0, 0, 1],
        ])

        if side:
            matrix = np.dot(matrix_x, matrix_y)
            matrix = np.dot(matrix, raw)
        else:
            matrix = np.dot(matrix_x, raw)
        matrix = np.dot(self.matrix_p, matrix)
        h = map_data.get_height()
        w = map_data.get_width()
        for y in range(h):
            tmp: List[Tuple[Tile, Tuple[int, int]]] = []
            for x in range(w):
                tile = map_data.get_tile(y, x)
                np.array([x, y, z, 1])
                p_x, p_y, p_z, p_w = np.dot(matrix,
                                            np.array([(x - (w - 1) / 2), ((h - 1) / 2) - y, tile.heightType * -0.4, 1]))
                p_x = (1 + p_x / p_w) / 2
                p_y = (1 + p_y / p_w) / 2
                center = int(p_x * self.width), int((1 - p_y) * self.height)
                tmp.append((tile, center))
            result.append(tmp)
        return result


gamedata_path = pathlib.Path(__file__).parent / "gamedata"
data_path = pathlib.Path(__file__).parent / "view.json"
stage_list: List[Stage] = []
with open(gamedata_path / "excel/stage_table.json", encoding="UTF-8") as fp:
    stage_table = json.loads(fp.read())
    for stageId, stageData in stage_table["stages"].items():
        levelId = stageData["levelId"]
        if levelId is None:
            stage = Stage(stageData["stageId"], stageData["code"], None)
        else:
            stage = Stage(stageData["stageId"], stageData["code"], levelId.lower())
        stage_list.append(stage)
with open(data_path, encoding="UTF-8") as fp:
    view_table = json.loads(fp.read())

if __name__ == "__main__":
    calc = Calc(1920, 1080)
    level = "2-10"
    img = cv2.imread(f"main/{level}.png")
    for i in calc.run(level, True):
        for j in i:
            tile, pos = j
            cv2.circle(img, pos, 10, (255 * tile.heightType, 0, 255 * tile.buildableType), -1)
    cv2.imwrite("test.png", img)
