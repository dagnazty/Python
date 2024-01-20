import tkinter as tk
from tkinter import filedialog
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

def obfuscate_script(path, obfuscate_vars, remove_comments, remove_whitespace, encode_base64):
    with open(path, 'r', encoding='utf-8') as file:
        script_content = file.read()

    script_content = remove_comments_and_whitespace(script_content, remove_comments, remove_whitespace)

    excluded_vars = {'env', 'true', 'false', 'null', '_', 'this', 'input', 'args'}
    if obfuscate_vars:
        variables = re.findall(r'\$\b[a-zA-Z_][a-zA-Z0-9_]*\b', script_content)
        for var in set(variables):
            var_name = var[1:].split(':')[0]
            if var_name.lower() not in excluded_vars:
                new_name = '$' + generate_random_name()
                script_content = re.sub(re.escape(var) + r'\b', new_name, script_content)

    if encode_base64:
        # Encode the content as Base64 and wrap it in a PowerShell script block
        encoded_content = base64.b64encode(script_content.encode('utf-8')).decode('utf-8')
        script_content = f"IEX ([System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('{encoded_content}')))"

    base, ext = os.path.splitext(path)
    output_path = f"{base}_obfuscated{ext}"

    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(script_content)

    return f"Obfuscated script saved to {output_path}"

def browse_file(entry):
    filename = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, filename)

def obfuscate_button_click():
    input_path = input_entry.get()
    obfuscate_vars = var_checkbox_var.get()
    remove_comments = remove_comments_var.get()
    remove_whitespace = remove_whitespace_var.get()
    encode_base64 = base64_encode_var.get() 
    result = obfuscate_script(input_path, obfuscate_vars, remove_comments, remove_whitespace, encode_base64)
    result_label.config(text=result)

root = tk.Tk()
root.title("dag's Obfuscator")

tk.Label(root, text="Input Script:").pack()
input_entry = tk.Entry(root, width=50)
input_entry.pack()
tk.Button(root, text="Browse...", command=lambda: browse_file(input_entry)).pack()

var_checkbox_var = tk.BooleanVar()
remove_comments_var = tk.BooleanVar()
remove_whitespace_var = tk.BooleanVar()
base64_encode_var = tk.BooleanVar()

tk.Checkbutton(root, text="Obfuscate Variables", variable=var_checkbox_var).pack()
tk.Checkbutton(root, text="Remove Comments", variable=remove_comments_var).pack()
tk.Checkbutton(root, text="Remove Blank Lines", variable=remove_whitespace_var).pack()
tk.Checkbutton(root, text="Base64 Encode", variable=base64_encode_var).pack()

obfuscate_button = tk.Button(root, text="Obfuscate", command=obfuscate_button_click)
obfuscate_button.pack()
result_label = tk.Label(root, text="", height=5, wraplength=300)
result_label.pack()

root.mainloop()
