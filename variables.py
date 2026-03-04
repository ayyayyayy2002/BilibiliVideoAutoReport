import os

# 模型路径
yolo_file = os.path.join('model', 'yolo.onnx')       # YOLO模型文件路径
siamese_file = os.path.join('model', 'siamese.onnx') # Siamese模型文件路径


collector_cookie_file = os.path.join('model', 'collector.json') # 收集账号cookie

# UID及名单文件
uid_file = os.path.join('list', 'uid.txt')        # 待处理UID列表
white_file = os.path.join('list', 'white.txt')    # 白名单UID
black_file = os.path.join('list', 'black.txt')    # 黑名单UID
keywords_file = os.path.join('list', 'keyword.txt') # 关键字列表
uid_sql = os.path.join('list', 'uid.sqlite3')    # 黑名单SQL

# 记录目录
true_dir = os.path.join("record", "true")    # 成功操作记录
false_dir = os.path.join("record", "false")  # 失败操作记录
report_dir = os.path.join("record", "report")# 举报日志目录

# 浏览器路径与超时设置
chrome_binary_path = os.path.join('list', 'chrome-win', 'chrome.exe')  # Chrome 可执行文件
timeout_request = (3, 3)   # 请求超时时间 (连接, 读取)
timeout_browser = 5000     # 浏览器操作超时 (毫秒)

# 代理设置
CLASH_API_URL = "http://127.0.0.1:9090"     # Clash API 地址
CLASH_PROXY_URL = "127.0.0.1:7890"         # Clash 本地代理端口
proxies = {
    'http': "http://127.0.0.1:7890",
    'https': "http://127.0.0.1:7890"
}
# Clash代理组名称
group = '哔哩哔哩'

# 单个UID最大举报次数
limit = 500
#举报账号个数
accountcount=3
#已举报提示后是否跳过该目标
skip=False

# 循环次数（可用于多轮操作）
cycle = 3

# User-Agent
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'

# 视频分类及权重（用于举报tid随机选择）
tids_with_weights = {
    '10030': 1,  # 色情低俗
    '10031': 10,  # 违规广告引流
    '10032': 10,  # 涉政敏感
    '10033': 10,  # 引战、网暴、不友善
    '10034': 1,  # 传播谣言
    '10035': 1,  # 涉嫌诈骗
    '10036': 1,  # 引人不适
    '10037': 1,  # 涉未成年人不良信息
    '10038': 1,  # 封面党、标题党
    '10039': 1,  # 其他
}

reasons = [
    # --- 1-10: 侧重于网络暴力与人身攻击 ---
    "视频利用 title 煽动情绪，在 duration 处集中剪辑片段断章取义，刻意放大个人失误，引导观众在评论区进行人身攻击与辱骂。",
    "借 title 制造争议话题，在 duration 中恶意拼接言论内容，诱导用户参与围攻，当事人遭受大规模网络暴力。",
    "封面及 title 带有明显贬损意味，在 duration 关键时段反复播放片段，引导评论区对特定群体进行嘲讽和羞辱。",
    "视频通过 title 挂标签方式抹黑个人形象，在 duration 段落中夸张表达，引发评论区情绪化谩骂。",
    "在 title 的挑衅性语言吸引下，duration 处刻意渲染冲突细节，诱导用户进行攻击性评论。",
    "视频在 duration 处集中展示片面证据，配合 title 暗示性表达，煽动观众对当事人实施网络围剿。",
    "标题 title 带有明显侮辱色彩，在 duration 画面中持续强化负面叙事，导致评论区出现大量恶意攻击。",
    "采用 title 进行情绪操纵，在 duration 时刻放大争议片段，引导观众发布辱骂和威胁性言论。",
    "视频以 title 为导火索，在 duration 画面中恶意解读行为动机，引发群体性网络暴力。",
    "针对 title 搜索进来的用户，在 duration 处强化对立叙事，诱导观众参与集体嘲讽与攻击。",

    # --- 11-20: 侧重于引战与男女对立 ---
    "视频利用 title 制造性别冲突话题，在 duration 中选择性剪辑案例，刻意放大男女矛盾，引发评论区激烈对骂。",
    "标题 title 带有明显挑衅性，在 duration 处渲染个别事件，误导观众将个案上升为性别群体对立。",
    "视频在 duration 画面中通过夸张数据对比，强化男女对立情绪，诱导用户发表极端观点。",
    "借 title 蹭热度引发性别争议，在 duration 中断章取义地展示言论，激化双方矛盾。",
    "视频在 duration 时段通过片面案例渲染群体问题，配合 title 的情绪化表达，引战效果明显。",
    "标题 title 正常化伪装下，duration 处刻意突出冲突细节，推动评论区形成性别对立阵营。",
    "视频利用 title 提供偏颇叙事，在 duration 处展示片面观点，诱导用户发表攻击性性别言论。",
    "在 duration 画面中强化对立标签，配合 title 的夸张表述，引导评论区持续争吵。",
    "视频通过 title 锚定争议焦点，在 duration 处不断重复极端言论，加剧性别对立氛围。",
    "标题 title 借助热点话题，在 duration 处引入争议观点，制造长期引战效果。",

    # --- 21-30: 侧重于政治谣言与虚假信息传播 ---
    "标题 title 使用误导性表述，在 duration 处传播未经证实的政治消息，引发观众误解。",
    "视频通过 title 制造紧张氛围，在 duration 画面中展示来源不明的所谓内幕信息，涉嫌散布政治谣言。",
    "该内容利用 title 吸引点击，在 duration 中断章取义引用讲话内容，误导公众认知。",
    "视频在 duration 处通过拼接旧闻充当新消息，配合 title 夸大其词，传播虚假政治信息。",
    "利用 title 制造爆点，在 duration 处引用不实数据，误导观众形成错误判断。",
    "视频在 duration 时刻散布未经核实的政策变动消息，配合 title 引发恐慌性讨论。",
    "标题 title 伪装为分析解读，却在 duration 处传播缺乏依据的政治指控。",
    "视频在 duration 处引用匿名来源爆料，配合 title 的渲染式表达，涉嫌造谣。",
    "该内容在 duration 中混淆时间线，误导观众理解事件背景，配合 title 制造误解。",
    "标题 title 存在明显夸张成分，在 duration 处传播片面信息，引发舆论误导。",

    # --- 31-40: 综合网络操纵与情绪煽动 ---
    "视频通过 title 刻意放大矛盾，在 duration 处反复强化对立观点，诱导评论区情绪化表达。",
    "在 duration 处通过断章取义剪辑内容，配合 title 的煽动性语言，引发群体冲突。",
    "视频利用 title 占据话题热度，在 duration 中传播偏颇观点，激发观众攻击性言论。",
    "标题 title 极度情绪化，在 duration 处渲染冲突细节，扩大争议范围。",
    "视频在 duration 时间点集中输出单一立场观点，配合 title 激化舆论对抗。",
    "利用 title 进行情绪引导，在 duration 处强化对立叙事，推动评论区形成阵营化对抗。",
    "视频在 duration 处通过反复播放争议画面，配合 title 制造持续争议氛围。",
    "标题 title 虚假导向，在 duration 处呈现片面内容，引导观众发表极端言论。",
    "该内容在 duration 处借助夸张表达制造误解，配合 title 扩大社会对立。",
    "视频在 duration 时段刻意强化争议标签，利用 title 引发长期舆论冲突。"
]

