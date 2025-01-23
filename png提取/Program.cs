using System;
using System.IO;
using System.Linq;

namespace PngExtractor
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("请输入要处理的文件夹路径: ");
            string? inputPath = Console.ReadLine();

            string dirPath = inputPath ?? "";
            if (!Directory.Exists(dirPath))
            {
                Console.WriteLine($"错误: {dirPath} 不是一个有效的目录。");
                return;
            }

            byte[] startSequence = { 0x89, 0x50, 0x4E, 0x47 };
            byte[] blockMarker = { 0x49, 0x48, 0x44, 0x52 };
            byte[] endSequence = { 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82 };

            foreach (string file in Directory.GetFiles(dirPath, "*.*", SearchOption.AllDirectories))
            {
                Console.WriteLine($"Processing file: {file}");
                byte[] content = File.ReadAllBytes(file);

                bool found = false;
                int start_index = 0;

                while (!found)
                {
                    start_index = FindSequence(content, startSequence, start_index);
                    if (start_index == -1)
                    {
                        break;
                    }

                    int end_index = FindSequence(content, endSequence, start_index);
                    if (end_index == -1)
                    {
                        break;
                    }

                    byte[] extracted = content.Skip(start_index).Take(end_index - start_index + endSequence.Length).ToArray();
                    if (ContainsSequence(extracted, blockMarker))
                    {
                        ExtractPng(file, dirPath, startSequence, blockMarker, endSequence);
                        found = true;
                    }

                    start_index += startSequence.Length;
                }
            }
        }

        static void ExtractPng(string filePath, string directoryPath, byte[] startSeq, byte[] blockMarker, byte[] endSeq)
        {
            byte[] content = File.ReadAllBytes(filePath);
            int start_index = 0;
            int count = 0;

            while (true)
            {
                start_index = FindSequence(content, startSeq, start_index);
                if (start_index == -1)
                {
                    break;
                }

                int end_index = FindSequence(content, endSeq, start_index);
                if (end_index == -1)
                {
                    break;
                }

                byte[] extracted = content.Skip(start_index).Take(end_index - start_index + endSeq.Length).ToArray();

                if (ContainsSequence(extracted, blockMarker))
                {
                    string fileExtension = ".png";
                    string baseName = Path.GetFileNameWithoutExtension(filePath);
                    string newFileName = $"{baseName}_{count}{fileExtension}";

                    string newFilePath = Path.Combine(directoryPath, newFileName);
                    File.WriteAllBytes(newFilePath, extracted);
                    Console.WriteLine($"Extracted and saved {newFileName}");
                    count++;
                }

                start_index += startSeq.Length;
            }
        }

        static int FindSequence(byte[] content, byte[] sequence, int startIndex)
        {
            if (startIndex < 0 || startIndex >= content.Length)
            {
                return -1;
            }

            for (int i = startIndex; i <= content.Length - sequence.Length; i++)
            {
                bool found = true;
                for (int j = 0; j < sequence.Length; j++)
                {
                    if (content[i + j] != sequence[j])
                    {
                        found = false;
                        break;
                    }
                }
                if (found)
                {
                    return i;
                }
            }
            return -1;
        }

        static bool ContainsSequence(byte[] content, byte[] sequence)
        {
            for (int i = 0; i <= content.Length - sequence.Length; i++)
            {
                bool found = true;
                for (int j = 0; j < sequence.Length; j++)
                {
                    if (content[i + j] != sequence[j])
                    {
                        found = false;
                        break;
                    }
                }
                if (found)
                {
                    return true;
                }
            }
            return false;
        }
    }
}