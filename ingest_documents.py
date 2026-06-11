from pathlib import Path

from project.rag.rag_service import RAGService


DOCUMENTS_FOLDER = "project/data/documents"


def main():
    service = RAGService()

    documents_path = Path(DOCUMENTS_FOLDER)

    if not documents_path.exists():
        print(f"Folder does not exist: {DOCUMENTS_FOLDER}")
        return

    supported_extensions = {
        ".txt",
        ".pdf",
        ".docx",
    }

    files = []

    for file_path in documents_path.rglob("*"):
        if (
            file_path.is_file()
            and file_path.suffix.lower() in supported_extensions
        ):
            files.append(file_path)

    if not files:
        print("No supported documents found.")
        return

    print(f"Found {len(files)} document(s).")

    for file_path in files:
        print("-" * 80)
        print(f"Processing: {file_path}")

        result = service.process_document(str(file_path))

        if result.success:
            print(
                f"SUCCESS | id={result.document_id} | file={result.filename}"
            )
        else:
            print(
                f"FAILED | file={result.filename} | error={result.error}"
            )

    print("-" * 80)
    print("Ingestion completed.")


if __name__ == "__main__":
    main()