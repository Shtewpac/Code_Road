

# Making `config.py` Importable in the `src` Folder

To make the `config` module available to all files in the `src` directory without needing to call `sys.path.append()` each time, you can add the directory containing `config.py` to the `PYTHONPATH` environment variable. Here are the steps:

1. **Open Terminal**:
   - On macOS and Linux: Open a terminal.
   - On Windows: Open Command Prompt or Git Bash.

2. **Navigate to the Directory**:
   Navigate to the directory containing the `config.py` file using the `cd` command.
   ```bash
   cd "G:/Other computers/My Laptop/UMass_CS/CS326_WebProgramming/Live Dialogue Options/LIVE_DIALOGUE_OPTIONS"
   ```
   or just
   cd LIVE_DIALOGUE_OPTIONS

3. **Set the `PYTHONPATH` Environment Variable**:
   - On macOS and Linux:
     ```bash
     export PYTHONPATH=$PYTHONPATH:"G:/Other computers/My Laptop/UMass_CS/CS326_WebProgramming/Live Dialogue Options/LIVE_DIALOGUE_OPTIONS"
     ```
   - On Windows:
     ```cmd
     set PYTHONPATH=%PYTHONPATH%;"G:\Other computers\My Laptop\UMass_CS\CS326_WebProgramming\Live Dialogue Options\LIVE_DIALOGUE_OPTIONS"
     ```

Now, you can import the `config` module in any file within the `src` directory without any additional configuration:

```python
import config
```
```