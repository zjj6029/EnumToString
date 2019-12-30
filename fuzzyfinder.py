# _*_ coding:utf-8 _*_

import re

# user_input 输入字符串
# collection 已有的待模糊匹配的字符串集合
def fuzzyfinder(user_input, collection):
    suggestions = []
    pattern = '.*?'.join(user_input)
    for item in collection:
        match = re.search(pattern, item, re.IGNORECASE)
        if match:
            suggestions.append((len(match.group()), match.start(), item))
    return [x for _,_,x in sorted(suggestions)]
