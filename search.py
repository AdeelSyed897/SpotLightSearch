import subprocess
from src.search_engine import SearchEngine


engine = SearchEngine()

print("SpotLight Search")
print('Use : for semantic search')
print('Use " for keyword search')
print('Type :q to quit')

while True:
    raw_query = input("\nSearch: ").strip()

    if raw_query == ":q":
        break

    if not raw_query:
        continue

    if raw_query.startswith(":"):
        query = raw_query[1:].strip()

        if not query:
            print("Enter a semantic query after :")
            continue

        results = engine.semantic_search(query)

    elif raw_query.startswith('"'):
        query = raw_query[1:].strip()

        if not query:
            print('Enter a keyword query after "')
            continue

        results = engine.keyword_search(query)

    else:
        print('Use : for semantic search or " for keyword search.')
        continue


    print("DEBUG RESULTS:", results)


    if not results:
        print("No matching files found.")
        continue

    for i, file_path in enumerate(results, start=1):
        print(f"{i}. {file_path}")

    subprocess.run(["open", results[0]])