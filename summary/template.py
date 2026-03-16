
import json

def template(messages:list):
    return f"""
根据具体的任务， 进行不同的压缩, 要求总结不超过1000字。


## task 编码 workflow ##
    1.总接用户需求。
    2.当前哪些已经完成。
    3.当前正在做什么。
    4.接下来要做什么。

## task 聊天 workflow ##
    1.用户的需求是什么，用户的深层次需求是什么。
    2.大概聊了哪些内容。
    3.接下来应该根据用户深层次需求继续聊。


template:
```

## 编码
**1. 用户需求总结**  
- xxxx

**2. 已完成**  
- xxxx

**3. 当前正在做**  
- xxxx
**4. 接下来要做**  
- xxxx  
```

历史会话：

```{messages}```
"""