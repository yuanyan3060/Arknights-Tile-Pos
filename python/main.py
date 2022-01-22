import numpy as np
import cv2
from typing import List, Optional, Tuple
from dataclasses import dataclass
import json
import pathlib
import math
import time

@dataclass
class Tile:
    heightType: int
    buildableType: int


@dataclass
class Level:
    stageId: str
    code: str
    levelId: str
    name: str
    height: int = 0
    width: int = 0
    tiles: List[List[Tile]] = None
    view: int = 0

    @classmethod
    def from_json(cls, json_data: dict) -> 'Level':
        raw_tiles = json_data['tiles']
        tiles = []
        for row in raw_tiles:
            row_tiles = []
            for tile in row:
                row_tiles.append(Tile(tile['heightType'], tile['buildableType']))
            tiles.append(row_tiles)

        return cls(
            stageId=json_data['stageId'],
            code=json_data['code'],
            levelId=json_data['levelId'],
            name=json_data['name'],
            height=json_data['height'],
            width=json_data['width'],
            tiles=tiles,
            view=json_data['view']
        )

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

    def run(self, code: str = "", name: str = "", side: bool = False) -> List[List[Tuple[Tile, Tuple[int, int]]]]:
        """
        :param code: 关卡代号 例如:0-1 1-7
        :param name: 关卡名称 例如:与虫为伴 code和name中选填一个，一般情况code更方便，但是肉鸽关卡不能用code确定
        :param side: 是否是放置干员时的视角
        :return: Tile和坐标构成的列表
        """
        result: List[List[Tuple[Tile, Tuple[int, int]]]] = []
        level = None
        for item in levels:
            if code == item.code or name == item.name:
                level = item
        if level is None:
            return []
        if level.view == 0:
            x, y, z = 0.0, -4.81, - 7.76
            if side:
                x += 0.5975104570388794
                y -= 0.5
                z -= 0.882108688354492
        elif level.view == 1:
            x, y, z = 0.0, -5.60, -8.92
            if side:
                x += 0.7989424467086792
                y -= 0.5
                z -= 0.86448486328125
        elif level.view == 2:
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
        print(matrix)
        matrix = np.dot(self.matrix_p, matrix)
        h = level.get_height()
        w = level.get_width()
        for y in range(h):
            tmp: List[Tuple[Tile, Tuple[int, int]]] = []
            for x in range(w):
                tile = level.get_tile(y, x)
                np.array([x, y, z, 1])
                p_x, p_y, p_z, p_w = np.dot(matrix,
                                            np.array([(x - (w - 1) / 2), ((h - 1) / 2) - y, tile.heightType * -0.4, 1]))
                p_x = (1 + p_x / p_w) / 2
                p_y = (1 + p_y / p_w) / 2
                center = int(p_x * self.width), int((1 - p_y) * self.height)
                tmp.append((tile, center))
            result.append(tmp)
        return result

levels_path = pathlib.Path(__file__).parent / "levels.json"
levels: List[Level] = []
with open(levels_path, encoding="UTF-8") as fp:
    start = time.time()
    level_table = json.loads(fp.read())
    for data in level_table:
        levels.append(Level.from_json(data))
    print(time.time()-start)

if __name__ == "__main__":
    calc = Calc(1680, 1080)
    code = "2-10"
    img = cv2.imread(f"../main/{code}.png")
    for i in calc.run(code, side=True):
        for j in i:
            tile, pos = j
            cv2.circle(img, pos, 10, (255 * tile.heightType, 0, 255 * tile.buildableType), -1)
    cv2.imwrite("../test.png", img)
