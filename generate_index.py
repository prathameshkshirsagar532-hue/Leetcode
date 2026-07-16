import os
import json
from concurrent.futures import ThreadPoolExecutor

EXCLUDE_DIRS = {'.git', '.github', '.vscode', 'node_modules'}

def process_folder(folder_name):
    if os.path.isdir(folder_name) and folder_name not in EXCLUDE_DIRS and not folder_name.startswith('.'):
        parts = folder_name.split('_', 3)
        if len(parts) >= 4:
            q_num_str = parts[0]
            if q_num_str.isdigit():
                try:
                    return {
                        "number": q_num_str,
                        "num_int": int(q_num_str),
                        "topic": parts[1],        # Array, String, etc.
                        "difficulty": parts[2],   # Easy, Medium, Hard
                        "title": parts[3].replace('_', ' '),
                        "path": folder_name.replace('\\', '/')
                    }
                except (ValueError, IndexError):
                    pass
    return None

def build_index():
    all_items = os.listdir('.')
    with ThreadPoolExecutor() as executor:
        results = executor.map(process_folder, all_items)
    
    questions = [r for r in results if r is not None]
    questions.sort(key=lambda x: x['num_int'])
    
    # data.js file generate hogi bina kisi extra HTML mess ke
    js_content = f"const rawQuestionsData = {json.dumps(questions, indent=2)};"
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"⚡ Success! {len(questions)} questions indexed in data.js")

if __name__ == "__main__":
    build_index()
