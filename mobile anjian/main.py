import numpy as np
import cv2
from typing import List, Optional, Tuple
from dataclasses import dataclass
import json
import pathlib
import math
import re

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
    view: List[List[float]] = None

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

    def run(self, code: str = "", name: str = "", side: bool = False, stage_id: Optional[str] = None) -> List[List[Tuple[Tile, Tuple[int, int]]]]:
        """
        :param code: 关卡代号 例如:0-1 1-7
        :param name: 关卡名称 例如:与虫为伴 code和name中选填一个，一般情况code更方便，但是肉鸽关卡不能用code确定
        :param side: 是否是放置干员时的视角
        :return: Tile和坐标构成的列表
        """
        result: List[List[Tuple[Tile, Tuple[int, int]]]] = []
        level = None
        for item in levels:
            if (item.stageId == stage_id if stage_id is not None
                    else code == item.code or name == item.name):
                level = item
        if level is None:
            return []
        if side:
            x, y, z = level.view[1]
        else:
            x, y, z = level.view[0]
        # act3 full-map view[0/1] means preparation shop/hand.
        autochess = re.fullmatch(r"activities/act3autochess/level_act3autochess_m\d{2}",
                                 level.levelId.lower().replace("\\", "/")) is not None
        if autochess:
            f32 = np.float32
            aspect, native = f32(self.width / self.height), f32(16 / 9)
            epsilon = f32(1e-5)
            ratio = 1.0 if aspect >= f32(native - epsilon) else float(f32(
                f32(f32(f32(native / aspect) - f32(1)) * f32(.64)) + f32(1)))
            y += (ratio - 1) * -4.809999942779541
            z += (ratio - 1) * -7.760000228881836
        else:
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

        if side and not autochess:
            matrix = np.dot(matrix_x, matrix_y)
            matrix = np.dot(matrix, raw)
        else:
            matrix = np.dot(matrix_x, raw)
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
                center = int(p_y * self.height),int(p_x * self.width)#交换了xy坐标,符合按键精灵的竖屏坐标 
                tmp.append((center))
                #print(x,y,center)
            result.append(tmp)
        return result

levels_path = pathlib.Path(__file__).parent.parent / "levels.json"
map_path=pathlib.Path(__file__).parent  
levels: List[Level] = []
calc = Calc(1920, 1080)
with open(levels_path, encoding="UTF-8") as fp:
    level_table = json.loads(fp.read())
    for data in level_table:
        print(data["name"],data["code"])
        levels.append(Level.from_json(data))
        if data["name"]== None:
            continue
        coordinate=[calc.run(code=data["code"],name=data["name"], side=False, stage_id=data["stageId"]),calc.run(code=data["code"],name=data["name"], side=True, stage_id=data["stageId"])]
        #print (coordinate)
        fw = open(map_path/(data["name"]+".txt"), 'w',encoding="UTF-8") #按地图名+保存坐标到txt  
        fw.write(json.dumps((coordinate), sort_keys=True, indent=4, separators=(',', ': '))) # 将字符串写入文件中

'''
if __name__ == "__main__":
    calc = Calc(1920, 1080)#屏幕分辨率
    code = "CE-6"    
    print( json.dumps(calc.run(code, side=False)))    
    print( json.dumps(calc.run(code, side=True))) 
'''
