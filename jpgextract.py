import os

def is_valid_jpg(data):
    # JPEG文件的开始标记
    start_marker = b'\xFF\xD8\xFF\xE0'
    # JPEG文件的结束标记
    end_marker = b'\xFF\xD9'
    # 数据块标记（JFIF或EXIF）
    block_markers = [b'JFIF', b'Exif']

    # 检查JPEG文件的开始标记
    if not data.startswith(start_marker):
        return None

    # 检查数据块开始标记
    for block_marker in block_markers:
        block_index = data.find(block_marker)
        if block_index != -1:
            # 检查文件尾标记
            end_index = data.find(end_marker, block_index)
            if end_index != -1:
                # 提取JPEG数据
                return data[:end_index + len(end_marker)]
    return None

def find_jpg_in_file(file_path):
    with open(file_path, 'rb') as file:
        file_content = file.read()
        jpg_start = file_content.find(b'\xFF\xD8\xFF\xE0')
        jpgs = []
        while jpg_start != -1:
            # 从文件头开始查找有效的JPEG数据
            jpg_data = is_valid_jpg(file_content[jpg_start:])
            if jpg_data:
                jpgs.append(jpg_data)
            # 移动到下一个可能的文件头位置
            jpg_start = file_content.find(b'\xFF\xD8\xFF\xE0', jpg_start + len(b'\xFF\xD8\xFF\xE0'))
        return jpgs

def extract_jpgs(directory_path):
    total_jpgs_extracted = 0
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            # Skip Python files and files containing 'disabled'
            if file.endswith('.py') or 'disabled' in file.lower():
                continue

            jpgs = find_jpg_in_file(file_path)
            for index, jpg_data in enumerate(jpgs):
                base_filename, _ = os.path.splitext(file)
                extracted_filename = f'{base_filename}_extracted_{index}.jpg'
                extracted_path = os.path.join(root, extracted_filename)
                with open(extracted_path, 'wb') as jpg_file:
                    jpg_file.write(jpg_data)
                total_jpgs_extracted += 1

    return total_jpgs_extracted

def main():
    directory_path = input("请输入要处理的文件夹路径: ")
    if not os.path.isdir(directory_path):
        print(f"错误: {directory_path} 不是一个有效的目录。")
        return

    total_jpgs_extracted = extract_jpgs(directory_path)
    print(f"Total jpgs extracted: {total_jpgs_extracted}")

if __name__ == "__main__":
    main()
