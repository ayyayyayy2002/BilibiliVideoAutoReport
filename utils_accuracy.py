import os

from variables import true_dir, false_dir


def calc_accuracy():
    true_count = len([f for f in os.listdir(true_dir) if f.lower().endswith(".jpg")])
    false_count = len([f for f in os.listdir(false_dir) if f.lower().endswith(".jpg")])

    total = true_count + false_count
    acc = true_count / total if total > 0 else 0

    print(f"成功样本数: {true_count}")
    print(f"失败样本数: {false_count}")
    print(f"正确率: {acc:.2%}")


