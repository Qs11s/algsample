# algsample
CS360/SE360 Artificial Intelligence Group Project - Optimal Samples Selection System

## 项目简介
从大数据集中筛选公平、无偏且最优的样本子集，满足项目指定的约束条件（m、n、k、j、s参数约束）。

## 核心功能
1. 支持参数m（45-54）、n（7-25）、k（4-7）、j（s≤j≤k）、s（3-7）输入与合法性校验
2. 支持随机生成或用户自定义初始n个样本（1~m的正整数）
3. 基于贪心算法筛选最小有效k样本子集集合，满足覆盖约束
4. 结果保存到algsample_db目录（JSON格式DB文件，命名规范：m-n-k-j-s-x-y.json）
5. 支持DB文件加载、删除操作

## 运行方式
1. 克隆仓库到本地：
   ```bash
   git clone https://github.com/your-username/algsample.git
   cd algsample