#!/usr/bin/env python3
import os
import time
import argparse

from dandelion import __version__
from dandelion.segsm.create_gsm import main as create_gsm, get_parser as create_gsm_parser
from dandelion.segsm.run_gsm import main as run_gsm, get_parser as run_gsm_parser
from dandelion.segsm.filter_gsm import main as filter_gsm, get_parser as filter_gsm_parser
from dandelion.neb.run_neb import main as run_neb, get_parser as run_neb_parser
from dandelion.neb.filter_neb import main as filter_neb, get_parser as filter_neb_parser
from dandelion.neb.compile_neb import main as compile_neb, get_parser as compile_neb_parser


def merge_args_with_defaults(module_parser, custom_args):
    """
    Merge custom arguments with module defaults.
    Args:
    - module_parser: the module parser function
    - custom_args: dictionary of custom arguments

    Returns:
    - argparse.Namespace: merged namespace of arguments
    """
    
    parser = module_parser()
    for action in parser._actions:
        if action.required:
            action.required = False

    defaults = vars(parser.parse_args([]))
    defaults.update(custom_args)

    for action in parser._actions:
        if not action.required and action.dest in custom_args:
            action.required = True

    return argparse.Namespace(**defaults)

def print_header(width=70):
    
    print(f'''                      
                     
                                                     `;:`  BREAK 1 2
                                         .;:;         /    BREAK 3 4 
        _____                   _      _;::;         `     ADD 1 3
        |  __ \                | |    | |';:;'           
        | |  | | __ _ _ __   __| | ___| |  _  ___  _ __  
        | |  | |/ _` | '_ \ / _` |/ _ \ | | |/ _ \| '_ \ 
        | |__| | (_| | | | | (_| |  __/ | | | (_) | | | |
        |_____/ \__,_|_| |_|\__,_|\___|_| |_|\___/|_| |_|
    
{"Chemical compound space sampling".center(width)}    
{"near transition state using xTB, SE-GSM and NEB".center(width)}    
{("Ver. " + __version__  + " by mlee").center(width)}
''')

def print_separator(text, width=70):
    border = "╔" + "═" * (width-2) + "╗"
    
    total_symbols_len = width - len(text) - 4  
    half_len = total_symbols_len // 2
    left_symbol = "║" + " " * (half_len - 1)
    right_symbol = " " * (total_symbols_len - half_len - 1) + "║"
    separator = left_symbol + '  ' + text + '  ' + right_symbol
    
    end = "╚" + "═" * (width-2) + "╝"
    print("\n\n" + border)
    print(separator)
    print(end + "\n\n")


def main():
    args = parse_arguments()
    
    input_path = args.input_path
    output_path = args.output_path
    max_workers = args.max_workers
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    phases = [
        ("1. Creating GSM", create_gsm, create_gsm_parser, {
            'input_path': input_path,
            'output_path': os.path.join(output_path, '1_gsm')
        }),
        ("2. Running GSM", run_gsm, run_gsm_parser, {
            'input_path': os.path.join(output_path, '1_gsm'),
            'max_workers': max_workers
        }),
        ("3. Filtering GSM", filter_gsm, filter_gsm_parser, {
            'input_path': os.path.join(output_path, '1_gsm'),
            'output_path': os.path.join(output_path, '2_gsm_filtered')
        }),
        
        ("4. Running NEB", run_neb, run_neb_parser, {
            'input_path': os.path.join(output_path, '2_gsm_filtered'),
            'output_path': os.path.join(output_path, '3_neb'),
            'max_workers': max_workers            
        }),
        ("5. Filtering NEB", filter_neb, filter_neb_parser, {
            'input_path': os.path.join(output_path, '3_neb'),
            'output_path': os.path.join(output_path, '4_neb_filtered')
        }),          
        ("6. Compiling samples", compile_neb, compile_neb_parser, {
            'input_path': os.path.join(output_path, '4_neb_filtered', 'reactions.json'),
            'output_path': os.path.join(output_path, 'xtb.h5')
        }),                    
    ]

    print_header()
    for title, function, parser, custom_args in phases:
        time.sleep(3)
        print_separator(title)
        merged_args = merge_args_with_defaults(parser, custom_args)
        function(merged_args)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Do SEGSM and NEB from mother structures,\
                                     Other parameters can be set in each modules')
    
    parser.add_argument('-i', '--input_path', required=True, 
                        help='Input path of mother structures')    
    parser.add_argument('-o', '--output_path', required=True, 
                        help='Output path of dandelion')
    parser.add_argument('-n', '--max_workers', type=int, required=True, 
                        help='Number of worker processes')
    return parser.parse_args()


if __name__ == "__main__":
    main()