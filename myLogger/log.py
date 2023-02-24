import logging
import os


def mkdir(path):
    # 去除尾部 / 符号
    path = path.rstrip("/")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        return False


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Log等级总开关

log_path = "../logs/"
mkdir(log_path)
logfile = "../logs/Error.log"
formatter = logging.Formatter(
    fmt="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: \n%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console_formatter = logging.Formatter(
    fmt="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# log文件的配置
handler = logging.FileHandler(logfile)
handler.setLevel(logging.WARNING)
handler.setFormatter(formatter)

# 控制台的配置
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(console_formatter)

logger.addHandler(handler)
logger.addHandler(console)
