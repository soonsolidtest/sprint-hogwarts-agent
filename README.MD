```scss
[llm_call] → (LLM建议工具？) → [tool_node (你叫 environment)] → [llm_call] → ...
                           ↘ (没有工具) → END
```
```scss
1. 用户输入 → 
2. LLM 产生 tool_call → 
3. 调用工具 → 
4. 返回 ToolMessage → 
5. should_continue 判断是否继续 →
6. 再次调用 LLM → 决定是否继续工具调用或终止

```