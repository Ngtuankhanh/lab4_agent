This repo demo how to use Langraph for Tool Calling

You can test using run_tests.py below:

```python
from agent import graph
from langchain_core.messages import HumanMessage

def run_test(test_num, query):
    print(f"\n{'='*20} Test {test_num} {'='*20}")
    print(f"User: {query}")
    print("\nProcessing...")
    
    # Run the graph
    result = graph.invoke({"messages": [HumanMessage(content=query)]})
    
    # Extract the final response
    final_message = result["messages"][-1]
    
    print(f"\nTravelBuddy: {final_message.content}")
    print("=" * 50)

if __name__ == "__main__":
    test_cases = [
        "Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu.",
        "Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng",
        "Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!",
        "Tôi muốn đặt khách sạn",
        "Giải giúp tôi bài tập lập trình Python về linked list"
    ]
    
    for i, query in enumerate(test_cases, 1):
        run_test(i, query)
