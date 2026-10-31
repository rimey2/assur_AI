"""Local Streamlit launcher with Windows socket-loop compatibility."""
from pathlib import Path
import asyncio
import os
import runpy
import sys


def configure_runtime():
    # This local HTTP app does not use asyncio subprocesses or pipe transports.
    # Avoid Proactor's socket-shutdown callback on Windows/Python 3.12.
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def main():
    configure_runtime()
    root = Path(__file__).resolve().parent
    os.chdir(root)
    sys.path.insert(0, str(root / '.packages'))
    sys.argv = ['streamlit', 'run', str(root / 'app.py'),
                '--global.developmentMode=false', '--server.address=127.0.0.1',
                '--server.headless=true', '--browser.gatherUsageStats=false']
    runpy.run_module('streamlit', run_name='__main__')


if __name__ == '__main__':
    main()
