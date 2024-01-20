# DaObfu
dag's Obfuscator aka DaObfu is a Python script that provides a graphical user interface for obfuscating PowerShell scripts. It offers various features such as variable obfuscation, comment removal, whitespace removal, and Base64 encoding.

## Features
Variable Obfuscation: Randomizes variable names in the script to make understanding and modifying the script more challenging.
Comment Removal: Strips out comments from the script, which can often contain revealing information or notes.
Whitespace Removal: Eliminates unnecessary blank lines to compact the script and make it less readable.
Base64 Encoding: Encodes the entire script in Base64, offering an additional layer of obfuscation.
GUI Interface: Easy-to-use graphical interface with script browsing and real-time processing feedback.

>[!IMPORTANT]
>To use dag's Obfuscator, ensure you have Python installed on your system along with the following dependencies:
>
>Tkinter (usually comes pre-installed with Python)
>PIL (Python Imaging Library)
>You can install PIL using pip:

    pip install pillow
    
## Usage
Launch the Script: Run the script using Python to open the GUI.
Load a PowerShell Script: Click on 'Browse...' to select a PowerShell script file.
Configure Obfuscation Settings:
Check 'Obfuscate Variables' to randomize variable names.
Check 'Remove Comments' to strip comments.
Check 'Remove Blank Lines' to eliminate unnecessary whitespace.
Check 'Base64 Encode' for encoding the script in Base64.
Obfuscate: Click on the 'Obfuscate' button to process the script.
View Results: The path to the obfuscated script will be displayed in the application window.

>[!NOTE]
>Customizing the Tool
>Adding Custom Images: Replace the DaObfu.jpg file in the script's directory with your own image (keeping the same filename) to customize the tool's appearance.
>Adjusting Image Size: Modify the max_size parameter in load_local_image function to change the displayed image size.

## Legal
Payloads from this repository are provided for educational purposes only. Payloads from dag are intended for authorized auditing and security analysis purposes only where permitted subject to local and international laws where applicable. Users are solely responsible for compliance with all laws of their locality. Dag and affiliates claim no responsibility for unauthorized or unlawful use.

## License
This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/dagnazty/Flipper_Zero/blob/main/LICENSE) file for details
