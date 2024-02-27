# 交我润

## 项目简介

基于雷电命令行的交我办自动跑步脚本，脱胎于[AutoWSGR](https://github.com/huan-yp/Auto-WSGR)

## 使用方法

### 安装

#### 前期准备

安装 [雷电模拟器](https://www.ldmnq.com/), [交我办](https://net.sjtu.edu.cn/wlfw/jwbApp.htm).

雷电模拟器请安装雷电模拟器9

[安装 Python](https://zhuanlan.zhihu.com/p/111168324) 注意, Python 版本要求 3.9 <= x <= 3.11, 我们推荐你安装 [Python3.9.13](https://www.python.org/downloads/release/python-3913/).

将模拟器设置为 `>=1280x720` 的 `16:9` 分辨率(推荐使用 1280x720 分辨率).

#### 安装本项目(sjtuautorun)

autowsgr 目前已支持通过 [PyPI](https://pypi.org/project/sjtuautorun/) 进行部署, 在安装好 Python 后, 打开命令提示符(cmd), 输入以下命令后回车.

```bash
pip install -U sjtuautorun
```

#### 检查是否安装成功

`Win+r` 打开 "运行", 输入 `python` 后回车, 在打开的黑框框里输入以下代码:

```python
import sjtuautorun
print(sjtuautorun.__version__)
```

能正常显示版本即为成功

## 近期更新

- 完成脚本基本逻辑，实现单个短程自动跑步 *2024/02/26*

## 使用本项目

## 未来开发任务

- 随机化跑步数据
- 调整图像识别模块，实现自动启动、结束
- 不同跑步策略（如光体、南体跑圈等）

