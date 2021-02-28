import astroid
from astroid.nodes import Import, ImportFrom, FunctionDef, ClassDef, Assign, AssignAttr, Call, Name

def parse_text(text: str):
    #Validation steps
    #Language selection
    root = astroid.parse(text)
    return root

def extract_names_from_node(node) -> list:
    names = []
    if hasattr(node, 'name'):
        names.append(node.name)
    if isinstance(node, Import):
        for lib, alias in node.names:
            names.extend([lib])
    if isinstance(node, ImportFrom):
        names.append(node.modname)
        for func, alias in node.names:
            names.append(func)
    if isinstance(node, Assign):
        print(node)
        for target in node.targets:
            names.extend(extract_names_from_node(target))
        names.extend(extract_names_from_node(node.value))
    if isinstance(node, AssignAttr):
        names.append(node.attrname)
    if isinstance(node, Call):
        names.extend(extract_names_from_node(node.func))
        if node.args is not None:
            for arg in node.args:
                names.extend(extract_names_from_node(arg))
        if node.keywords is not None:
            for kwarg in node.keywords:
                names.extend(extract_names_from_node(kwarg))
    return names

def recurse_on_tree(root):
    root_names = extract_names_from_node(root)
    if not hasattr(root, 'body'):
        return root_names
    if not isinstance(root.body, list):
        return root_names
    for node in root.body:
        node_names = recurse_on_tree(node)
        root_names.extend(node_names)
    return root_names

def test_recurse_on_tree(filepath='sample_code.py'):
    names=None
    with open(filepath, 'r') as f:
        text = f.read()
        root = parse_text(text)
        names = recurse_on_tree(root)[1:]
    print(names)

if __name__ == '__main__':
    test_recurse_on_tree()