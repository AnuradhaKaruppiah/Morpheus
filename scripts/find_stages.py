# find all references to add_stage in the codebase
'''
This script is used for analyzing the morpheus code base. It only works in an environment where the
morpheus 'base' package is installed.
'''
import os
import re

import click
from tabulate import tabulate


def find_stages(file_paths, details):
    '''
    Find all stage names in a give directory.
    Args:
    details: if True, show where the stage is used and its dependencies
    Returns:
    A tuple containing:
        A list of lists containing the stage names and the files they are used in
        Stages imported from morpheus
    '''
    stage_pat = re.compile(r'add_stage\(\s*(?P<stage_name>\w+)')
    source_pat = re.compile(r'set_source\(\s*(?P<stage_name>\w+)')
    example_pat = re.compile(r'examples\/(?P<example_name>\w+)')

    stage_name_map = {}
    source_name_map = {}
    all_morpheus_imports = []

    def is_source_stage(stage, import_str):
        '''
        Fixme: this is a poor hack
        from morpheus.pipeline.source_stage import SourceStage
        exec(import_str)
        return eval(f'issubclass({stage}, SourceStage)')
        '''
        return False

    # read every file in the codebase
    for file_path in file_paths:
        for root, _, files in os.walk(file_path):
            for file in files:
                if not file.endswith('.py'):
                    continue
                with open(os.path.join(root, file), mode='r', encoding='utf-8') as f:
                    contents = f.read()
                    source_names = source_pat.findall(contents)
                    stage_names = stage_pat.findall(contents)
                    file_name = os.path.join(root, file)
                    obj = example_pat.search(file_name)

                    # replace file name with a shorthand where possible
                    if obj and obj.group('example_name'):
                        # use the dir name under examples
                        file_name = obj.group('example_name')
                    elif 'nv-ingest' in file_name:
                        # use the file_name at the lowest level
                        file_name = file_name.split('/')[-1]
                    elif 'tests' in file_name:
                        # temporarily abstracting the test file names to 'tests'
                        file_name = 'tests'

                    for stage in stage_names:
                        s_name = stage
                        stage_is_source = False
                        import_pat_list = [
                            re.compile(r'from\s+morpheus.*import\s+' + f'{s_name}'),
                            re.compile(r'import\s+morpheus.*' + f'{s_name}')
                        ]
                        for import_pat in import_pat_list:
                            morpheus_import = import_pat.search(contents)
                            if morpheus_import:
                                if is_source_stage(s_name, morpheus_import.group()):
                                    source_names.append(s_name)
                                    stage_is_source = True
                                    break
                                if s_name not in all_morpheus_imports:
                                    all_morpheus_imports.append(s_name)
                                break
                        if stage_is_source:
                            # if stage is a source, skip it
                            continue
                        if stage not in stage_name_map:
                            stage_name_map[stage] = [file_name]
                        else:
                            stage_name_map[stage].append(file_name)

                    for source in source_names:
                        s_name = source
                        import_pat_list = [
                            re.compile(r'from\s+morpheus.*import\s+' + f'{s_name}'),
                            re.compile(r'import\s+morpheus.*' + f'{s_name}')
                        ]
                        for import_pat in import_pat_list:
                            morpheus_import = import_pat.search(contents)
                            if morpheus_import:
                                if s_name not in all_morpheus_imports:
                                    all_morpheus_imports.append(s_name)
                                break
                        if source not in source_name_map:
                            source_name_map[source] = [file_name]
                        else:
                            source_name_map[source].append(file_name)

    # Convert the dictionary to a list of lists for tabulate
    if details:
        source_list = [[source, 's', len(users), users] for source, users in source_name_map.items()]
        stage_list = [[stage, '', len(users), users] for stage, users in stage_name_map.items()]
    else:
        source_list = [[source, 's', len(users)] for source, users in source_name_map.items()]
        stage_list = [[stage, '', len(users)] for stage, users in stage_name_map.items()]

    return (source_list + stage_list, all_morpheus_imports)


@click.command()
@click.option('--details', default=True, type=bool, help='Show where the stage is used')
@click.option('--file_paths',
              default=('./examples', './tests'),
              multiple=True,
              help='Specify the file paths to search for stages')
@click.option('--from_morpheus', default=False, type=bool, help='Print only stages from morpheus')
def stages(details, file_paths, from_morpheus):
    all_list, all_morpheus_imports = find_stages(file_paths, details)

    # annotate list with flags
    # if stage name is present in morpheus_imports add a flag 'm' to the flags column
    for i, _ in enumerate(all_list):
        if all_list[i][0] in all_morpheus_imports:
            all_list[i][1] += 'm'

    # apply filters
    # filter out stages that are not from morpheus
    if from_morpheus:
        all_list = [x for x in all_list if 'm' in x[1]]

    # sort the list by the stage name
    all_list = sorted(all_list, key=lambda x: x[0])

    # determine how many stages are used multiple times
    multiple_usages = len([x for x in all_list if x[2] > 1])

    # determine number of sources
    source_count = len([x for x in all_list if 's' in x[1]])

    # stages that are not sources
    stage_count = len(all_list) - source_count

    # if the same user is present multiple times, represent it as a {cnt}x{user}
    if details:
        for i, _ in enumerate(all_list):
            user_list = []
            for elem in set(all_list[i][3]):
                elem_count = all_list[i][3].count(elem)
                tmp_elem = f"{elem_count}x{elem}"
                if elem_count > 1:
                    user_list.append(tmp_elem)
                else:
                    user_list.append(elem)
            all_list[i][3] = user_list
        print(tabulate(all_list, headers=['Stage Name', 'Flags', 'Cnt', 'Users'], tablefmt='plain'))
    else:
        print(tabulate(all_list, headers=['Stage Name', 'Flags', 'Cnt'], tablefmt='simple'))

    print(f"Total sources: {source_count}, total stages: {stage_count},"
          f" stages with multiple usage: {multiple_usages}, stages from morpheus: {len(all_morpheus_imports)}")


@click.group(name=__name__)
def cli():
    pass


cli.add_command(stages)

if __name__ == '__main__':
    cli()
