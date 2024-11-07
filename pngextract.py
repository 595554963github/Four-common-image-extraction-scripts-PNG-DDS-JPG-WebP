import os

def extract_content(file_path, directory_path, start_sequence, block_marker, end_sequence):
    with open(file_path, 'rb') as file:
        content = file.read()
        start_index = content.find(start_sequence)
        if start_index == -1:
            print(f"No start sequence found in {file_path}")
            return
        
        # 从第一个文件头开始读取
        content = content[start_index:]
        count = 0
        while True:
            start_index = content.find(start_sequence)
            if start_index == -1:
                print(f"No more start sequences found in {file_path}")
                break

            # 从找到的字节序列开始，直到下一个字节序列结束
            next_start_index = content.find(start_sequence, start_index + len(start_sequence))
            if next_start_index == -1:
                # 如果没有找到下一个文件头，则提取剩余的内容
                end_index = len(content)
            else:
                # 提取从文件头到下一个文件头之前的内容
                end_index = next_start_index

            # 提取内容
            extracted_data = content[start_index:end_index]
            # 检查是否为有效PNG（即是否包含数据块标记）
            if block_marker in extracted_data:
                # 生成新的文件名
                new_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}{count}.png"
                new_filepath = os.path.join(directory_path, new_filename)
                # 保存到新文件
                with open(new_filepath, 'wb') as new_file:
                    new_file.write(extracted_data)
                print(f"Extracted content saved as: {new_filepath}")
                count += 1
            else:
                print(f"Invalid PNG data found in {file_path}, skipping...")

            # 更新内容，继续查找
            if next_start_index == -1:
                break
            content = content[next_start_index:]

def main():
    directory_path = input("请输入要处理的文件夹路径: ")
    if not os.path.isdir(directory_path):
        print(f"错误: {directory_path} 不是一个有效的目录。")
        return

    # 定义要查找的字节序列
    start_sequence = b'\x89\x50\x4E\x47'
    block_marker = b'\x49\x48\x44\x52'
    end_sequence = b'\x00\x00\x00\x49\x45\x4E\x44\xAE\x42\x60\x82'

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"Processing file: {file_path}")
            extract_content(file_path, directory_path, start_sequence, block_marker, end_sequence)

if __name__ == "__main__":
    main()
