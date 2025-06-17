from langchain_core.messages import HumanMessage
from graphs.main_graph import main_graph
from state.types import MessagesState
from utils.account_utils import load_accounts, parse_instruction

def test_print_job():
    """测试打印任务流程"""
    # 加载账号配置
    accounts = load_accounts()
    
    # 测试指令
    instruction = "用user1打开https://dev.account.sprintray.com/，新建一个indications为crown的打印任务"
    
    # 解析指令
    test_config = parse_instruction(instruction, accounts)
    
    # 初始化状态
    state = {
        "messages": [HumanMessage(content=instruction)],
        "input": instruction,
        "module_intent": "",
        "test_config": test_config
    }
    
    print("开始测试打印任务流程...")
    print(f"测试配置: {test_config}")
    print("\n图的流转信息:")
    
    try:
        # 执行主图
        result = main_graph.invoke(state)
        print("\n测试完成!")
        print(f"最终状态: {result}")
        
        # 打印消息历史
        print("\n对话历史:")
        for msg in result["messages"]:
            print(f"{msg.type}: {msg.content}")
            
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    test_print_job() 