import os
import subprocess
from openai import OpenAI

def update_client_models(be_files, repo_dir, client_dir="sample/Sample App/Model"):
    """Update client Codable files using OpenAI based on BE model changes."""
    client = OpenAI()

    updated_files = []

    for be_file in be_files:
        be_path = os.path.join("", be_file)
        if not os.path.exists(be_path):
            print(f"❌ Backend model file not found: {be_path}")
            continue

        be_content = open(be_path).read()

        # Derive matching client file name (simple mapping: Foo.swift <-> Foo.swift)
        filename = os.path.basename(be_file).replace(".py", ".swift")  # adjust if BE not python
        client_path = os.path.join(repo_dir, client_dir, "UserModel.swift")
        print(client_path)
        if not os.path.exists(client_path):
            print(f"⚠️ Skipping {filename}, no matching client file found")
            continue

        client_content = open(client_path).read()

        print(f"🔄 Updating client file: {client_path} based on {be_file}")

        completion = client.chat.completions.create(
            model="gpt-4.1",  # or gpt-5 if available
            messages=[
                {"role": "system", "content": "You are an expert Swift developer. Update Codable structs based on backend models."},
                {"role": "user", "content": f"""
                Here is the new backend model definition:
                
                {be_content}
                
                Here is the current Swift Codable file:
                
                {client_content}
                
                Update the Swift Codable structs so they fully match the backend model. Preserve existing formatting and coding style.
                Only return the updated Swift code, nothing else. Do not add any explanations. If there are multiple files then give me 
                the full content of the updated file. I would use following code to write it to back to disk:
                ```python
                new_code = completion.choices[0].message.content.strip()

                with open(client_path, "w") as f:
                    f.write(new_code)

                updated_files.append(client_path)
                ``` Give the output such that the above code can save the changes correctly.
                """}
            ],
        )

        new_code = completion.choices[0].message.content.strip()

        with open(client_path, "w") as f:
            f.write(new_code)

        updated_files.append(client_path)

    return updated_files

update_client_models(["models.py"], "", client_dir="sample/Sample App/Model")