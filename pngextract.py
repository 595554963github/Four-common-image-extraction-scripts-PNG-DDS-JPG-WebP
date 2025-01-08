import os
import struct

def extract_content(file_path, directory_path, start_sequence, block_marker, end_sequence):
    with open(file_path, 'rb') as file:
        content = file.read()
        start_index = content.find(start_sequence)
        while start_index!= -1:
            sub_content = content[start_index:]
            end_marker_index = sub_content.find(end_sequence)
            if end_marker_index == -1:
                break

            extracted_data = sub_content[:end_marker_index + len(end_sequence)]
            if block_marker in extracted_data:
                new_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}_{len(os.listdir(directory_path))}.png"
                new_filepath = os.path.join(directory_path, new_filename)
                os.makedirs(os.path.dirname(new_filepath), exist_ok=True)
                with open(new_filepath, 'wb') as new_file:
                    new_file.write(extracted_data)
                print(f"Extracted content saved as: {new_filepath}")

            content = content[start_index + len(start_sequence):]
            start_index = content.find(start_sequence)

def main():
    directory_path = input("请输入要处理的文件夹路径: ")
    if not os.path.isdir(directory_path):
        print(f"错误: {directory_path} 不是一个有效的目录。")
        return

    start_sequence = b'\x89\x50\x4E\x47'
    block_marker = b'\x49\x48\x44\x52'
    end_sequence = b'\x00\x00\x00\x49\x45\x4E\x44\xAE\x42\x60\x82'

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if not file.endswith(('.py', '.png')):
                print(f"Processing file: {file_path}")
                extract_content(file_path, directory_path, start_sequence, block_marker, end_sequence)

if __name__ == "__main__":
    main()