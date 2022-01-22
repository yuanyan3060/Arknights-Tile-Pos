#pragma once

#include <string>
#include <vector>

#include <opencv2/opencv.hpp>
#include <meojson/include/json.hpp>

namespace Map {
    struct Tile
    {
        int heightType = 0;
        int buildableType = 0;
    };

    class Level {
    public:
        Level(const json::value& data);
        int get_width() const;
        int get_height() const;
        Tile get_item(int y, int x) const;
        int view = 0;
        std::string stageId;
        std::string	code;
        std::string	levelId;
        std::string	name;
    private:
        int height = 0;
        int width = 0;
        std::vector<std::vector<Tile>> tiles;
    };
    class TileCalc
    {
    public:
        TileCalc(int width, int height, const std::string& dir);
        bool run(const std::string& code, const std::string& name, bool side, std::vector<std::vector<cv::Point2d>>& out_pos, std::vector<std::vector<Tile>>& out_tiles) const;
    private:
        int width = 0;
        int height = 0;
        const double degree = atan(1.0) * 4 / 180;
        std::vector<Level> levels;
        cv::Mat MatrixP = cv::Mat(4, 4, CV_64F);
        cv::Mat MatrixX = cv::Mat(4, 4, CV_64F);
        cv::Mat MatrixY = cv::Mat(4, 4, CV_64F);
        bool adapter(double& x, double& y) const;
    };
}
