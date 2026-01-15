import os

base_dir = os.getcwd()
yolo_file = os.path.join(base_dir, 'model', 'yolo.onnx')
siamese_file = os.path.join(base_dir, 'model', 'siamese.onnx')
reporter_cookie_file = os.path.join(base_dir, 'model','reporter.json')
collector_cookie_file = os.path.join(base_dir,'model', 'collector.json')
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
reason='标题title和封面违规,黑产,引流'
group='哔哩哔哩'
uid_file = os.path.join(base_dir, 'list', 'uid.txt')
white_file = os.path.join(base_dir, 'list', 'white.txt')
black_file = os.path.join(base_dir, 'list', 'black.txt')
keywords_file = os.path.join(base_dir, 'list', 'keyword.txt')
true_dir = os.path.join(base_dir, "record", "true")
false_dir = os.path.join(base_dir, "record", "false")
chrome_binary_path = os.path.join(base_dir, 'list','chrome-win', 'chrome.exe')
chrome_driver_path = os.path.join(base_dir, 'list','chrome-win', 'chromedriver.exe')
CLASH_API_URL = "http://127.0.0.1:9090"
proxies = {
    'http': "http://127.0.0.1:7890",
    'https': "http://127.0.0.1:7890"
}