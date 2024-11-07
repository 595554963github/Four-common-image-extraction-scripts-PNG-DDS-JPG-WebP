import os
import struct

def extract_webp_data(file_content):
    riff_header = b'\x52\x49\x46\x46'
    webp_header = b'\x57\x45\x42\x50\x56\x50\x38\x58'

    webp_data_start = file_content.find(riff_header)
    while webp_data_start != -1:
        file_size = struct.unpack('<I', file_content[webp_data_start + 4:webp_data_start + 8])[0]
        # 确保file_size是4字节对齐
        file_size = (file_size + 1) & ~1
        if file_content[webp_data_start + 8:webp_data_start + 16] == webp_header:
            webp_data = file_content[webp_data_start:webp_data_start + file_size + 8]
            yield webp_data
        webp_data_start = file_content.find(riff_header, webp_data_start + file_size + 8)

def extract_webps_from_file(file_path):
    with open(file_path, 'rb') as file:
        file_content = file.read()

    webp_data_generator = extract_webp_data(file_content)
    count = 0
    for webp_data in webp_data_generator:
        base_filename, _ = os.path.splitext(os.path.basename(file_path))
        extracted_filename = f"{base_filename}_{count}.webp"
        extracted_path = os.path.join(os.path.dirname(file_path), extracted_filename)
        os.makedirs(os.path.dirname(extracted_path), exist_ok=True)
        with open(extracted_path, 'wb') as output_file:
            output_file.write(webp_data)
        print(f"Extracted content saved as: {extracted_path}")
        count += 1

def extract_webps(directory_path):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(('.py', '.webp')):
                continue
            file_path = os.path.join(root, file)
            extract_webps_from_file(file_path)

def main():
    directory_path = input("请输入要处理的文件夹路径: ")
    if not os.path.isdir(directory_path):
        print(f"错误: {directory_path} 不是一个有效的目录。")
        return

    extract_webps(directory_path)
    print("WebP 文件提取完成。")

if __name__ == "__main__":
    main()
