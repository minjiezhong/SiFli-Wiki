#!/usr/bin/env python3
"""
自动翻译脚本
用于检测文件变更并进行中英文互译
"""

import os
import re
import sys
import subprocess
import argparse
from pathlib import Path
from openai import OpenAI

class AutoTranslator:
    def __init__(self, api_key=None, base_url="https://api.siliconflow.cn/v1"):
        """初始化翻译器"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("需要设置OPENAI_API_KEY环境变量或传入API密钥")
        
        self.client = OpenAI(api_key=self.api_key, base_url=base_url)
        self.model = "Qwen/Qwen2.5-72B-Instruct"
        
    def get_system_prompt(self, target_lang):
        """获取翻译系统提示词"""
        if target_lang == "en":
            return """你是一个专业的技术文档翻译专家。请将中文技术文档翻译成英文，要求：

1. 保持原文档的所有格式，包括：
   - Markdown格式（标题、列表、代码块、链接等）
   - reStructuredText格式（指令、标题、代码块等）
   - 缩进和空行
   - 特殊符号和标记

2. 翻译准确性：
   - 保持技术术语的准确性
   - 芯片型号、引脚名称等保持原样不翻译
   - API函数名、变量名、文件名等保持原样
   - 代码块内容完全不变

3. 语言风格：
   - 使用专业、清晰的技术英语
   - 保持原文的语气和风格
   - 确保翻译自然流畅

4. 特殊处理：
   - 如果遇到已经是英文的内容，保持原样
   - 中英文混合的句子要自然翻译
   - 保留所有的链接、图片引用等

请直接返回翻译后的内容，不要添加任何解释或说明。"""
        else:
            return """你是一个专业的技术文档翻译专家。请将英文技术文档翻译成中文，要求：

1. 保持原文档的所有格式，包括：
   - Markdown格式（标题、列表、代码块、链接等）
   - reStructuredText格式（指令、标题、代码块等）
   - 缩进和空行
   - 特殊符号和标记

2. 翻译准确性：
   - 保持技术术语的准确性
   - 芯片型号、引脚名称等保持原样不翻译
   - API函数名、变量名、文件名等保持原样
   - 代码块内容完全不变

3. 语言风格：
   - 使用专业、清晰的中文表达
   - 保持原文的语气和风格
   - 确保翻译自然流畅

4. 特殊处理：
   - 如果遇到已经是中文的内容，保持原样
   - 中英文混合的句子要自然翻译
   - 保留所有的链接、图片引用等

请直接返回翻译后的内容，不要添加任何解释或说明。"""

    def translate_content(self, content, target_lang):
        """翻译内容"""
        if not content.strip():
            return content
            
        system_prompt = self.get_system_prompt(target_lang)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请翻译以下内容：\n\n{content}"}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"翻译失败: {str(e)}")
            return content

    def get_changed_files(self, branch1="HEAD", branch2="HEAD~1"):
        """获取两个提交之间发生变更的文件"""
        try:
            # 获取变更的文件列表
            result = subprocess.run(
                ["git", "diff", "--name-only", branch1, branch2],
                capture_output=True,
                text=True,
                check=True
            )
            files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # 处理source目录下的.rst和.md文件
            source_files = []
            for file in files:
                if file.startswith('source/') and (file.endswith('.rst') or file.endswith('.md')):
                    source_files.append(file)
            
            return source_files
        except subprocess.CalledProcessError as e:
            print(f"获取变更文件失败: {e}")
            return []

    def translate_file(self, file_path, target_lang):
        """翻译单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"正在翻译文件: {file_path}")
            translated_content = self.translate_content(content, target_lang)
            
            return translated_content
        except Exception as e:
            print(f"翻译文件 {file_path} 失败: {e}")
            return None

    def translate_changed_files(self, source_branch, target_branch, target_lang):
        """翻译变更的文件并准备目标分支的内容"""
        print(f"检测 {source_branch} 分支的变更文件...")
        
        # 获取当前分支
        current_branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        
        try:
            # 切换到源分支
            subprocess.run(["git", "checkout", source_branch], check=True)
            
            # 获取变更的文件
            changed_files = self.get_changed_files()
            
            if not changed_files:
                print("没有发现需要翻译的文件变更")
                return []
            
            print(f"发现 {len(changed_files)} 个变更的文件:")
            for file in changed_files:
                print(f"  - {file}")
            
            # 翻译文件
            translated_files = []
            for file_path in changed_files:
                if os.path.exists(file_path):
                    translated_content = self.translate_file(file_path, target_lang)
                    if translated_content:
                        translated_files.append({
                            'path': file_path,
                            'content': translated_content
                        })
            
            return translated_files
            
        finally:
            # 恢复到原分支
            subprocess.run(["git", "checkout", current_branch], check=False)

    def apply_translations_to_branch(self, translated_files, target_branch):
        """将翻译结果应用到目标分支"""
        if not translated_files:
            return False
            
        try:
            # 切换到目标分支
            subprocess.run(["git", "checkout", target_branch], check=True)
            
            # 创建新的分支用于PR
            pr_branch = f"auto-translation-{target_branch}"
            subprocess.run(["git", "checkout", "-b", pr_branch], check=True)
            
            # 应用翻译
            for file_info in translated_files:
                file_path = file_info['path']
                content = file_info['content']
                
                # 确保目录存在
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # 写入翻译后的内容
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"已更新文件: {file_path}")
            
            # 提交更改
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run([
                "git", "commit", "-m", 
                f"Auto-translation: Update {len(translated_files)} files"
            ], check=True)
            
            # 推送分支
            subprocess.run(["git", "push", "origin", pr_branch], check=True)
            
            print(f"已创建并推送分支: {pr_branch}")
            return pr_branch
            
        except subprocess.CalledProcessError as e:
            print(f"应用翻译到分支失败: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='自动翻译工具')
    parser.add_argument('--source-branch', default='main', help='源分支（默认：main）')
    parser.add_argument('--target-branch', default='en', help='目标分支（默认：en）')
    parser.add_argument('--target-lang', default='en', help='目标语言（en/zh）')
    parser.add_argument('--api-key', help='OpenAI API密钥')
    
    args = parser.parse_args()
    
    try:
        translator = AutoTranslator(api_key=args.api_key)
        
        # 翻译变更的文件
        translated_files = translator.translate_changed_files(
            args.source_branch, 
            args.target_branch, 
            args.target_lang
        )
        
        if translated_files:
            # 应用翻译到目标分支
            pr_branch = translator.apply_translations_to_branch(
                translated_files, 
                args.target_branch
            )
            
            if pr_branch:
                print(f"\n翻译完成！已创建分支 {pr_branch}")
                print("请在GitHub上创建PR将更改合并到目标分支")
            else:
                print("应用翻译失败")
        else:
            print("没有需要翻译的文件")
            
    except Exception as e:
        print(f"翻译过程出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
