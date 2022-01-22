#include "opencv2/core.hpp"
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc.hpp>
#include "TileCalc.h"
int main() {
	auto img = cv::imread("..\\main\\2-10.png");
	auto calc = Map::TileCalc::TileCalc(1920, 1080, "..\\levels.json");
	std::vector<std::vector<cv::Point2d>> pos;
	std::vector<std::vector<Map::Tile>> tiles;
	calc.run("2-10", "", true, pos, tiles);
	for (int y = 0; y < pos.size(); y++) {
		for (int x = 0; x < pos[y].size(); x++) {
			cv::circle(img, pos[y][x], 10, cv::Scalar(tiles[y][x].buildableType * 255, 0, tiles[y][x].heightType * 255), -1);
		}
	}
	cv::imwrite("result.png", img);
}