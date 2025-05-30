import os
import struct
from typing import List, Tuple, Optional

DDS_MAGIC = 0x20534444  # "DDS "的四字符代码
DDS_HEADER_SIZE = 124    # 标准DDS头大小（不含魔数）
DX10_HEADER_SIZE = 20    # DX10扩展头大小

DXGI_FORMAT = {
    0: "DXGI_FORMAT_UNKNOWN",
    1: "DXGI_FORMAT_R32G32B32A32_TYPELESS",
    2: "DXGI_FORMAT_R32G32B32A32_FLOAT",
    3: "DXGI_FORMAT_R32G32B32A32_UINT",
    4: "DXGI_FORMAT_R32G32B32A32_SINT",
    5: "DXGI_FORMAT_R32G32B32_TYPELESS",
    6: "DXGI_FORMAT_R32G32B32_FLOAT",
    7: "DXGI_FORMAT_R32G32B32_UINT",
    8: "DXGI_FORMAT_R32G32B32_SINT",
    9: "DXGI_FORMAT_R16G16B16A16_TYPELESS",
    10: "DXGI_FORMAT_R16G16B16A16_FLOAT",
    11: "DXGI_FORMAT_R16G16B16A16_UNORM",
    12: "DXGI_FORMAT_R16G16B16A16_UINT",
    13: "DXGI_FORMAT_R16G16B16A16_SNORM",
    14: "DXGI_FORMAT_R16G16B16A16_SINT",
    15: "DXGI_FORMAT_R32G32_TYPELESS",
    16: "DXGI_FORMAT_R32G32_FLOAT",
    17: "DXGI_FORMAT_R32G32_UINT",
    18: "DXGI_FORMAT_R32G32_SINT",
    19: "DXGI_FORMAT_R32G8X24_TYPELESS",
    20: "DXGI_FORMAT_D32_FLOAT_S8X24_UINT",
    21: "DXGI_FORMAT_R32_FLOAT_X8X24_TYPELESS",
    22: "DXGI_FORMAT_X32_TYPELESS_G8X24_UINT",
    23: "DXGI_FORMAT_R10G10B10A2_TYPELESS",
    24: "DXGI_FORMAT_R10G10B10A2_UNORM",
    25: "DXGI_FORMAT_R10G10B10A2_UINT",
    26: "DXGI_FORMAT_R11G11B10_FLOAT",
    27: "DXGI_FORMAT_R8G8B8A8_TYPELESS",
    28: "DXGI_FORMAT_R8G8B8A8_UNORM",
    29: "DXGI_FORMAT_R8G8B8A8_UNORM_SRGB",
    30: "DXGI_FORMAT_R8G8B8A8_UINT",
    31: "DXGI_FORMAT_R8G8B8A8_SNORM",
    32: "DXGI_FORMAT_R8G8B8A8_SINT",
    33: "DXGI_FORMAT_R16G16_TYPELESS",
    34: "DXGI_FORMAT_R16G16_FLOAT",
    35: "DXGI_FORMAT_R16G16_UNORM",
    36: "DXGI_FORMAT_R16G16_UINT",
    37: "DXGI_FORMAT_R16G16_SNORM",
    38: "DXGI_FORMAT_R16G16_SINT",
    39: "DXGI_FORMAT_R32_TYPELESS",
    40: "DXGI_FORMAT_D32_FLOAT",
    41: "DXGI_FORMAT_R32_FLOAT",
    42: "DXGI_FORMAT_R32_UINT",
    43: "DXGI_FORMAT_R32_SINT",
    44: "DXGI_FORMAT_R24G8_TYPELESS",
    45: "DXGI_FORMAT_D24_UNORM_S8_UINT",
    46: "DXGI_FORMAT_R24_UNORM_X8_TYPELESS",
    47: "DXGI_FORMAT_X24_TYPELESS_G8_UINT",
    48: "DXGI_FORMAT_R8G8_TYPELESS",
    49: "DXGI_FORMAT_R8G8_UNORM",
    50: "DXGI_FORMAT_R8G8_UINT",
    51: "DXGI_FORMAT_R8G8_SNORM",
    52: "DXGI_FORMAT_R8G8_SINT",
    53: "DXGI_FORMAT_R16_TYPELESS",
    54: "DXGI_FORMAT_R16_FLOAT",
    55: "DXGI_FORMAT_D16_UNORM",
    56: "DXGI_FORMAT_R16_UNORM",
    57: "DXGI_FORMAT_R16_UINT",
    58: "DXGI_FORMAT_R16_SNORM",
    59: "DXGI_FORMAT_R16_SINT",
    60: "DXGI_FORMAT_R8_TYPELESS",
    61: "DXGI_FORMAT_R8_UNORM",
    62: "DXGI_FORMAT_R8_UINT",
    63: "DXGI_FORMAT_R8_SNORM",
    64: "DXGI_FORMAT_R8_SINT",
    65: "DXGI_FORMAT_A8_UNORM",
    66: "DXGI_FORMAT_R1_UNORM",
    67: "DXGI_FORMAT_R9G9B9E5_SHAREDEXP",
    68: "DXGI_FORMAT_R8G8_B8G8_UNORM",
    69: "DXGI_FORMAT_G8R8_G8B8_UNORM",
    70: "DXGI_FORMAT_BC1_TYPELESS",
    71: "DXGI_FORMAT_BC1_UNORM",
    72: "DXGI_FORMAT_BC1_UNORM_SRGB",
    73: "DXGI_FORMAT_BC2_TYPELESS",
    74: "DXGI_FORMAT_BC2_UNORM",
    75: "DXGI_FORMAT_BC2_UNORM_SRGB",
    76: "DXGI_FORMAT_BC3_TYPELESS",
    77: "DXGI_FORMAT_BC3_UNORM",
    78: "DXGI_FORMAT_BC3_UNORM_SRGB",
    79: "DXGI_FORMAT_BC4_TYPELESS",
    80: "DXGI_FORMAT_BC4_UNORM",
    81: "DXGI_FORMAT_BC4_SNORM",
    82: "DXGI_FORMAT_BC5_TYPELESS",
    83: "DXGI_FORMAT_BC5_UNORM",
    84: "DXGI_FORMAT_BC5_SNORM",
    85: "DXGI_FORMAT_B5G6R5_UNORM",
    86: "DXGI_FORMAT_B5G5R5A1_UNORM",
    87: "DXGI_FORMAT_B8G8R8A8_UNORM",
    88: "DXGI_FORMAT_B8G8R8X8_UNORM",
    89: "DXGI_FORMAT_R10G10B10_XR_BIAS_A2_UNORM",
    90: "DXGI_FORMAT_B8G8R8A8_TYPELESS",
    91: "DXGI_FORMAT_B8G8R8A8_UNORM_SRGB",
    92: "DXGI_FORMAT_B8G8R8X8_TYPELESS",
    93: "DXGI_FORMAT_B8G8R8X8_UNORM_SRGB",
    94: "DXGI_FORMAT_BC6H_TYPELESS",
    95: "DXGI_FORMAT_BC6H_UF16",
    96: "DXGI_FORMAT_BC6H_SF16",
    97: "DXGI_FORMAT_BC7_TYPELESS",
    98: "DXGI_FORMAT_BC7_UNORM",
    99: "DXGI_FORMAT_BC7_UNORM_SRGB",
    100: "DXGI_FORMAT_AYUV",
    101: "DXGI_FORMAT_Y410",
    102: "DXGI_FORMAT_Y416",
    103: "DXGI_FORMAT_NV12",
    104: "DXGI_FORMAT_P010",
    105: "DXGI_FORMAT_P016",
    106: "DXGI_FORMAT_420_OPAQUE",
    107: "DXGI_FORMAT_YUY2",
    108: "DXGI_FORMAT_Y210",
    109: "DXGI_FORMAT_Y216",
    110: "DXGI_FORMAT_NV11",
    111: "DXGI_FORMAT_AI44",
    112: "DXGI_FORMAT_IA44",
    113: "DXGI_FORMAT_P8",
    114: "DXGI_FORMAT_A8P8",
    115: "DXGI_FORMAT_B4G4R4A4_UNORM",
    130: "DXGI_FORMAT_P208",
    131: "DXGI_FORMAT_V208",
    132: "DXGI_FORMAT_V408",
    0xffffffff: "DXGI_FORMAT_FORCE_UINT"
}

