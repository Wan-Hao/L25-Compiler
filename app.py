import sys
import io
import json
from flask import Flask, render_template, request, jsonify
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.error import CompilerError
from src.visualizer import ASTVisualizer  # Add this import

# We need to make the 'src' directory available for imports
sys.path.insert(0, './src')

app = Flask(__name__)

# Store example file contents in memory
EXAMPLES = {}
EXAMPLE_FILES = {
    "basic": "tests/test_programs/example.l25",
    "factorial": "tests/test_programs/factorial.l25",
    "full": "tests/test_programs/full_features.l25",
    "try_catch": "tests/test_programs/division_by_zero.l25",
}

def load_examples():
    for name, path in EXAMPLE_FILES.items():
        try:
            with open(path, 'r') as f:
                EXAMPLES[name] = f.read()
        except FileNotFoundError:
            print(f"Warning: Example file not found at {path}")
            EXAMPLES[name] = f"# Error: Could not load {path}"

@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html', examples=EXAMPLES)

@app.route('/ast-viewer')
def ast_viewer():
    """Serve the AST visualization page."""
    return render_template('ast_viewer.html', examples=EXAMPLES)

@app.route('/compile', methods=['POST'])
def compile_code():
    """API endpoint to compile and run L25 code."""
    source_code = request.json.get('code', '')
    
    # Redirect stdout to capture output from the 'output' statement
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()
    
    output_string = ""
    error_string = ""

    try:
        lexer = Lexer(source_code)
        tokens = lexer.tokens()
        parser = Parser(tokens)
        interpreter = Interpreter(parser)
        interpreter.interpret()
        
    except CompilerError as e:
        error_string = str(e)
    except Exception as e:
        error_string = f"An unexpected system error occurred: {e}"
    finally:
        # Get the captured output and restore stdout
        output_string = captured_output.getvalue()
        sys.stdout = old_stdout

    return jsonify({
        'output': output_string,
        'error': error_string
    })

@app.route('/visualize', methods=['POST'])
def visualize_ast():
    """API endpoint to generate AST visualization."""
    source_code = request.json.get('code', '')
    
    try:
        lexer = Lexer(source_code)
        tokens = lexer.tokens()
        parser = Parser(tokens)
        ast = parser.parse()  # Get the AST without interpreting
        
        # Generate Mermaid diagram
        visualizer = ASTVisualizer(ast)
        mermaid_graph = visualizer.generate()
        
        return jsonify({
            'mermaid': mermaid_graph,
            'error': None
        })
        
    except CompilerError as e:
        return jsonify({
            'mermaid': None,
            'error': str(e)
        })
    except Exception as e:
        return jsonify({
            'mermaid': None,
            'error': f"An unexpected system error occurred: {e}"
        })

if __name__ == '__main__':
    load_examples()
    app.run(debug=True, port=5001)
