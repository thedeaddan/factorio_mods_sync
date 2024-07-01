from flask import Flask, jsonify, send_from_directory, abort
import os

app = Flask(__name__)

# Путь к папке, содержимое которой будет предоставляться
DIRECTORY = '/opt/factorio/mods'

def get_all_files(directory):
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), directory)
            file_list.append(relative_path)
    return file_list

@app.route('/files', methods=['GET'])
def list_files():
    try:
        files = get_all_files(DIRECTORY)
        return jsonify(files)
    except FileNotFoundError:
        return jsonify([]), 404

@app.route('/files/<path:filename>', methods=['GET'])
def get_file(filename):
    try:
        file_path = os.path.join(DIRECTORY, filename)
        if os.path.isfile(file_path):
            directory = os.path.dirname(file_path)
            return send_from_directory(directory, os.path.basename(file_path))
        else:
            abort(404, description=f"File {filename} not found in {DIRECTORY}")
    except Exception as e:
        abort(500, description=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
