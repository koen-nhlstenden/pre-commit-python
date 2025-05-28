from hooks.fix_docs import process_file

process_file(file_path="test.py", use_capitalization=True, string_to_check=":param ")
