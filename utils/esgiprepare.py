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
    # <пустая строка> \textbf{<текст>} <пустая строка> → \subsection{<текст>}
    patternTextbfSubsection = r'\n\s*\n\\textbf\{([^}]*)\}\n\s*\n'
    content = re.sub(patternTextbfSubsection, r'\n\n\\subsection{\1}\n\n', content)

    hl_pattern = r'\\hl\{(.*?)\}'
    content = re.sub(hl_pattern, r'\1', content, flags=re.DOTALL)
    
# Копирайты перед именами
    patternCopyRight = r'©[ ~](?:\d{4}\s)?'
    content = re.sub(patternCopyRight, '', content)

# т.д. и др. пишем с тонким пробелом
    patternTd = r'т\.[ ~]?([деп])\.'
    replacementTd = r'т.\,\1.'
    content = re.sub(patternTd, replacementTd, content)

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

# In Russian / In English → неразрывный пробел
    content = re.sub(r'In\sRussian', 'In~Russian', content)
    content = re.sub(r'In\sEnglish', 'In~English', content)

# Число + пробел/разрыв + "с." / "p." → заменить пробел на ~
    content = re.sub(r'(\d)[\s\n]+(с\.)', r'\1~\2', content)
    content = re.sub(r'(\d)[\s\n]+(p\.)', r'\1~\2', content)

# EDN: + пробел → заменить пробел на ~
    content = re.sub(r'EDN:\s+', 'EDN:~', content)

# Диапазоны чисел "5---10" → короткое тире "5–10"
    content = re.sub(r'(\d+)---(\d+)', r'\1–\2', content)

# DOI-ссылки → \url{...} (завершающая пунктуация остаётся снаружи)
    content = re.sub(r'(?<!\\url\{)(https://doi\.org/[^\s}]+)',
                     lambda m: '\\url{' + m.group(1).rstrip('.,;)]') + '}', content)

# \emph{<email>,} → \href{mailto:<email>}{\textit{<email>}},
    patternEmail = r'\\emph\{([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+),\}'
    content = re.sub(patternEmail, r'\\href{mailto:\1}{\\textit{\1}},', content)

# Дефис в длинных составных словах (обе части длиннее 3 символов) → "=
# Содержимое \url{...} защищено: перехватывается первой альтернативой и возвращается без изменений.
# Lookahead не поглощает слово после дефиса — корректно обрабатываются цепочки "слово-слово-слово"
    patternHyphen = re.compile(r'(\\url\{[^}]*\})|([А-Яа-яЁёA-Za-z]{4,})-(?=[А-Яа-яЁёA-Za-z]{4})')
    content = patternHyphen.sub(
        lambda m: m.group(1) if m.group(1) else m.group(2) + '"=',
        content)

# Кавычки ``...'' с кириллицей внутри → „...“
    content = re.sub(r"``(.*?[А-Яа-яЁё].*?)''", '„\\1“', content)

with open(texFile, 'w', encoding='utf-8', newline='\n') as openFile:
    openFile.write(content)
    openFile.close


