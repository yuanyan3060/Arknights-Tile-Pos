#encoding= Utf-8
import json
import time
import pathlib

levels_path = pathlib.Path(__file__).parent / "levels0.json"#side=false坐标
#levels_path = pathlib.Path(__file__).parent / "levels1.json"#side=true坐标
with open(levels_path, encoding="UTF-8") as fp:
    start = time.time()
    level_table = json.loads(fp.read())
    for name,data in level_table.items():
        print (name)
        data=data["tiles"]
        data.reverse()#从下往上排列
        for i in range(len(data)):
            for j in range(len(data[i])):
                data[i][j]=data[i][j]["pos"]
                
                data[i][j][0],data[i][j][1]=1080-data[i][j][1],data[i][j][0]#转换为按键精灵坐标,原点为竖屏左上角
        fw = open("../map/"+name+"0.txt", 'w',encoding="UTF-8") #按地图名+0保存坐标到txt
        #fw = open("../map/"+name+"1.txt", 'w',encoding="UTF-8") #按地图名+1保存坐标txt
        fw.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))) # 将字符串写入文件中
        
    print(time.time()-start)