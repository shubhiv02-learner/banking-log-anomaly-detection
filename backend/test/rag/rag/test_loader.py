from backend.rag.loaders.loader import DocumentLoader


def main():
    loader = DocumentLoader()

    documents = loader.load_documents()

    print(f"\nFound {len(documents)} documents\n")

    for doc in documents:
        print(doc)


if __name__ == "__main__":
    main()