#!/usr/bin/env python3
"""
flt_tool.py is a simple script to aid in Vivado project creation.
"""
import argparse
import logging
import os.path
import sys
from typing import List

from jinja2 import Environment, FileSystemLoader

__version__ = '0.1.0'


def parse_flt_file(flt_file: str, parsed_files: List[str] = None) -> List[str]:
    """Parse a .flt file and get the file list."""
    logging.info(f'Parse flt file: "{flt_file}".')
    file_list = []

    flt_file = os.path.abspath(flt_file)
    base_dir = os.path.dirname(flt_file)

    # parsed_files logs .flt file we have already seen
    if parsed_files is None:
        parsed_files = [flt_file]
    else:
        parsed_files.append(flt_file)

    with open(flt_file, encoding='utf8') as fd:
        for line in fd:
            line = line.strip()

            # Bypass empty or comment line
            if len(line) == 0 or line.startswith('#'):
                continue

            # It should be normalized, so we use it as unique identifier
            line = os.path.abspath(os.path.join(base_dir, line))

            # Recursively parse .flt file, but take care cycle reference
            root_ext = os.path.splitext(line)
            if root_ext[1] == '.flt':
                if line not in parsed_files:
                    parsed_files.append(line)
                    sub_file_list = parse_flt_file(line, parsed_files)
                    file_list.extend(sub_file_list)
                else:
                    logging.debug(f'File "{line}" is already parsed, so ignore.')
            else:
                # Vivado Tcl does not handle backward slash well
                file_list.append(line.replace('\\', '/'))

    return file_list


def generate_files(base: str, name: str, file_lists: List[str]) -> None:
    build_dir = 'vivado_build'
    build_dir = os.path.abspath(os.path.join(base, build_dir))

    if os.path.isdir(build_dir):
        logging.info(f'Folder "{build_dir}" already exists.')
    elif os.path.exists(build_dir):
        logging.error(f'File "{build_dir} already exists but is not a folder, abort."')
        sys.exit(2)
    else:
        logging.info(f'Create folder "{build_dir}".')
        os.mkdir(build_dir)

    variables = {
        'version': __version__,
        'project_name': name,
        'project_dir': '.',
        'vivado_version': '2022.1',
        'part': 'xc7z020-clg484-1',
        'src_files': file_lists,
    }

    # Get Jinja2 Environment
    env = Environment(
        loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
        newline_sequence='\n',
        keep_trailing_newline=True
    )

    # Render and write target files
    targets = ['.gitignore', 'Makefile', 'vivado_project.sh', 'vivado_project.bat', 'vivado_project.tcl']
    for t in targets:
        template = env.get_template(t + '.jinja2')
        rendered = template.render(variables)

        target_file = os.path.join(build_dir, t)
        if os.path.isfile(target_file):
            logging.warning(f'File "{target_file}" already exists, it will be overwrite.')
        elif os.path.exists(target_file):
            logging.error(f'File "{target_file}" already exists but is not a regular file, abort.')
            sys.exit(2)
        with open(target_file, mode='w', encoding='utf8', newline='\n') as fd:
            fd.write(rendered)


def parse_arguments(argv: List[str] = None) -> argparse.Namespace:
    """Build the CLI of script."""
    parser = argparse.ArgumentParser()
    # Input and output
    parser.add_argument('flt',
                        help='Read input form specified .flt file')
    parser.add_argument('-p', '--print-only',
                        help='Only print file list then exit',
                        dest='print_only',
                        action='store_true')
    # Debug log level
    parser.add_argument('-q', '--quiet',
                        help='Only show error messages',
                        dest='debug_level',
                        action='store_const',
                        const=logging.ERROR,
                        default=logging.WARNING)
    parser.add_argument('-v', '--verbose',
                        help='Show almost all log, except debug messages',
                        dest='debug_level',
                        action='store_const',
                        const=logging.INFO)
    parser.add_argument('-d', '--debug',
                        help='Show all log, including debug messages',
                        dest='debug_level',
                        action='store_const',
                        const=logging.DEBUG)
    # Get the version string of this script.
    parser.add_argument('-V', '--version',
                        action='version',
                        version=__version__)
    args = parser.parse_args(argv)
    return args


def main(argv: List[str] = None) -> None:
    """This function will be executed if run as script."""
    args = parse_arguments(argv)

    # Set logging level to desired value
    logging.basicConfig(level=args.debug_level)
    logging.debug(f'Python version: {sys.version.split()[0]}')
    logging.debug(f'Script version: {__version__}')
    logging.debug(f'Arguments: {vars(args)}')

    top_flt_file = args.flt
    top_flt_file = os.path.abspath(top_flt_file)
    logging.info(f'Top level flt file: "{top_flt_file}"')

    base_dir = os.path.dirname(top_flt_file)
    root_ext = os.path.splitext(os.path.basename(top_flt_file))
    name = root_ext[0]

    # Check input
    if not os.path.isfile(top_flt_file):
        logging.error(f'File "{top_flt_file}" is not a regular file')
        sys.exit(1)
    if root_ext[1] != '.flt':
        logging.error(f'File "{top_flt_file}" should has extension .flt')
        sys.exit(1)

    file_list = parse_flt_file(top_flt_file)
    if args.print_only:
        for item in file_list:
            print(item)
        sys.exit(0)

    generate_files(base_dir, name, file_list)


if __name__ == '__main__':
    main(sys.argv[1:])
