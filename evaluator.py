
def precision_calc(retrieved_documents, relevant_documents):
    num = len(set(retrieved_documents).intersection(relevant_documents))
    denom = len(set(retrieved_documents))
    return num/(denom+1e-06)


def recall_calc(retrieved_documents, relevant_documents):
    num = len(set(retrieved_documents).intersection(relevant_documents))
    denom = len(set(relevant_documents))
    return num/(denom+1e-06)
