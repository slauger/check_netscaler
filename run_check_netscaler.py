#!/usr/bin/env python3
"""
PyInstaller entry point for check_netscaler
Wrapper to avoid relative import issues
"""

if __name__ == '__main__':
    from check_netscaler.cli import main
    main()
