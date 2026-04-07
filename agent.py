import logging
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, ToolMessage
from tools import search_flights, search_hotels, calculate_budget
from dotenv import load_dotenv

# 0. Cấu hình LOGGING
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TravelBuddyAgent")

load_dotenv()

# 1. Đọc System Prompt
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()


# 2. Khai báo State
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# 3. Khởi tạo LLM và Tools
tools_list = [search_flights, search_hotels, calculate_budget]
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools_list)


# 4. Nodes
def agent_node(state: AgentState):
    messages = state["messages"]
    # Thêm System Prompt vào đầu danh sách tin nhắn nếu chưa có
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = llm_with_tools.invoke(messages)

    # LOGGING ACTIONS
    if response.tool_calls:
        for tc in response.tool_calls:
            logger.info(f"ACTION: Gọi tool '{tc['name']}' với tham số: {tc['args']}")
    else:
        logger.info("ACTION: Trả lời trực tiếp người dùng.")

    return {"messages": [response]}


def tool_node_with_logging(state: AgentState):
    """Wrapper cho ToolNode để log Observation."""
    tool_node = ToolNode(tools_list)
    result = tool_node.invoke(state)

    # LOGGING OBSERVATIONS
    for msg in result["messages"]:
        if isinstance(msg, ToolMessage):
            # Đảm bảo nội dung là chuỗi để log
            content_str = str(msg.content)
            obs_preview = (
                (content_str[:100] + "...") if len(content_str) > 100 else content_str
            )
            logger.info(f"OBSERVATION từ tool: {obs_preview}")

    return result


# 5. Xây dựng Graph
builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node_with_logging)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

graph = builder.compile()

# 6. Chat loop
if __name__ == "__main__":
    print("-" * 50)
    print("TravelBuddy Agent")
    print("-" * 50)

    while True:
        try:
            user_input = input("\nBạn: ").strip()
            if user_input.lower() in ("quit", "exit", "q"):
                break

            if not user_input:
                continue

            # Chạy graph và lấy kết quả cuối cùng
            result = graph.invoke({"messages": [("human", user_input)]})
            final_result = result["messages"][-1]

            print(f"\nTravelBuddy: {final_result.content}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Lỗi thực thi: {e}")
            print("\nTravelBuddy: Có lỗi xảy ra, vui lòng thử lại sau.")
