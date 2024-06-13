import ast
import astor

class FunctionReorderer(ast.NodeTransformer):
    def __init__(self, method_order):
        self.method_order = method_order

    def visit_ClassDef(self, node):
        # Reorder methods in the class based on predefined order
        methods = {method.name: method for method in node.body if isinstance(method, ast.FunctionDef)}
        ordered_methods = [methods[name] for name in self.method_order if name in methods]

        # Keep non-method elements in their original order
        non_methods = [n for n in node.body if not isinstance(n, ast.FunctionDef)]
        node.body = non_methods + ordered_methods
        return node

def reorder_functions_in_class(file_path, class_name, method_order):
    with open(file_path, 'r') as file:
        source_code = file.read()

    # Parse the source code
    tree = ast.parse(source_code)

    # Reorder functions in the specified class
    reorderer = FunctionReorderer(method_order)
    tree = reorderer.visit(tree)

    # Convert AST back to source code
    return astor.to_source(tree)

# File paths
input_file_path = 'src/managers/audio_manager.py'
output_file_path = 'development_utils/audio_manager_2.py'

# Define the order of methods
method_order = [
    '__init__', 'initialize', 'start_recording', 'stop_recording', 'is_recording',
    'run', 'check_and_process_updates', '_recording_loop', '_async_processing_loop',
    '_store_snippet', '_combine_audio_files', '_combining_and_transcribing_loop',
    'get_transcript', 'format_transcript', 'transcribe_with_diarization', 'preprocess_audio',
    'correct_transcript', 'correct_transcript_compare', 'set_transcript_update_callback',
    'delete_existing_audio_files', '_record_snippet', '_process_snippet'
]

# Reorder functions in class
reordered_code = reorder_functions_in_class(input_file_path, 'AudioManager', method_order)

# Print the reordered code
print("\nReordered code:\n"
        "----------------\n"
        f"{reordered_code}")

# Write the reordered code to a new file
with open(output_file_path, 'w') as file:
    file.write(reordered_code)
