Processing:
steps in usage需要和generate script以及cleanup, 以及所有的actions和branches都要覆盖到里 同步更新, start和test都要同步
有一个地想不起来了，和 cls.NAME? output? 有关







type: ignore
All done.


Useful Paths:
/usr/local/Cellar/python@3.9/3.9.1_6/Frameworks/Python.framework/Versions/3.9/lib/python3.9/enum.py
/Users/Zichoole/.local/share/virtualenvs/audio-god-jcJC6gcV/lib/python3.9/site-packages/eyed3
/Users/Zichoole/.pyenv/versions/3.10.6/lib/python3.10


Relax:
在每一个调用 for in sources 里，都记得输出处理日志，并带有 23/136 这样的处理进度，最好同时额外带一个进度条，看看日志和进度条是线程的全d吗
详细梳理增量更新的逻辑，并写在usage里
mgg文件解密（意义不大，因为tencent会定期更换mgg的加密算法，windows下生成的是mgg，而mac下是qmc，很好解密）
-a -b -c 参数重新分配
看看能不能改成多进程以及多线程模式，加快速度（应该不行，好多依赖的库，貌似都是线程不安全的，更别提多进程了，暂时维持现状吧）
qmc等文件转化完mp3后，tags会丢失是吧？
看看能加进度条地方，都加上
记得同时实现导出音频的封面和上传封面给音频这两个功能
Action 继承自多个父类时，ARGUMENTS and KWARGS and rewrite_parameters 怎么合并
多个父类导致action顺序被改变，那些参数，在不断的子类继承时被update，顺序也变了
检查所有的 Action 里对应的 Argument，所有的参数校验和rewrite都要在 rewrite_parameters函数里完成
pydoc 字体各版式控制, 研究 pydoc 样式如何渲染
自己搭建云播放平台？网站？App？
VScode VS Cursor
输出的错误信息，如果不是程序bug，那就不要把代码栈打印出来，只打印有效信息就行
导出 markdown 色彩版和简单版, 去除 Markdown 中的链接下划线
去除依赖库，改为嵌入到本文件的相关代码
封装成docker，并传到 github 以及 dockerhub 上，并添加 actions
是否可虑适配 windows 系统，并将代码中的 / 符号全部检查一遍，替换为 os.path.join 形式，甚至需要更改 grouping 分隔符, os.path.normpath() os.path.normcase()  if sys.platform == "win32":
python match case 如果对应的是变量或者公式或者函数调用，该怎么处理
是否需要全域都进行 type checking ？类似 typescript
在导出和加载 itunes plist 功能时，加入对mac系统和itunes版本的判断
import evernote+plist+markdown & export markdown+plist & directory maker & plist playlist
仿照 arkid 项目，增加 precommit 等, pre-commit-config.yaml, .pre-commit-hooks.yaml, (Anebit/startupmate-backend), .flake8, .readthedocs.yml
看看有必要增加几种类型的导入导出文件之间的相互转化
export 的那几种形式，是否需要独立拆分出单独的 actions？
import_json, import_markdown, import_plist
export-json, export-markdown, export_note 功能完善
convert-qmc0, convert-kmx, convert-mp4
命令行参数支持从类似json的配置文件加载？比如那些json形式的命令行参数，或者直接就全部命令行参数都支持json或者yaml,toml格式配置载入
plist 文件里的 kind，track_type，file_folder_count，library_folder_count 设置规则需要重新审视下
display 命令里，过滤和排序对 artwork 的单独处理
解决在bash中获取解释器路径的逻辑，目前由于bash写入history文件有延时，即使设置了PROMPT_COMMAND="history -a"也没用，因为只有当当前命令执行完毕才会写入历史文件，sleep也没有用，调用python中调用subprocess会开启看不到的额外终端，与当前执行脚本的会话不在同一会话，所以怎么操作都没有意义。底线逻辑是获取当前python脚本的解释器完整路径（psutil.Process(os.getpid()).cmdline()），这个是可以实时做到的，但是完整路径过长，和想要的效果不同。psutil.Process().parent().name().lower()获取shell类型的逻辑里，如果是脚本间多层嵌套的话，那么parent()可能与人工执行命令的主终端所在会话不一样，可能会出错.
是否需要针对repeated的audios汇总groups
type ignore都处理一下
os.path.dirname如果是根目录，那么结尾会带有/，其他情况不带，此时对结尾去除/后，逻辑关系会变化，全局梳理下


Fixed:
没有必要增加多个note合并的功能，直接追加到 origin 文件底部就可以了，逻辑上是一样的
输出的note或者其他的，plist、markdown，各种tree等，排序要第一是artist，第二是album，第三才是title
所有的logger是否需要集成到handle_out里？（应该不用，保持现状就挺好）
有必要在ARGUMENTS里增加disable字段吗？表示排除这个参数(没有必要，违背当时设定 必要参数这个选项了)
对于 summaries里的properties，有必要根据fields的指定顺序排序下吗？
把所有的.format()都改为keyvalue形式
os.environ['HOME'], os.path.expandvars('${HOME}'), '~' 看看是否需要统一下
看看所有的路径或者其他的可配置的内容，是否独立出来写成宏
import 某个 field 为空值时，是直接赋值空值还是跳过不赋值 这块逻辑梳理下（字段为空值，则就直接赋值即可，无需考虑别的，不赋值的话就不要加这个字段就行了，对于 None 的情况，通常本程序需求的场景不考虑这种情况，只有空值，没有None）
export 所有空值的 field 都不要输出, 要注意对整型数据 0 和 0.0 的判断，0 的话也要输出，不算空值
notes文件加载逻辑里，歌曲信息里的属性值优先级是最高的，高于 分组信息 行
genre 和 grouping 里不能包含空白符
fieldtype 在display和export里都要使用
export 支持指定文件类型和属性名的中英文
所有正则表达式里的空格改成\s
所有的fetch和fetchx都看看是否缺参数
所有需要split的地方，都要三部曲,所有split的地方，都要考虑空字符串切割后列表并不为空而是有一个空字符串元素,查查看所有的split，有些是不需要去重和去空白的
groups有重复的情况要处理一下(GROUPING和group都查找一下)
export note时，输出概览
import note & format note & export note 三者统一一下, import和export 所有方式抽象出统一部分
import 时支持fields三种类型识别
看看 genre 和 grouping 是否在summaries时扣除去
看看 import 和 export 逻辑里可以做到增量更新吗,新增曲库时，看看各个环节是否可以由全量模式改为增量模式
oad_sources(matched=True)这里的matched看看能不能去掉，太别扭


Giveup:
os.symlink & os.link 看看取舍
创建软链接时，目前都是用的绝对路径，是否应该改成相对路径
判断是否是硬连接 os.stat(filename).st_nlink > 1
load audios 时删除所有无效软链接，或者全部软链接都删除也可以, https://gist.github.com/seanh/229454, if not os.path.exists(os.readlink(path)): os.path.exists(os.path.realpath(path)) link_target=os.readlink(path) dir=os.path.dirname(path) if not os.path.isabs(link_target): link_target=os.path.join(dir, link_target) if os.path.exists(link_target):
支持将多个歌手创作的同一首歌加入所有歌手的列表中，同时，多个歌手列表保留, 思考如何处理同一首歌可以存在于多个歌单的情景，并在markdown文件中体现出来，软连接？
支持属性输入由文件名决定, FILENAME 作为属性数据源的逻辑还没有梳理
