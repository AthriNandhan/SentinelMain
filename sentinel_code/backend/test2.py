import tree_sitter_python
from tree_sitter import Language, Parser
PY_LANGUAGE = Language(tree_sitter_python.language())
parser = Parser(PY_LANGUAGE)
tree = parser.parse(b"query = f'SELECT * FROM users WHERE username = \\'{username}\\''")
print(tree.root_node.sexp())

query = PY_LANGUAGE.query("""
    (string) @str
""")
captures = query.captures(tree.root_node)
print([(node.text, name) for node, name in captures])
