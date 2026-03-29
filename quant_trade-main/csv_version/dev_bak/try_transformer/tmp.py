import os
import random
import pandas as pd
import shutil
import zipfile
from datetime import datetime

# 设置路径和参数
source_path = fr"E:\stock\csv_version\out_analysis_results"  # 源路径，替换为你的实际路径
dest_folder = fr"E:\stock\csv_version\out_analysis_results\selected_csv_files"  # 目标文件夹名称
num_files = 150
min_rows = 1000

# 创建目标文件夹
if not os.path.exists(dest_folder):
    os.makedirs(dest_folder)
    print(f"创建目标文件夹: {dest_folder}")

# 获取所有符合条件的CSV文件
csv_files = []
for file in os.listdir(source_path):
    if file.endswith(".csv"):
        file_path = os.path.join(source_path, file)
        try:
            # 使用Pandas快速获取行数
            df = pd.read_csv(file_path, nrows=min_rows+1)
            if len(df) > min_rows:
                csv_files.append((file_path, len(df)))
        except Exception as e:
            print(f"跳过文件 {file}: {str(e)}")
            continue

print(f"找到 {len(csv_files)} 个符合条件的CSV文件")

# 随机选择文件
if len(csv_files) > num_files:
    selected = random.sample(csv_files, num_files)
else:
    selected = csv_files
    print(f"警告: 只有 {len(csv_files)} 个符合条件的文件，选择所有")

# 移动文件到目标文件夹
moved_files = []
for file_path, row_count in selected:
    try:
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(dest_folder, file_name)
        shutil.copy2(file_path, dest_path)  # 使用copy2保留元数据
        moved_files.append((file_name, row_count))
        print(f"已复制: {file_name} (行数: {row_count})")
    except Exception as e:
        print(f"复制文件 {file_path} 时出错: {str(e)}")

# 创建压缩包
if moved_files:
    timestamp = datetime.now().strftime("%Y%m%d")
    zip_filename = fr"E:\stock\csv_version\out_analysis_results\selected_csv_files_{timestamp}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_name, _ in moved_files:
            file_path = os.path.join(dest_folder, file_name)
            zipf.write(file_path, file_name)
    
    print(f"\n已创建压缩包: {zip_filename}")
    print(f"总共处理了 {len(moved_files)} 个文件")
else:
    print("没有文件被移动和压缩")