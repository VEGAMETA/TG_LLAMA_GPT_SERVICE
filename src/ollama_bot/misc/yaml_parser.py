def parse_yaml_lines(lines, indent_level=0):
    result = {}
    key = None
    value = None

    for n, line in enumerate(lines):        
        if not line or line.startswith('#'):
            continue

        cur_indent = 0
        
        for char in line:
            if char != ' ':
                break
            cur_indent += 1

        if cur_indent < indent_level:
            break

        if cur_indent == indent_level:
            parts = line.split(':', 1)
            key = parts[0].strip()
            value = None
            if len(parts) > 1:
                value = parts[1].strip()
            if value:
                result[key] = value
        elif cur_indent > indent_level:
            if key is None:
                raise ValueError("Invalid YAML format")
            if key not in result:
                result[key] = {}
            sub_result = parse_yaml_lines(lines[n:], indent_level=cur_indent)
            result[key].update(sub_result)

    return result
