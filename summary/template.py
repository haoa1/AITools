
import json

def template(messages:list):
    return f"""

历史会话：

```{messages}```
"""