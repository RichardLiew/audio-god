/usr/local/Cellar/python@3.9/3.9.1_6/Frameworks/Python.framework/Versions/3.9/lib/python3.9/enum.py

/Users/Zichoole/.local/share/virtualenvs/audio-god-jcJC6gcV/lib/python3.9/site-packages/eyed3

增加mp4转mp3等等的功能
将常用命令写到印象笔记
命令行 单个 - 的参数重新分配
思考如何处理同一首歌可以存在于多个歌单的情景，并在markdown文件中体现出来，软连接？
导出 markdown 色彩版和简单版
支持解析 markdown 和普通 notes 两种方式
去除 Markdown 中的链接下划线
去除依赖库，改为嵌入到本文件的相关代码
封装成docker，并传到 github 以及 dockerhub 上，并添加 actions
过滤和排序对 artwork 的单独处理
读入和导出 apple music xml 格式文件
支持属性输入由文件名决定
支持将多个歌手创作的同一首歌加入所有歌手的列表中，同时，多个歌手列表保留
在导出和加载itunes plist功能时，加入对mac系统和itunes版本的判断
完善 help 信息，将所有可能的场景对应的命令写入帮助信息里
export-json, export-markdown 功能完善
重新审视 Plist 生成逻辑，field做成可配，并引用新的域结构
export 逻辑里，仿照 import 逻辑去配合 filesources 做
FILENAME 作为属性数据源的逻辑还没有梳理
