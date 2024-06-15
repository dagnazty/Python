import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import re
import random
import string
import os
import base64

def generate_random_name():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def remove_comments_and_whitespace(script_content, remove_comments, remove_whitespace):
    if remove_comments:
        script_content = re.sub(r'^\s*#.*$', '', script_content, flags=re.MULTILINE)
    if remove_whitespace:
        script_content = re.sub(r'^\s*\n', '', script_content, flags=re.MULTILINE)
    return script_content

def detect_blocks(lines):
    block_ranges = []
    block_start = None
    open_braces = 0

    for i, line in enumerate(lines):
        stripped_line = line.strip()
        open_braces += stripped_line.count('{')
        open_braces -= stripped_line.count('}')

        if '{' in stripped_line:
            if block_start is None:
                block_start = i
        if '}' in stripped_line:
            if open_braces == 0 and block_start is not None:
                block_ranges.append((block_start, i))
                block_start = None

    return block_ranges

def insert_control_flow_obfuscation(script_content):
    lines = script_content.splitlines()
    block_ranges = detect_blocks(lines)
    obfuscated_lines = []
    i = 0

    while i < len(lines):
        if any(start <= i <= end for start, end in block_ranges):
            start, end = next((start, end) for start, end in block_ranges if start <= i <= end)
            block_lines = lines[start:end+1]
            indent = re.match(r'^\s*', lines[start]).group(0)
            obfuscated_lines.append(f"{indent}if ($true) {{")
            obfuscated_lines.extend([f"{indent}    {l}" for l in block_lines])
            obfuscated_lines.append(f"{indent}}}")
            obfuscated_lines.append(f"{indent}try {{")
            for _ in block_lines:
                random_var1 = generate_random_name()
                random_var2 = generate_random_name()
                obfuscated_lines.append(f"{indent}    ${random_var1} = ${random_var2}")
            obfuscated_lines.append(f"{indent}}} catch {{}}")
            i = end + 1
        else:
            group_start = i
            while i < len(lines) and not any(start <= i <= end for start, end in block_ranges):
                i += 1
            group_end = i

            if group_start != group_end:
                group_lines = lines[group_start:group_end]
                indent = re.match(r'^\s*', lines[group_start]).group(0)
                obfuscated_lines.append(f"{indent}if ($true) {{")
                obfuscated_lines.extend([f"{indent}    {l}" for l in group_lines])
                obfuscated_lines.append(f"{indent}}}")
                obfuscated_lines.append(f"{indent}try {{")
                for _ in group_lines:
                    random_var1 = generate_random_name()
                    random_var2 = generate_random_name()
                    obfuscated_lines.append(f"{indent}    ${random_var1} = ${random_var2}")
                obfuscated_lines.append(f"{indent}}} catch {{}}")

    return '\n'.join(obfuscated_lines)

def obfuscate_script(path, obfuscate_vars, remove_comments, remove_whitespace, encode_base64, control_flow_obfuscation):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            script_content = file.read()
    except Exception as e:
        return f"Error reading file: {e}"

    script_content = remove_comments_and_whitespace(script_content, remove_comments, remove_whitespace)

    excluded_vars = {'env', 'true', 'false', 'null', '_', 'this', 'input', 'args'}
    if obfuscate_vars:
        variables = re.findall(r'\$\b[a-zA-Z_][a-zA-Z0-9_]*\b', script_content)
        for var in set(variables):
            var_name = var[1:].split(':')[0]
            if var_name.lower() not in excluded_vars:
                new_name = '$' + generate_random_name()
                script_content = re.sub(re.escape(var) + r'\b', new_name, script_content)

    if control_flow_obfuscation:
        script_content = insert_control_flow_obfuscation(script_content)

    if encode_base64:
        encoded_content = base64.b64encode(script_content.encode('utf-8')).decode('utf-8')
        script_content = f'IEX ([System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("{encoded_content}")))'

    output_path = filedialog.asksaveasfilename(defaultextension=".ps1", filetypes=[("PowerShell Scripts", "*.ps1")])
    if output_path:
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(script_content)
            return f"Obfuscated script saved to {output_path}"
        except Exception as e:
            return f"Error writing file: {e}"
    else:
        return "Save operation cancelled."

def browse_file(entry):
    filename = filedialog.askopenfilename()
    if filename:
        entry.delete(0, tk.END)
        entry.insert(0, filename)

def obfuscate_button_click():
    input_path = input_entry.get()
    if not input_path:
        messagebox.showwarning("Input Error", "Please select an input script.")
        return

    obfuscate_vars = var_checkbox_var.get()
    remove_comments = remove_comments_var.get()
    remove_whitespace = remove_whitespace_var.get()
    encode_base64 = base64_encode_var.get()
    control_flow_obfuscation = control_flow_var.get()

    result = obfuscate_script(input_path, obfuscate_vars, remove_comments, remove_whitespace, encode_base64, control_flow_obfuscation)
    result_label.config(text=result)

def load_local_image(image_path, max_size=(300, 300)):
    if not os.path.exists(image_path):
        return None

    try:
        img = Image.open(image_path)
        img.thumbnail(max_size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

root = tk.Tk()
root.title("dag's Obfuscator")

image_path = "DaObfu.jpg"
photo = load_local_image(image_path)
if photo:
    image_label = tk.Label(root, image=photo)
    image_label.pack()

tk.Label(root, text="Input Script:").pack()
input_entry = tk.Entry(root, width=50)
input_entry.pack()
tk.Button(root, text="Browse...", command=lambda: browse_file(input_entry)).pack()

var_checkbox_var = tk.BooleanVar()
remove_comments_var = tk.BooleanVar()
remove_whitespace_var = tk.BooleanVar()
control_flow_var = tk.BooleanVar()
base64_encode_var = tk.BooleanVar()

tk.Checkbutton(root, text="Obfuscate Variables", variable=var_checkbox_var).pack()
tk.Checkbutton(root, text="Remove Comments", variable=remove_comments_var).pack()
tk.Checkbutton(root, text="Remove Blank Lines", variable=remove_whitespace_var).pack()
tk.Checkbutton(root, text="Control Flow Obfuscation", variable=control_flow_var).pack()
tk.Checkbutton(root, text="Base64 Encode", variable=base64_encode_var).pack()

obfuscate_button = tk.Button(root, text="Save", command=obfuscate_button_click)
obfuscate_button.pack()
result_label = tk.Label(root, text="", height=5, wraplength=300)
result_label.pack()

root.mainloop()