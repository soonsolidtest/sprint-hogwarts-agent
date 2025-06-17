import re
import yaml
from langchain_core.messages import HumanMessage
from graphs.rayware_graph import rayware_module_graph

# 读取账号配置
def load_accounts():
    with open("config/rayware_accounts.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["accounts"]

def parse_instruction(instruction, accounts):
    # 解析网址
    url_match = re.search(r"@([\w\-:\/.]+)", instruction)
    url = url_match.group(1) if url_match else None
    # 解析账号描述
    user_match = re.search(r"用(\w+)登录", instruction)
    user_desc = user_match.group(1) if user_match else None
    # 解析Indications
    ind_match = re.search(r"Indications为([\w\u4e00-\u9fa5]+)", instruction)
    indications = ind_match.group(1) if ind_match else "crown"
    # 匹配账号
    account = None
    if user_desc:
        for acc in accounts:
            if acc["description"] == user_desc:
                account = acc
                break
    if not account:
        account = accounts[0]  # 默认第一个
    # url优先指令，否则用账号配置
    final_url = url if url else account["url"]
    return {
        "url": final_url,
        "username": account["username"],
        "password": account["password"],
        "auto_intent": "new_print_job",
        "print_job_config": {
            "Indications": indications,
            "Orientation": "default",
            "Printer": "default",
            "Material": "default"
        }
    }

def main():
    accounts = load_accounts()
    # 支持命令行输入或直接写死
    try:
        instruction = input("请输入测试指令（如：我要打开@https://dev.account.sprintray.com/ 网址，用user1登录测试新建打印任务，Indications为crown）：\n")
    except Exception:
        instruction = "用user1登录测试新建打印任务，Indications为crown"
    test_config = parse_instruction(instruction, accounts)
    state = {
        "messages": [HumanMessage(content=instruction)],
        "test_config": test_config
    }
    print("开始测试Rayware流程...")
    print(f"测试配置: {test_config}")
    # 打印图的流转信息
    print("\n图的流转信息:")
    for node in rayware_module_graph.nodes:
        print(f"节点: {node}")
        input_state = state.copy()
        output_state = rayware_module_graph.nodes[node].invoke(input_state)
        print(f"输入状态: {input_state}")
        print(f"输出状态: {output_state}")
    try:
        result = rayware_module_graph.invoke(state)
        print("\n测试完成!")
        print(f"最终状态: {result}")
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main() 