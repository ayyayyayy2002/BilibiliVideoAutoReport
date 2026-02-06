import os
yolo_file = os.path.join( 'model', 'yolo.onnx')
siamese_file = os.path.join( 'model', 'siamese.onnx')
reporter_cookie_file = os.path.join( 'model','reporter.json')
collector_cookie_file = os.path.join('model', 'collector.json')
uid_file = os.path.join( 'list', 'uid.txt')
white_file = os.path.join( 'list', 'white.txt')
black_file = os.path.join( 'list', 'black.txt')
keywords_file = os.path.join( 'list', 'keyword.txt')
true_dir = os.path.join( "record", "true")
false_dir = os.path.join( "record", "false")
report_dir= os.path.join( "record", "report")
chrome_binary_path = os.path.join( 'list','chrome-win', 'chrome.exe')
timeout_request= (2, 2)
timeout_browser=3000
CLASH_API_URL = "http://127.0.0.1:9090"
CLASH_PROXY_URL="127.0.0.1:7890"
proxies = {'http': "http://127.0.0.1:7890",'https': "http://127.0.0.1:7890"}
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'
tids_with_weights = {
    '10030': 1,  # 色情低俗
    '10031': 1,  # 违规广告引流
    '10032': 1,  # 涉政敏感
    '10033': 1,  # 引战、网暴、不友善
    '10034': 1,  # 传播谣言
    '10035': 1,  # 涉嫌诈骗
    '10036': 1,  # 引人不适
    '10037': 1,  # 涉未成年人不良信息
    '10038': 1,  # 封面党、标题党
    '10039': 1,  # 其他
}
reasons = [
    "视频标题title存在明显违规，引导性极强。在视频duration处，画面左下角出现疑似广告引流内容，诱导用户跳转站外平台。",
    "标题title与视频内容严重不符，涉嫌标题党。在duration附近画面中出现联系方式，引流至黑产渠道。",
    "视频使用title作为标题吸引点击，但在duration时段画面右侧出现非法广告水印，存在黑产推广嫌疑。",
    "标题title涉嫌歪曲历史事实，在duration位置通过字幕和画面暗示历史虚无主义观点。",
    "视频标题title正常，但在duration处画面下方滚动字幕传播政治谣言，误导观众。",
    "title视频在duration时间段，画面中出现明显辱华标语或符号，性质恶劣。",
    "视频标题title具有迷惑性，在duration处通过画面角落植入广告二维码进行非法引流。",
    "title作为封面与标题，但在duration附近内容出现黑产相关话术，诱导加群或私聊。",
    "视频标题title刻意制造对立情绪，在duration时画面配合字幕散布不实政治言论。",
    "title视频在duration画面左上角长期显示广告联系方式，疑似有组织的商业引流行为。",
    "标题title掩盖真实内容，在duration处画面出现非法交易相关文字提示。",
    "title视频在duration时间点，画面背景中出现明显辱华元素，违反平台规定。",
    "title视频通过封面吸引点击，但在duration段落插入与内容无关的广告画面。",
    "标题title下的视频在duration位置，通过字幕传播未经证实的政治谣言。",
    "title视频在duration画面右下角展示外部平台账号，存在恶意导流行为。",
    "title内容在duration附近出现歪曲历史的画面剪辑，存在历史虚无主义问题。",
    "视频标题title正常，但在duration处画面中出现明显黑产推广信息。",
    "title视频在duration段落，利用敏感话题配合字幕进行违规引流。",
    "标题title存在误导性，在duration画面中通过暗示性内容诱导关注和私信。",
    "title视频在duration时，画面局部出现违规标语或广告内容，影响恶劣。"
]
group='哔哩哔哩'
limit=20
cycle=1



