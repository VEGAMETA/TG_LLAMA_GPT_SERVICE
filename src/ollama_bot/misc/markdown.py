import re


def _find_all_index(str, pattern):
    index_list = [0]
    for match in re.finditer(pattern, str, re.MULTILINE):
        if match.group(1) != None:
            start = match.start(1)
            end = match.end(1)
            index_list += [start, end]
    index_list.append(len(str))
    return index_list


def _replace_all(text, pattern, function):
    poslist = [0]
    strlist = []
    originstr = []
    poslist = _find_all_index(text, pattern)
    for i in range(1, len(poslist[:-1]), 2):
        start, end = poslist[i:i+2]
        strlist.append(function(text[start:end]))
    for i in range(0, len(poslist), 2):
        j, k = poslist[i:i+2]
        originstr.append(text[j:k])
    if len(strlist) < len(originstr):
        strlist.append('')
    else:
        originstr.append('')
    new_list = [item for pair in zip(originstr, strlist) for item in pair]
    return ''.join(new_list)

def escapeshape(text):
    return '▎*' + text.split()[1] + '*'

def escapeminus(text):
    return '\\' + text

def escapebackquote(text):
    return r'\`\`'

def escapeplus(text):
    return '\\' + text

async def escape(text, flag=0):
    """
    Escapes markdown special characters with the preceding character '\'.
    """
    text = re.sub(r"\\\[", '@->@', text)
    text = re.sub(r"\\\]", '@<-@', text)
    text = re.sub(r"\\\(", '@-->@', text)
    text = re.sub(r"\\\)", '@<--@', text)
    if flag: text = re.sub(r"\\\\", '@@@', text)
    text = re.sub(r"\\", r"\\\\", text)
    if flag: text = re.sub(r"\@{3}", r"\\\\", text)
    text = re.sub(r"_", '\_', text)
    text = re.sub(r"\*{2}(.*?)\*{2}", '@@@\\1@@@', text)
    text = re.sub(r"\n{1,2}\*\s", '\n\n• ', text)
    text = re.sub(r"\*", '\*', text)
    text = re.sub(r"\@{3}(.*?)\@{3}", '*\\1*', text)
    text = re.sub(r"\!?\[(.*?)\]\((.*?)\)", '@@@\\1@@@^^^\\2^^^', text)
    text = re.sub(r"\[", '\[', text)
    text = re.sub(r"\]", '\]', text)
    text = re.sub(r"\(", '\(', text)
    text = re.sub(r"\)", '\)', text)
    text = re.sub(r"\@\-\>\@", '\[', text)
    text = re.sub(r"\@\<\-\@", '\]', text)
    text = re.sub(r"\@\-\-\>\@", '\(', text)
    text = re.sub(r"\@\<\-\-\@", '\)', text)
    text = re.sub(r"\@{3}(.*?)\@{3}\^{3}(.*?)\^{3}", '[\\1](\\2)', text)
    text = re.sub(r"~", '\~', text)
    text = re.sub(r">", '\>', text)
    text = _replace_all(text, r"(^#+\s.+?$)|```[\D\d\s]+?```", escapeshape)
    text = re.sub(r"#", '\#', text)
    text = _replace_all(text, r"(\+)|\n[\s]*-\s|```[\D\d\s]+?```|`[\D\d\s]*?`", escapeplus)
    text = re.sub(r"\n{1,2}(\s*)-\s", '\n\n\\1• ', text)
    text = re.sub(r"\n{1,2}(\s*\d{1,2}\.\s)", '\n\n\\1', text)
    text = _replace_all(text, r"(-)|\n[\s]*-\s|```[\D\d\s]+?```|`[\D\d\s]*?`", escapeminus)
    text = re.sub(r"```([\D\d\s]+?)```", '@@@\\1@@@', text)

    triples = text.count("```") % 2
    singles = text.count("`") % 2
    if triples or singles:
        reversed_text = text[::-1]
    if triples:
        text = reversed_text.replace("```", "`\\`\\`\\", 1)[::-1]
    elif singles:
        text = reversed_text.replace("`", "`\\", 1)[::-1]
    text = re.sub(r"^``([^`]+?)", '\\`\\`\1', text)

    # if text.count(r"``[^`]"):
    #    text = replace_all(text, r"(``)", r'\`\`')

    text = re.sub(r"\@{3}([\D\d\s]+?)\@{3}", '```\\1```', text)
    text = re.sub(r"=", '\=', text)
    text = re.sub(r"\|", '\|', text)
    text = re.sub(r"{", '\{', text)
    text = re.sub(r"}", '\}', text)
    text = re.sub(r"\.", '\.', text)
    text = re.sub(r"!", '\!', text)
    text = text[:-1] if text[-1] == "," else text
    return text
