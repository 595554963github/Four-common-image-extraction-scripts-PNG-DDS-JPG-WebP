import os
import sys
import concurrent.futures
from typing import List, Optional, Tuple
import time

def parse_sequence(sequence_input: str) -> bytes:
    if '*' in sequence_input:
        parts = sequence_input.split('*')
        byte_value = bytes.fromhex(parts[0].replace(' ', ''))
        repeat_count = int(parts[1])
        return byte_value * repeat_count
    else:
        return bytes.fromhex(sequence_input.replace(' ', ''))

def find_sequence(content: bytes, sequence: bytes, start_index: int) -> int:
    return content.find(sequence, start_index)

def is_valid_jpg(data: bytes) -> bool:
    if len(data) < 10:
        return False
    if not data.startswith(b'\xFF\xD8\xFF'):
        return False
    return (b'JFIF' in data[:20] or b'Exif' in data[:32]) and b'\xFF\xD9' in data

def extract_jpgs_from_file(file_path: str, start_sequence: bytes, end_sequence: bytes, 
                          output_dir: str, progress_callback=None) -> int:
    try:
        if os.path.getsize(file_path) == 0:
            if progress_callback:
                progress_callback(f"跳过空文件: {file_path}")
            return 0
            
        base_filename = os.path.basename(file_path)
        filename_without_ext = os.path.splitext(base_filename)[0]
        os.makedirs(output_dir, exist_ok=True)
        
        extracted_count = 0
        buffer_size = 8 * 1024 * 1024
        remaining_data = b''
        
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(buffer_size)
                if not chunk:
                    break
                    
                current_data = remaining_data + chunk
                start_index = 0
                
                while True:
                    jpg_start = find_sequence(current_data, start_sequence, start_index)
                    if jpg_start == -1:
                        break
                        
                    jpg_end = find_sequence(current_data, end_sequence, jpg_start + len(start_sequence))
                    if jpg_end == -1:
                        break
                        
                    jpg_end += len(end_sequence)
                    jpg_data = current_data[jpg_start:jpg_end]
                    
                    if is_valid_jpg(jpg_data):
                        output_filename = f"{filename_without_ext}_{extracted_count}.jpg"
                        output_path = os.path.join(output_dir, output_filename)
                        
                        with open(output_path, 'wb') as out_file:
                            out_file.write(jpg_data)
                            
                        extracted_count += 1
                        if progress_callback:
                            progress_callback(f"已提取: {output_path}")
                    
                    start_index = jpg_end
                
                remaining_data = current_data[start_index:]
        
        if progress_callback:
            progress_callback(f"从 {file_path} 提取了 {extracted_count} 个JPG")
            
        return extracted_count
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"处理文件 {file_path} 时出错: {str(e)}")
        return 0

def process_directory(directory_path: str, start_sequence: bytes, end_sequence: bytes, 
                     output_base_dir: str, max_workers: int = 5, progress_callback=None) -> int:
    files_to_process = []
    
    for root, _, files in os.walk(directory_path):
        for file in files:
            if not file.endswith('.py') and 'disabled' not in file.lower():
                files_to_process.append(os.path.join(root, file))
    
    if progress_callback:
        progress_callback(f"发现 {len(files_to_process)} 个文件需要处理")
    
    total_extracted = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(
                extract_jpgs_from_file, 
                file_path, 
                start_sequence, 
                end_sequence,
                os.path.join(output_base_dir, os.path.relpath(os.path.dirname(file_path), directory_path)),
                progress_callback
            ): file_path for file_path in files_to_process
        }
        
        for future in concurrent.futures.as_completed(future_to_file):
            try:
                total_extracted += future.result()
            except Exception as e:
                if progress_callback:
                    progress_callback(f"处理文件时发生异常: {str(e)}")
    
    return total_extracted

def progress_log(message: str):
    print(message)

def main():
    directory_path = input("请输入要处理的文件夹路径: ")
    if not os.path.isdir(directory_path):
        print(f"错误: {directory_path} 不是一个有效的目录。")
        sys.exit(1)
    
    start_sequence = parse_sequence("FF D8 FF E0")
    end_sequence = parse_sequence("FF D9")
    
    print("开始提取JPG文件...")
    output_base_dir = os.path.join(directory_path, "extracted_jpgs")
    start_time = time.time()
    
    try:
        total_jpgs = process_directory(directory_path, start_sequence, end_sequence, 
                                      output_base_dir, progress_callback=progress_log)
        elapsed_time = time.time() - start_time
        
        print(f"提取完成! 共找到 {total_jpgs} 个JPG文件")
        print(f"耗时: {elapsed_time:.2f} 秒")
        print(f"提取的文件保存在: {output_base_dir}")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()
