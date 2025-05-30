#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from coverage import Coverage


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

    running_tests = sys.argv[1] == "test"
    if running_tests:
        cov = Coverage()
        cov.erase()
        cov.start()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

    if running_tests:
        cov.stop()
        cov.save()
        cov.html_report()
        covered = cov.report()
        if covered < 49.5:
            print(f'Coverage minimum at 50, current: {covered}')
            sys.exit(1)


if __name__ == '__main__':
    main()
