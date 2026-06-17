from project.graph_agent.data_reader_graph import DataReaderGraph


def print_result(state):
    print("\n========== FINAL ANSWER ==========")
    print(state["final_answer"])

    print("\n========== MESSAGES ==========")
    for message in state["messages"]:
        print(f"{message['role']}: {message['content']}")

    print("\n========== DEBUG ==========")
    print(f"current_agent={state['current_agent']}")
    print(f"retry_count={state['retry_count']}")
    print(f"error={state['error']}")
    print(f"documents_found={len(state['documents_found'])}")


def main():
    graph = DataReaderGraph()

    questions = [
        "Search in my documents: what is the termination notice?",
        "Search in my documents: who is the supplier?",
        "Search in my documents: what is the refund policy?",
        "What is the capital of France?",
    ]

    for question in questions:
        print("\n" + "=" * 100)
        print(f"USER QUESTION: {question}")

        state = graph.run(question)
        print_result(state)


if __name__ == "__main__":
    main()
