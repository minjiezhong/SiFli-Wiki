import re
import os
import sys
from tqdm import tqdm
def load_translation_dict(tr_file):
    """
    加载.tr字典文件，构建中英对照字典
    格式要求：每行 str_cn:中文内容,str_en:英文内容
    """
    trans_dict = {}
    with open(tr_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # 使用正则表达式严格匹配
            match = re.match(r'str_cn:(.+?),str_en:(.+)$', line)
            if match:
                cn = match.group(1).strip()
                en = match.group(2).strip()
                trans_dict[cn] = en  # 后者覆盖前者
            else:
                print(f"格式错误行: {line[:50]}...")
    return trans_dict

def replace_with_dict(input_file, output_file, trans_dict):
    """
    增强版替换函数，遇到{toctree}即停止后续替换
    """
    pattern = re.compile(
        '|'.join(sorted([re.escape(cn) for cn in trans_dict.keys()], 
                        key=lambda x: -len(x)))
    )
    
    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8') as f_out:
        
        skip_replacement = False  # 替换控制开关
        for line in f_in:
            if skip_replacement:
                f_out.write(line)
                continue
            
            # 检测toctree指令
            toc_match = re.search(r'\{toctree\}', line)
            if toc_match:
                # 分割指令前后内容
                pre_toc = line[:toc_match.start()]
                post_toc = line[toc_match.start():]
                
                # 仅替换指令前的内容
                processed_pre = pattern.sub(
                    lambda m: trans_dict.get(m.group(), m.group()), 
                    pre_toc
                )
                f_out.write(processed_pre + post_toc)
                skip_replacement = True  # 后续内容保持原样
            else:
                processed_line = pattern.sub(
                    lambda m: trans_dict.get(m.group(), m.group()), 
                    line
                )
                f_out.write(processed_line)



def find_tr_files(root_dir):
    """构建.md以及.rst文件与.tr文件的映射关系"""
    file_pairs = []
    for foldername, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.md') or filename.endswith('.rst'):
                md_path = os.path.join(foldername, filename)
                tr_path = os.path.splitext(md_path)[0] + '.tr'
                if os.path.exists(tr_path):
                    file_pairs.append((md_path, tr_path))
    return file_pairs

def process_all_files(input_root, output_root, file_pairs):
    """批量处理所有匹配的文件"""
    for md_path, tr_path in tqdm(file_pairs, desc="处理进度"):
        # 生成输出路径
        relative_path = os.path.relpath(md_path, input_root)
        output_path = os.path.join(output_root, relative_path)
        
        # 创建输出目录
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 执行单个文件处理
        try:
            trans_dict = load_translation_dict(tr_path)
            replace_with_dict(md_path, output_path, trans_dict)
        except Exception as e:
            print(f"\n处理文件失败: {md_path}")
            print(f"错误信息: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使用方法: python batch_replace.py [输入目录] [输出目录]")
        print("示例: python batch_replace.py ./docs ./translated_docs")
        sys.exit(1)

    input_root = sys.argv[1]
    output_root = sys.argv[2]

    print("正在扫描目录结构...")
    file_pairs = find_tr_files(input_root)
    print(f"找到 {len(file_pairs)} 对需要处理的文件")

    if len(file_pairs) > 0:
        process_all_files(input_root, output_root, file_pairs)
        print(f"\n处理完成！结果保存在: {output_root}")
    else:
        print("未找到需要处理的.md文件")
    
