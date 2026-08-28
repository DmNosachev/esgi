#!/usr/bin/python
import argparse
import subprocess
import sys
import os
import glob
import re

parser = argparse.ArgumentParser(description="Process tex file")
parser.add_argument("-f", "--file", type=str, help="File to process")
args = parser.parse_args()

texFile = args.file

with open(texFile, 'r', encoding='utf-8') as openFile:
    content = openFile.read()

# Предварительная очистка
    # Символ U+2011 — неразрывный дефис
    content = content.replace('\u2011', '-')
    content = content.replace('\\begin{quote}', '')
    content = content.replace('\\end{quote}', '')
    content = content.replace('\\def\\labelenumi{\\arabic{enumi}.}', '')
    content = content.replace('\\textbf{Введение}', '\\subsection{Введение}')
    content = content.replace('\\textbf{Заключение}', '\\subsection{Заключение}')
    content = content.replace('\\textbf{Выводы}', '\\subsection{Выводы}')

    hl_pattern = r'\\hl\{(.*?)\}'
    content = re.sub(hl_pattern, r'\1', content, flags=re.DOTALL)
    
# Копирайты перед именами
    patternCopyRight = r'©[ ~](?:\d{4}\s)?'
    content = re.sub(patternCopyRight, '', content)

# т.д. и др. пишем с тонким пробелом
    patternTd = r'т\.[ ~]?([деп])\.'
    replacementTd = r'т.\,\1.'
    content = re.sub(patternTd, replacementTd, content)

# endash в диапазонах
    patternEndash = r'(\d+)-(\d+)'
    replacementEndash = r'\1–\2'
    content = re.sub(patternEndash, replacementEndash, content)

# 1. №, ч., п., ст. + пробел/разрыв + число → заменить пробел на ~
# Ищем: (№|ч\.|п\.|ст\.)[\s\n]+(\d)
# Заменяем на: \1~\2
    pattern1 = r'(№|ч\.|п\.|ст\.)[\s\n]+(\d)'
    content = re.sub(pattern1, r'\1~\2', content)

# 2. Число + пробел/разрыв + (г\.|гг\.|тыс|млн|млрд|трлн) → заменить пробел на ~
# Ищем: (\d)[\s\n]+(г\.|гг\.|тыс|млн|млрд|трлн)
# Заменяем на: \1~\2
    pattern2 = r'(\d)[\s\n]+(г\.|гг\.|тыс|млн|млрд|трлн)'
    content = re.sub(pattern2, r'\1~\2', content)

# 3. Римские цифры + пробел/разрыв + «в.» → заменить пробел на ~
# Римские цифры: I, V, X, L, C, D, M (в любом регистре, возможно несколько)
# Ищем: ([IVXLCDMivxlcdm]+)[\s\n]+в\.
# Заменяем на: \1~в.
    pattern3 = r'([IVXLCDMivxlcdm]+)[\s\n]+в\.'
    content = re.sub(pattern3, r'\1~в.', content)

# 4. Заменить пробелы/разрывы в "тыс руб.", "млн руб." и т.п. на ~
# Ищем: (тыс|млн|млрд|трлн)[\s\n]+руб\.
# Заменяем на: \1~руб.
    pattern4 = r'(тыс|млн|млрд|трлн)[\s\n]+руб\.'
    content = re.sub(pattern4, r'\1~руб.', content)

    pattern6 = r'[\s]+-{2,3}[\s]+'
    content = re.sub(pattern6, '~— ', content)

    pattern7 = r'[\s]+не[\s]+'
    content = re.sub(pattern7, ' не\u00A0', content)

with open(texFile, 'w', encoding='utf-8', newline='\n') as openFile:
    openFile.write(content)
    openFile.close


