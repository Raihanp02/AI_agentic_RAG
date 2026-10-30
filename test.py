# from app.llm.service.graph.agent_graph import AgenticRAGGraph
# from app.llm.service.llm import OpenRouterLLM
# from app.llm.service.agent_tools.rag_tools import rag_tools
# # from app.llm.service.agent_tools.query_tools import sql_analytics

# # from langgraph.graph import MessagesState, StateGraph

# graph = AgenticRAGGraph(llm_method=OpenRouterLLM(), tools=[rag_tools])

# graph.draw_graph()

# # def start(state: MessagesState):
# #     return {"messages": state.get("messages")}

# # def end(state: MessagesState):
# #     return {"messages": state.get("messages")}

# # res = start({"messages": ["Hello, world!"]})
# # print(res)

# # res = end({"messages": ["Goodbye, world!"]})
# # print(res)

from openpyxl import load_workbook

def excel_structure_to_text(path: str, sheet_name: str = None) -> str:
    wb = load_workbook(path, data_only=True)
    ws = wb[sheet_name] if sheet_name else wb.active

    lines = [f"Sheet: {ws.title}"]
    for row in ws.iter_rows(min_row=1, max_row=min(10, ws.max_row)):  # sample first N rows
        row_values = [str(cell.value) if cell.value is not None else "" for cell in row]
        lines.append(" | ".join(row_values))

    return "\n".join(lines)

structure_text = excel_structure_to_text(r"C:\Users\AQI\Downloads\Manhour Estimation_PT Galliaria Prospera Eterna_Bottle QC Inspection.xlsx")

print("Excel Structure as Text:\n", structure_text)