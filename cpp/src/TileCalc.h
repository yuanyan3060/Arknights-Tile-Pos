#pragma once
#include <opencv2/opencv.hpp>
#include <string>
#include "meojson/include/json.hpp"
#include <vector>
namespace Map {
	struct Tile
	{
		int heightType;
		int buildableType;
	};

	class Level {
	public:
		Level(const json::value &data);
		int get_width();
		int get_height();
		Tile get_item(int y, int x);
		int view;
		std::string stageId;
		std::string	code;
		std::string	levelId;
		std::string	name;
	private:
		int height;
		int width;
		std::vector<std::vector<Tile>> tiles;
	};
	class TileCalc
	{
	public:
		TileCalc(int width, int height, const std::string& dir);
		void run(const std::string& code, const std::string& name, bool side, std::vector<std::vector<cv::Point2d>> &out_pos, std::vector<std::vector<Tile>> &out_tiles);
	private:
		int width;
		int height;
		double degree = atan(1.0) * 4 / 180;
		std::vector<Level> levels;
		cv::Mat MatrixP = cv::Mat(4, 4, CV_64F);
		cv::Mat MatrixX = cv::Mat(4, 4, CV_64F);
		cv::Mat MatrixY = cv::Mat(4, 4, CV_64F);
		bool adapter(double& x, double& y);
	};
}
