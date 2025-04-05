"""Script to run the application."""
import os
import sys
import uvicorn
from cli import cli

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        # Remove the "cli" argument and pass the rest to the CLI
        sys.argv.pop(1)
        cli()
    else:
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True) 