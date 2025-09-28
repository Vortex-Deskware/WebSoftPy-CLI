# Turn any website into a desktop app. Fast, flexible, yours. That's WebSoftPy.

<img width="500" height="500" alt="Untitled (35)" src="https://github.com/user-attachments/assets/28fab140-1128-436c-84be-21df47525f92" />


## Prerequisites

---

- ```pip install PyQt6 PyQt6-WebEngine pyinstaller rich```  
  Required for **WebSoftPy 2.5 CLI | Expressional** and later.

  **Or** run the included batch script (Windows only).
---

# Usage

WebSoftPy is a **command-line tool** that converts any website into a standalone desktop web app using PyQt6 and Qt WebEngine, no GUI needed.

## How to Use

1. **Run the CLI generator**:  
   ```bash
   python WebSoftPy.py
   ```

2. **Follow the interactive prompts**:  
   - **Application Title**: The name of your web app (e.g., "My WebSoftPy App").  
   - **Target URL**: The full `https://` (or `http://`) address of the site.  
   - **Window Style**: Choose from:
     - *Normal*: Standard OS window.  
     - *Custom Title Bar*: Frameless window with draggable title bar and **theme-based SVG controls**.  
     - *Frameless Window*: Borderless, draggable window with no buttons.  
   - **Theme** *(shown only for “Custom Title Bar”)*: Pick a visual style:  
     - *WebSoftPy Flow* (original)  
     - *WebSoftPy Desk* (minimal)  
     - *WebSoftPy Color* (colored icons)  
     - *WebSoftPy Fizz* (bubble-inspired)  
     - *WebSoftPy Text* (text-based labels)  
     - *WebSoftPy Draw* (hand-drawn style)  
   - **Persistent Storage**: Enable to save cookies, cache, and local data between sessions.

3. **Generate the app**:  
   The script is automatically saved to the `webapps/` folder as a `.py` file.

4. **(Optional) Build an executable**:  
   When prompted, choose **Yes** to create a standalone `.exe` (Windows) or binary (macOS/Linux) using PyInstaller.  
   > ⚠️ Requires `pyinstaller` (`pip install pyinstaller`).

5. **Run your app**:  
   - Execute the `.py` file directly (requires Python + PyQt6).  
   - Or run the generated executable for full portability.

---

### File Structure

After generation, your project directory will look like this:

```
your_project/
├── websoftpy_cli.py        ← Generator (run this)
├── elements/               ← Theme assets
│   ├── WebSoftPy Flow/
│   │   ├── minimize.svg
│   │   ├── maximize.svg
│   │   └── close.svg
│   ├── WebSoftPy Desk/
│   ├── WebSoftPy Color/
│   ├── WebSoftPy Fizz/
│   ├── WebSoftPy Text/
│   └── WebSoftPy Draw/
└── webapps/                ← Generated apps go here
    ├── my_app.py           ← Source code
    └── my_app/             ← Executable (if built)
        └── my_app.exe
```

> **Important**:  
> - Do **not move** generated apps outside the `webapps/` folder—this breaks SVG icon paths.  
> - Do **not rename** a webapp after logging in—this will reset persistent storage and delete cookies.  
> - For easy access, create desktop shortcuts instead.

---

## How the CLI Looks

WebSoftPy CLI uses **rich, colorful prompts** for a modern terminal experience:

- Clear step-by-step questions  
- Numbered options for window style and themes  
- Visual feedback on success or error  
- Clean, readable layout with no clutter  

<img width="961" height="483" alt="image" src="https://github.com/user-attachments/assets/c6ae8d5a-03e5-4ea7-ae76-16bab163e2ff" />


*(Example: CLI with theme selection and build prompt)*

---

## Notes from Developers

- WebSoftPy CLI retains **all features** of the GUI version, just in terminal form.  
- The tool is generic, no site is hardcoded. It works with any valid URL.  
- Generated apps are fully self-contained and respect user privacy settings.  
- Version 2.5 introduces **Expressional** theming, now available in the CLI for power users and automation.

---

### Frequently Asked Questions

**Q: Why are `.exe` files so large (~150 MB)?**  
A: PyInstaller bundles the Python interpreter, PyQt6, Qt WebEngine, and all dependencies. To reduce size, compress the executable with [UPX](https://upx.github.io/), a free and secure executable packer that typically reduces file size by 50–70% with no runtime penalty.

**Q: What license is WebSoftPy under?**  
A: WebSoftPy is licensed under the **Apache License 2.0**. See the `LICENSE` file for details.

**Q: Can I customize the title bar buttons?**  
A: Yes. Each theme has its own folder in `elements/`. You can edit or replace the SVGs in any theme folder (e.g., `elements/WebSoftPy Desk/minimize.svg`). Just keep the filenames unchanged.

**Q: Why do I need `rich`?**  
A: `rich` enables the beautiful, interactive CLI interface. It’s lightweight and only used in the generator, not in your final apps.

---

Vortex Deskware © 2025  
*WebSoftPy 2.5 CLI | Expressional*
