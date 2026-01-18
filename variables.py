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
CLASH_API_URL = "http://127.0.0.1:9090"
CLASH_PROXY_URL="127.0.0.1:7890"
proxies = {'http': "http://127.0.0.1:7890",'https': "http://127.0.0.1:7890"}
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
reason='标题title和封面违规,黑产,引流,历史虚无,政治谣言'
group='哔哩哔哩'
limit=100
cycle=1



