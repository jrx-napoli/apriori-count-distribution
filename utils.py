import os
import json


def save_to_file(output):

    output_file_path = 'output.txt'
    output_directory = 'output'

    # Create the directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(f'output')

    # Write the list to the file
    with open(f'{output_directory}\{output_file_path}', 'w') as file:
        for rule in output:
            file.write(str(rule))
            file.write('\n')

    print(f'\nOutput saved to {output_file_path}')