class DDSHeader:
    def __init__(self, data: bytes):
        self.size = struct.unpack_from('<I', data, 4)[0]
        self.flags = struct.unpack_from('<I', data, 8)[0]
        self.height = struct.unpack_from('<I', data, 12)[0]
        self.width = struct.unpack_from('<I', data, 16)[0]
        self.pitch_or_linear_size = struct.unpack_from('<I', data, 20)[0]
        self.depth = struct.unpack_from('<I', data, 24)[0]
        self.mipmap_count = struct.unpack_from('<I', data, 28)[0]
        self.reserved1 = struct.unpack_from('<11I', data, 32)

        pf_offset = 76
        self.pf_size = struct.unpack_from('<I', data, pf_offset)[0]
        self.pf_flags = struct.unpack_from('<I', data, pf_offset + 4)[0]
        self.pf_fourcc = struct.unpack_from('<4s', data, pf_offset + 8)[0].decode('ascii').strip('\x00')
        self.pf_bitcount = struct.unpack_from('<I', data, pf_offset + 12)[0]
        self.pf_rmask = struct.unpack_from('<I', data, pf_offset + 16)[0]
        self.pf_gmask = struct.unpack_from('<I', data, pf_offset + 20)[0]
        self.pf_bmask = struct.unpack_from('<I', data, pf_offset + 24)[0]
        self.pf_amask = struct.unpack_from('<I', data, pf_offset + 28)[0]

        caps_offset = 108
        self.caps1 = struct.unpack_from('<I', data, caps_offset)[0]
        self.caps2 = struct.unpack_from('<I', data, caps_offset + 4)[0]
        self.caps3 = struct.unpack_from('<I', data, caps_offset + 8)[0]
        self.caps4 = struct.unpack_from('<I', data, caps_offset + 12)[0]
        self.reserved2 = struct.unpack_from('<I', data, caps_offset + 16)[0]

    def is_valid(self) -> bool:
        return (self.size == DDS_HEADER_SIZE and
                (self.flags & 0x1007) != 0 and  # DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT
                self.width > 0 and self.height > 0 and
                self.pf_size == 32)

    def has_dx10_extension(self) -> bool:
        return self.pf_fourcc == 'DX10'

    def get_dxgi_format(self, dx10_data: bytes) -> str:
        if not self.has_dx10_extension():
            return self.pf_fourcc
        try:
            dxgi_format = struct.unpack_from('<I', dx10_data, 0)[0]
            return DXGI_FORMAT.get(dxgi_format, f"UNKNOWN({dxgi_format})")
        except struct.error:
            return "UNKNOWN"

    def calculate_data_size(self) -> int:
        if self.flags & 0x80000:  # DDSD_LINEARSIZE
            return self.pitch_or_linear_size

        if self.pf_fourcc in ['DXT1', 'BC1', 'ATI1']:
            block_size = 8
        elif self.pf_fourcc in ['DXT3', 'DXT5', 'BC2', 'BC3', 'ATI2']:
            block_size = 16
        elif self.pf_fourcc in ['BC4U', 'BC4S']:
            block_size = 4
        elif self.pf_fourcc in ['BC5U', 'BC5S']:
            block_size = 8
        else:
            block_size = max(1, (self.pf_bitcount + 7) // 8) * 4

        total_size = 0
        w, h = self.width, self.height
        for _ in range(max(1, self.mipmap_count)):
            block_w = max(1, (w + 3) // 4)
            block_h = max(1, (h + 3) // 4)
            total_size += block_w * block_h * block_size
            w = max(1, w // 2)
            h = max(1, h // 2)

        return total_size

class DDSProcessor:
    def __init__(self):
        self.extracted_count = 0
        self.skipped_files = []

    def extract_from_file(self, file_path: str, output_dir: str) -> int:
        try:
            with open(file_path, 'rb') as f:
                data = f.read()

            extracted = 0
            offset = 0

            while offset <= len(data) - 128:
                dds_pos = data.find(struct.pack('<I', DDS_MAGIC), offset)
                if dds_pos == -1:
                    break

                header_data = data[dds_pos:dds_pos + 128]
                header = DDSHeader(header_data)

                if not header.is_valid():
                    offset = dds_pos + 4
                    continue

                has_dx10 = header.has_dx10_extension()
                dx10_size = DX10_HEADER_SIZE if has_dx10 else 0

                data_size = header.calculate_data_size()
                total_size = 4 + DDS_HEADER_SIZE + dx10_size + data_size

                if dds_pos + total_size > len(data):
                    offset = dds_pos + 4
                    continue

                dx10_data = data[dds_pos + 128:dds_pos + 128 + dx10_size] if has_dx10 else b''
                format_str = header.get_dxgi_format(dx10_data)

                output_path = os.path.join(output_dir, f"extracted_{self.extracted_count:04d}.dds")

                with open(output_path, 'wb') as out_file:
                    out_file.write(data[dds_pos:dds_pos + total_size])

                print(f"[{self.extracted_count:04d}] 从 {file_path} 提取到 {output_path}")
                print(f"      尺寸: {header.width}x{header.height}, 格式: {format_str}")

                extracted += 1
                self.extracted_count += 1
                offset = dds_pos + total_size

            return extracted

        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
            self.skipped_files.append(file_path)
            return 0

    def process_directory(self, input_dir: str, output_dir: str) -> Tuple[int, int, int]:
        total_files = 0
        processed_files = 0
        total_extracted = 0

        for root, _, files in os.walk(input_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                total_files += 1

                if not os.path.isfile(file_path):
                    continue

                print(f"\n处理文件: {file_path}")
                extracted = self.extract_from_file(file_path, output_dir)

                if extracted > 0:
                    processed_files += 1
                    total_extracted += extracted

        return total_files, processed_files, total_extracted

def main():
    print("=" * 50)
    print(" DDS图像提取器")
    print("=" * 50)

    input_dir = input("请输入要处理的文件夹路径: ").strip()

    if not os.path.isdir(input_dir):
        print(f"错误: {input_dir} 不是一个有效的目录。")
        return

    output_dir = os.path.join(input_dir, "extracted_dds")
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")

    print("\n开始处理...\n")

    processor = DDSProcessor()
    total_files, processed_files, total_extracted = processor.process_directory(input_dir, output_dir)

    print("\n" + "=" * 50)
    print(f"处理完成!")
    print(f"总文件数: {total_files}")
    print(f"包含DDS的文件: {processed_files}")
    print(f"提取的DDS图像总数: {total_extracted}")
    print(f"提取的文件保存在: {output_dir}")

    if processor.skipped_files:
        print(f"\n跳过的文件数: {len(processor.skipped_files)}")
        for file in processor.skipped_files[:5]:
            print(f"  - {file}")
        if len(processor.skipped_files) > 5:
            print(f"  - ... 和其他 {len(processor.skipped_files) - 5} 个文件")

    print("=" * 50)

if __name__ == "__main__":
    main()
