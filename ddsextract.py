import os

def extract_dds_content(file_path, directory_path, start_sequence, end_sequence):
    with open(file_path, 'rb') as file:
        content = file.read()
        count = 0
        start_index = 0  # 从文件开头开始

        while start_index < len(content):
            # 查找文件头
            start_index = content.find(start_sequence, start_index)
            if start_index == -1:
                print(f"No more start sequences found in {file_path}")
                break

            # 查找下一个文件头
            next_start_index = content.find(start_sequence, start_index + len(start_sequence))
            if next_start_index == -1:
                end_index = len(content)
            else:
                end_index = next_start_index

            # 提取从当前文件头到下一个文件头之前的内容
            extracted_data = content[start_index:end_index]
            # 生成新的文件名
            new_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}_extracted_{count}.dds"
            new_filepath = os.path.join(directory_path, new_filename)
            # 保存到新文件
            with open(new_filepath, 'wb') as new_file:
                new_file.write(extracted_data)
            print(f"Extracted content saved as: {new_filepath}")
            count += 1

            # 更新内容，继续查找
            start_index = next_start_index

def main():
    directory_path = input("请输入要处理的文件夹路径: ")
    if not os.path.isdir(directory_path):
        print(f"错误: {directory_path} 不是一个有效的目录。")
        return

    start_sequence = b'\x44\x44\x53\x20\x7C\x00\x00\x00'  # DDS file header
    end_sequence = b'\x44\x44\x53\x20\x7C\x00\x00\x00'  # Next DDS file header

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"Processing file: {file_path}")
            extract_dds_content(file_path, directory_path, start_sequence, end_sequence)

if __name__ == "__main__":
    main()
