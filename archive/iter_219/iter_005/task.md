This task is to fix a file encoding error in a JSON file.

1.  The file at `archive/iter_218/results/champion_rule.json` has a UTF-8 decoding error.
2.  Read this file using a robust method. For example, open it in binary mode (`'rb'`) and then decode the bytestring into a string using `bytes.decode('utf-8', errors='replace')`.
3.  Parse the resulting string as JSON to ensure it is valid.
4.  Create a new, clean file at `archive/iter_219/results/g4_rule_083_cleaned.json`.
5.  Write the parsed JSON data into this new file using standard UTF-8 encoding.
6.  The task is successful if the new file is created and is a valid JSON file.
7.  Report `status: ok` and add an artifact entry for the newly created file.