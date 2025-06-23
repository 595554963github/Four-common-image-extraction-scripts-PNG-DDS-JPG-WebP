import os
import struct

def extract_content(file_path, directory_path, start_sequence, block_marker, end_sequence):
    buffer_size = 8192 
    start_seq_len = len(start_sequence)
    end_seq_len = len(end_sequence)
    
    with open(file_path, 'rb') as file:
        leftover = b''
        current_png = None
        found_start = False
        
        while True:
            chunk = file.read(buffer_size)
            if not chunk: 
                break
                
            data = leftover + chunk
            
            if not found_start:
                start_index = data.find(start_sequence)
                if start_index != -1:
                    found_start = True
                    current_png = data[start_index:]
                    leftover = b''
                else:
                    leftover = data[-start_seq_len + 1:] if len(data) >= start_seq_len else data
            else:
                current_png += chunk
                
                end_index = current_png.find(end_sequence)
                if end_index != -1:
                    end_index += end_seq_len
                    extracted_data = current_png[:end_index]
                    
                    if block_marker in extracted_data:
                        new_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}_{len(os.listdir(directory_path))}.png"
                        new_filepath = os.path.join(directory_path, new_filename)
                        os.makedirs(os.path.dirname(new_filepath), exist_ok=True)
                        with open(new_filepath, 'wb') as new_file:
                            new_file.write(extracted_data)
                        print(f"提取的内容另存为: {new_filepath}")
                    
                    found_start = False
                    leftover = current_png[end_index:]
                    current_png = None

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
                print(f"处理文件: {file_path}")
                extract_content(file_path, directory_path, start_sequence, block_marker, end_sequence)

if __name__ == "__main__":
    main()
