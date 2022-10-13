/usr/local/Cellar/python@3.9/3.9.1_6/Frameworks/Python.framework/Versions/3.9/lib/python3.9/enum.py

/Users/Zichoole/.local/share/virtualenvs/audio-god-jcJC6gcV/lib/python3.9/site-packages/eyed3

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
export 所有空值的 field 都不要输出, 要注意对整型数据 0 和 0.0 的判断，0 的话也要输出，不算空值
import 某个 field 为空值时，是直接赋值空值还是跳过不赋值 这块逻辑梳理下

import evernote+plist+markdown & export markdown+plist & directory maker & plist playlist
仿照 arkid 项目，增加 precommit 等
看看有必要增加几种类型的导入导出文件之间的相互转化
pydoc.pipepager
取消 string 类型的 enum 中的 value 累赘
是否可虑适配 windows 系统，并将代码中的 / 符号全部检查一遍，替换为 os.path.join 形式，甚至需要更改 grouping 分隔符, os.path.normpath() os.path.normcase()  if sys.platform == "win32":
os.symlink & os.link 看看取舍
load audios 时删除所有无效软链接，或者全部软链接都删除也可以, https://gist.github.com/seanh/229454, if not os.path.exists(os.readlink(path)): os.path.exists(os.path.realpath(path)) link_target=os.readlink(path) dir=os.path.dirname(path) if not os.path.isabs(link_target): link_target=os.path.join(dir, link_target) if os.path.exists(link_target):
创建软链接时，目前都是用的绝对路径，是否应该改成相对路径 
