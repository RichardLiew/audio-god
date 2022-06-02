/usr/local/Cellar/python@3.9/3.9.1_6/Frameworks/Python.framework/Versions/3.9/lib/python3.9/enum.py

/Users/Zichoole/.local/share/virtualenvs/audio-god-jcJC6gcV/lib/python3.9/site-packages/eyed3

命令行 单个 - 的参数重新分配
导出 markdown 色彩版和简单版, 去除 Markdown 中的链接下划线
去除依赖库，改为嵌入到本文件的相关代码
封装成docker，并传到 github 以及 dockerhub 上，并添加 actions
过滤和排序对 artwork 的单独处理
支持将多个歌手创作的同一首歌加入所有歌手的列表中，同时，多个歌手列表保留, 思考如何处理同一首歌可以存在于多个歌单的情景，并在markdown文件中体现出来，软连接？
在导出和加载 itunes plist 功能时，加入对mac系统和itunes版本的判断
支持属性输入由文件名决定, FILENAME 作为属性数据源的逻辑还没有梳理
import_json, import_markdown, import_plist
export-json, export-markdown, export_note 功能完善
convert-qmc0, convert-kmx, convert-mp4
plist 文件里的 kind，track_type，file_folder_count，library_folder_count 设置规则需要重新审视下
看看 import 和 export 逻辑里可以做到增量更新吗






第一步：下载曲目，并保证文件名是按照“歌手-曲名”命名的
第二步：将曲目详细信息添加到 Notes 文件中，并做好分类
第三步：format-notes
第四步：fill-properties
第五步：format-properties
第六步：rename-audios
第七步：organize-files
第八步：export plist, markdown



额外功能：
1. derive-artworks
2. convert
3. display
