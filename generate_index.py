import os
import json
import re

def generate_index():
    dataset = []
    base_dir = os.getcwd()
    # Pattern to support formats like "0001_Array_Easy_Two_Sum" safely
    folder_pattern = re.compile(r'^(\d+)_(.+?)_(Easy|Medium|Hard)_(.+)$')

    if not os.path.exists(base_dir):
        print("❌ Error: Working directory not found.")
        return

    for item in sorted(os.listdir(base_dir)):
        item_path = os.path.join(base_dir, item)
        if not os.path.isdir(item_path) or item.startswith('.'):
            continue
            
        match = folder_pattern.match(item)
        if match:
            q_num = match.group(1)
            q_topic = match.group(2).replace('_', ' ')
            q_diff = match.group(3)
            q_title = match.group(4).replace('_', ' ')
            
            code_content = ""
            file_name = ""
            file_ext = ""
            notes_content = ""
            
            try:
                sub_files = os.listdir(item_path)
            except Exception:
                continue
            
            for sub_file in sub_files:
                sub_file_path = os.path.join(item_path, sub_file)
                if os.path.isdir(sub_file_path):
                    continue
                    
                ext = sub_file.split('.')[-1].lower()
                
                if ext == 'md' and (sub_file.lower() == 'readme.md' or 'notes' in sub_file.lower()):
                    try:
                        with open(sub_file_path, 'r', encoding='utf-8') as f:
                            notes_content = f.read()
                    except Exception:
                        notes_content = ""
                elif ext in ['py', 'py3', 'cpp', 'c', 'cs', 'java', 'js', 'ts', 'go', 'rs', 'kt', 'rb', 'sh']:
                    try:
                        with open(sub_file_path, 'r', encoding='utf-8') as f:
                            code_content = f.read()
                            file_name = sub_file
                            file_ext = ext
                    except Exception:
                        pass

            dataset.append({
                "number": q_num,
                "num_int": int(q_num),
                "title": q_title,
                "topic": q_topic,
                "difficulty": q_diff,
                "filename": file_name,
                "extension": file_ext,
                "code": code_content,
                "notes": notes_content
            })

    dataset.sort(key=lambda x: x["num_int"])
    output_js_content = f"const rawQuestionsData = {json.dumps(dataset, indent=4)};"
    
    try:
        with open('data.js', 'w', encoding='utf-8') as out_file:
            out_file.write(output_js_content)
        print(f"✅ Success: Indexed {len(dataset)} questions into data.js!")
    except Exception as e:
        print(f"❌ Error writing data.js: {str(e)}")

if __name__ == "__main__":
    generate_index()
            
