# Faceworks

一个基于CNN的颜值打分器

## 社区

本项目为 PY-Learning 群共同维护，PY-Learning是一个交流Python学习、IT前沿、~~程序员情感~~的微信社群，现有活跃在各个领域的社员123人。

加入社区请联系群秘书机器人「Wbot」，通过申请后自动邀请进群。群秘书二维码：

![robot wechat](https://ws2.sinaimg.cn/large/006tNc79gy1fhkg6jfx6rj30uu0zkwgo.jpg)

## 项目划分

项目划分为几个子项目：

+ `facespider` 在网络上爬取人像照片的爬虫机器人
+ `pre-processor` 旋转、裁剪、调色等预处理人像工具集合
+ `grader` 一个基于Web的交叉评分系统，获取人像评分的数据
+ `cnn` 卷积神经网络设计、训练相关代码
+ `services` 对外提供服务的Web接口
