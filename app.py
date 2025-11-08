from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import json
import os
import tempfile
import time
from datetime import datetime
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Ensure yantra files directory exists
YANTRA_FILES_DIR = 'yantra_files'
OUTPUT_DIR = 'yantra_outputs'

os.makedirs(YANTRA_FILES_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_yantra_script(script_path, inputs):
    """
    Run a yantra Python script with given inputs and capture output
    """
    try:
        # Create input string for the script
        input_string = '\n'.join(inputs) + '\n'
        
        # Run the script with inputs
        process = subprocess.Popen(
            ['python', script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(os.path.abspath(script_path))
        )
        
        stdout, stderr = process.communicate(input=input_string, timeout=60)
        
        if process.returncode != 0:
            return {"success": False, "error": f"Script error: {stderr}"}
        
        return {"success": True, "output": stdout, "error": stderr}
        
    except subprocess.TimeoutExpired:
        process.kill()
        return {"success": False, "error": "Script execution timeout"}
    except Exception as e:
        return {"success": False, "error": f"Execution error: {str(e)}"}

def find_generated_files(output_dir, yantra_name):
    """
    Find generated JSON and image files
    """
    json_file = None
    image_file = None
    
    # Look for JSON file    
    possible_json_names = [
        "Samrat_Yantra_Calcs.json",
        "rasi_valya_yantra.json", 
        "dpcy.json",
        "rama_yantra.json",
        "diagsma_yantra.json"
    ]
    
    for filename in os.listdir(output_dir):
        if filename.endswith('.json') and any(name in filename for name in possible_json_names):
            json_file = os.path.join(output_dir, filename)
            break
    
    # Look for image files (PNG, JPG, etc.)
    for filename in os.listdir(output_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')):
            image_file = os.path.join(output_dir, filename)
            break
    
    return json_file, image_file

def encode_image_to_base64(image_path):
    """
    Convert image file to base64 string
    """
    try:
        with open(image_path, 'rb') as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        return None
    
# ====== ROUTE: GENERIC YANTRA RUNNER ======
@app.route('/api/yantra/<yantra_type>', methods=['POST'])
def run_yantra(yantra_type):
    mapping = {
        "samrat": "samrat-yantra",
        "rasivalaya": "rasivalaya-yantra",
        "dhruva": "dhruva-yantra",
        "rama": "rama-yantra",
        "diagsma": "diagsma-yantra",
    }
    if yantra_type not in mapping:
        return jsonify({"success": False, "error": "Invalid yantra type"}), 400

    return run_samrat_yantra() if yantra_type == "samrat" else \
           run_rasivalaya_yantra() if yantra_type == "rasivalaya" else \
           run_dhruva_yantra() if yantra_type == "dhruva" else \
           run_rama_yantra() if yantra_type == "rama" else \
           run_diagsma_yantra()

# ====== ROUTE 1: SAMRAT YANTRA ======
@app.route('/api/samrat-yantra', methods=['POST'])
def run_samrat_yantra():
    """
    Run Samrat Yantra script with provided parameters
    """
    try:
        data = request.get_json()
        
        # Validate required parameters
        required_params = ['latitude', 'longitude', 'scale_m', 'date']
        for param in required_params:
            if param not in data:
                return jsonify({"success": False, "error": f"Missing parameter: {param}"}), 400
        
        # Prepare inputs for the script
        inputs = [
            str(data['latitude']),
            str(data['longitude']),
            str(data['scale_m']),
            data['date']
        ]
        
        # Path to Samrat Yantra script
        script_path = os.path.abspath("yantra_files/Samrat_Yantra_Calcs.py")
        
        if not os.path.exists(script_path):
            return jsonify({"success": False, "error": "Samrat Yantra script not found"}), 404
        
        # Run the script
        result = run_yantra_script(script_path, inputs)
        
        if not result["success"]:
            return jsonify(result), 500
        
        # Find generated files
        json_file, image_file = find_generated_files('.', 'samrat')
        
        response_data = {
            "yantra_type": "samrat",
            "parameters": data,
            "script_output": result["output"],
            "timestamp": datetime.now().isoformat()
        }
        
        # Include JSON data if found
        if json_file and os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    response_data["yantra_data"] = json.load(f)
            except Exception as e:
                response_data["json_error"] = str(e)
        
        # Include image data if found
        if image_file and os.path.exists(image_file):
            image_base64 = encode_image_to_base64(image_file)
            if image_base64:
                response_data["image"] = image_base64
                response_data["image_format"] = os.path.splitext(image_file)[1][1:]
        
        return jsonify({"success": True, "data": response_data})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ====== ROUTE 2: RASIVALAYA YANTRA ======
@app.route('/api/rasivalaya-yantra', methods=['POST'])
def run_rasivalaya_yantra():
    """
    Run Rasivalaya Yantra script with provided parameters
    """
    try:
        data = request.get_json()
        
        required_params = ['latitude', 'longitude', 'scale_m', 'date']
        for param in required_params:
            if param not in data:
                return jsonify({"success": False, "error": f"Missing parameter: {param}"}), 400
        
        inputs = [
            str(data['latitude']),
            str(data['longitude']),
            str(data['scale_m']),
            data['date']
        ]
        
        script_path = os.path.abspath("yantra_files/rasi_valya_yantra.py")
        
        if not os.path.exists(script_path):
            return jsonify({"success": False, "error": "Rasivalaya Yantra script not found"}), 404
        
        result = run_yantra_script(script_path, inputs)
        
        if not result["success"]:
            return jsonify(result), 500
        
        json_file, image_file = find_generated_files('.', 'rasivalaya')
        
        response_data = {
            "yantra_type": "rasivalaya",
            "parameters": data,
            "script_output": result["output"],
            "timestamp": datetime.now().isoformat()
        }
        
        if json_file and os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    response_data["yantra_data"] = json.load(f)
            except Exception as e:
                response_data["json_error"] = str(e)
        
        if image_file and os.path.exists(image_file):
            image_base64 = encode_image_to_base64(image_file)
            if image_base64:
                response_data["image"] = image_base64
                response_data["image_format"] = os.path.splitext(image_file)[1][1:]
        
        return jsonify({"success": True, "data": response_data})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ====== ROUTE 3: DHRUVA-PROTHA-CHAKRA YANTRA ======
@app.route('/api/dhruva-yantra', methods=['POST'])
def run_dhruva_yantra():
    """
    Run Dhruva-Protha-Chakra Yantra script with provided parameters
    """
    try:
        data = request.get_json()
        
        required_params = ['latitude', 'longitude', 'scale_m', 'date', 'time']
        for param in required_params:
            if param not in data:
                return jsonify({"success": False, "error": f"Missing parameter: {param}"}), 400
        
        inputs = [
            str(data['latitude']),
            str(data['longitude']),
            str(data['scale_m']),
            data['date'],
            data['time']
        ]
        
        script_path = os.path.abspath("yantra_files/dpcy_yantra.py")
        
        if not os.path.exists(script_path):
            return jsonify({"success": False, "error": "Dhruva-Protha-Chakra Yantra script not found"}), 404
        
        result = run_yantra_script(script_path, inputs)
        
        if not result["success"]:
            return jsonify(result), 500
        
        json_file, image_file = find_generated_files('.', 'dhruva')
        
        response_data = {
            "yantra_type": "dhruva_protha_chakra",
            "parameters": data,
            "script_output": result["output"],
            "timestamp": datetime.now().isoformat()
        }
        
        if json_file and os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    response_data["yantra_data"] = json.load(f)
            except Exception as e:
                response_data["json_error"] = str(e)
        
        if image_file and os.path.exists(image_file):
            image_base64 = encode_image_to_base64(image_file)
            if image_base64:
                response_data["image"] = image_base64
                response_data["image_format"] = os.path.splitext(image_file)[1][1:]
        
        return jsonify({"success": True, "data": response_data})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ====== ROUTE 4: RAMA YANTRA ======
@app.route('/api/rama-yantra', methods=['POST'])
def run_rama_yantra():
    """
    Run Rama Yantra script with provided parameters
    """
    try:
        data = request.get_json()
        
        required_params = ['latitude', 'longitude', 'scale_m', 'date', 'time']
        for param in required_params:
            if param not in data:
                return jsonify({"success": False, "error": f"Missing parameter: {param}"}), 400
        
        inputs = [
            str(data['latitude']),
            str(data['longitude']),
            str(data['scale_m']),
            data['date'],
            data['time']
        ]
        
        script_path = os.path.abspath("yantra_files/rama_yantra.py")
        
        if not os.path.exists(script_path):
            return jsonify({"success": False, "error": "Rama Yantra script not found"}), 404
        
        result = run_yantra_script(script_path, inputs)
        
        if not result["success"]:
            return jsonify(result), 500
        
        json_file, image_file = find_generated_files('.', 'rama')
        
        response_data = {
            "yantra_type": "rama",
            "parameters": data,
            "script_output": result["output"],
            "timestamp": datetime.now().isoformat()
        }
        
        if json_file and os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    response_data["yantra_data"] = json.load(f)
            except Exception as e:
                response_data["json_error"] = str(e)
        
        if image_file and os.path.exists(image_file):
            image_base64 = encode_image_to_base64(image_file)
            if image_base64:
                response_data["image"] = image_base64
                response_data["image_format"] = os.path.splitext(image_file)[1][1:]
        
        return jsonify({"success": True, "data": response_data})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
# ====== ROUTE 5: DIAGSMA YANTRA ======
@app.route('/api/diagsma_yantra', methods=['POST'])
def run_diagsma_yantra():
    """
    Run Diagsma Yantra script with provided parameters
    """
    try:
        data = request.get_json()
        
        required_params = ['latitude', 'longitude', 'scale_m', 'date', 'time']
        for param in required_params:
            if param not in data:
                return jsonify({"success": False, "error": f"Missing parameter: {param}"}), 400
        
        inputs = [
            str(data['latitude']),
            str(data['longitude']),
            str(data['scale_m']),
            data['date'],
            data['time']
        ]
        
        script_path = os.path.abspath("yantra_files/diagsma_yantra.py")
        
        if not os.path.exists(script_path):
            return jsonify({"success": False, "error": "Diagsma Yantra script not found"}), 404
        
        result = run_yantra_script(script_path, inputs)
        
        if not result["success"]:
            return jsonify(result), 500
        
        json_file, image_file = find_generated_files('.', 'diagsma')
        
        response_data = {
            "yantra_type": "diagsma",
            "parameters": data,
            "script_output": result["output"],
            "timestamp": datetime.now().isoformat()
        }
        
        if json_file and os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    response_data["yantra_data"] = json.load(f)
            except Exception as e:
                response_data["json_error"] = str(e)
        
        if image_file and os.path.exists(image_file):
            image_base64 = encode_image_to_base64(image_file)
            if image_base64:
                response_data["image"] = image_base64
                response_data["image_format"] = os.path.splitext(image_file)[1][1:]
        
        return jsonify({"success": True, "data": response_data})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ====== HEALTH CHECK & INFO ROUTES ======
@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "available_yantras": [
            "samrat-yantra",
            "rasivalaya-yantra", 
            "dhruva-yantra",
            "rama-yantra"
        ]
    })

@app.route('/api/yantras', methods=['GET'])
def list_yantras():
    """
    List all available yantra endpoints with their required parameters
    """
    yantras = {
        "samrat-yantra": {
            "endpoint": "/api/samrat-yantra",
            "method": "POST",
            "description": "Samrat Yantra - Solar time measurement instrument",
            "required_parameters": {
                "latitude": "float (e.g., 28.6139)",
                "longitude": "float (e.g., 77.2090)",
                "scale_m": "float (e.g., 3.0)",
                "date": "string YYYY-MM-DD (e.g., '2024-01-15')"
            },
            "script_file": "samrat_yantra.py"
        },
        "rasivalaya-yantra": {
            "endpoint": "/api/rasivalaya-yantra", 
            "method": "POST",
            "description": "Rasivalaya Yantra - Zodiac position tracking instrument",
            "required_parameters": {
                "latitude": "float (e.g., 28.6139)",
                "longitude": "float (e.g., 77.2090)", 
                "scale_m": "float (e.g., 5.0)",
                "date": "string YYYY-MM-DD (e.g., '2024-01-15')"
            },
            "script_file": "rasivalaya_yantra.py"
        },
        "dhruva-yantra": {
            "endpoint": "/api/dhruva-yantra",
            "method": "POST", 
            "description": "Dhruva-Protha-Chakra Yantra - Polaris tracking instrument",
            "required_parameters": {
                "latitude": "float (e.g., 28.6139)",
                "longitude": "float (e.g., 77.2090)",
                "scale_m": "float (e.g., 4.0)",
                "date": "string YYYY-MM-DD (e.g., '2024-01-15')",
                "time": "string HH:MM (e.g., '20:30')"
            },
            "script_file": "dhruva_protha_chakra_yantra.py"
        },
        "rama-yantra": {
            "endpoint": "/api/rama-yantra",
            "method": "POST",
            "description": "Rama Yantra - Altitude measurement instrument", 
            "required_parameters": {
                "latitude": "float (e.g., 28.6139)",
                "longitude": "float (e.g., 77.2090)",
                "scale_m": "float (e.g., 3.0)",
                "date": "string YYYY-MM-DD (e.g., '2024-01-15')",
                "time": "string HH:MM (e.g., '14:30')"
            },
            "script_file": "rama_yantra.py"
        },
        "diagsma-yantra": {
            "endpoint": "/api/diagsma-yantra",
            "method": "POST",
            "description": "Diagsma Yantra - Altitude measurement instrument", 
            "required_parameters": {
                "latitude": "float (e.g., 28.6139)",
                "longitude": "float (e.g., 77.2090)",
                "scale_m": "float (e.g., 3.0)",
                "date": "string YYYY-MM-DD (e.g., '2024-01-15')",
                "time": "string HH:MM (e.g., '14:30')"
            },
            "script_file": "diagsma.py"
        }
    }
    
    # Check which script files exist
    for yantra_name, yantra_info in yantras.items():
        script_path = os.path.join(YANTRA_FILES_DIR, yantra_info["script_file"])
        yantra_info["script_exists"] = os.path.exists(script_path)
        yantra_info["script_path"] = script_path
    
    return jsonify({
        "available_yantras": yantras,
        "total_count": len(yantras),
        "yantra_files_directory": YANTRA_FILES_DIR,
        "output_directory": OUTPUT_DIR
    })

@app.route('/api/yantra/<yantra_type>/example', methods=['GET'])
def get_example_request(yantra_type):
    """
    Get example request for a specific yantra type
    """
    examples = {
        "samrat": {
            "url": f"{request.host_url}api/samrat-yantra",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": {
                "latitude": 28.6139,
                "longitude": 77.2090,
                "scale_m": 3.0,
                "date": "2024-01-15"
            }
        },
        "rasivalaya": {
            "url": f"{request.host_url}api/rasivalaya-yantra",
            "method": "POST", 
            "headers": {"Content-Type": "application/json"},
            "body": {
                "latitude": 28.6139,
                "longitude": 77.2090,
                "scale_m": 5.0,
                "date": "2024-06-21"
            }
        },
        "dhruva": {
            "url": f"{request.host_url}api/dhruva-yantra",
            "method": "POST",
            "headers": {"Content-Type": "application/json"}, 
            "body": {
                "latitude": 28.6139,
                "longitude": 77.2090,
                "scale_m": 4.0,
                "date": "2024-01-15",
                "time": "20:30"
            }
        },
        "rama": {
            "url": f"{request.host_url}api/rama-yantra",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": {
                "latitude": 28.6139,
                "longitude": 77.2090, 
                "scale_m": 3.0,
                "date": "2024-01-15",
                "time": "14:30"
            }
        },
        "diagsma": {
            "url": f"{request.host_url}api/diagsma-yantra",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": {
                "latitude": 28.6139,
                "longitude": 77.2090, 
                "scale_m": 3.0,
                "date": "2024-01-15",
                "time": "14:30"
            }
        }
    }

# ====== FILE MANAGEMENT ROUTES ======
@app.route('/api/upload-yantra-script', methods=['POST'])
def upload_yantra_script():
    """
    Upload a yantra Python script file
    """
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        if not file.filename.endswith('.py'):
            return jsonify({"success": False, "error": "Only Python files (.py) are allowed"}), 400
        
        # Save the file
        filename = file.filename
        filepath = os.path.join(YANTRA_FILES_DIR, filename)
        file.save(filepath)
        
        return jsonify({
            "success": True,
            "message": f"Script {filename} uploaded successfully",
            "filepath": filepath,
            "size": os.path.getsize(filepath)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/yantra-files', methods=['GET'])
def list_yantra_files():
    """
    List all yantra script files in the directory
    """
    try:
        files = []
        if os.path.exists(YANTRA_FILES_DIR):
            for filename in os.listdir(YANTRA_FILES_DIR):
                if filename.endswith('.py'):
                    filepath = os.path.join(YANTRA_FILES_DIR, filename)
                    files.append({
                        "filename": filename,
                        "size": os.path.getsize(filepath),
                        "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                    })
        
        return jsonify({
            "yantra_files": files,
            "count": len(files),
            "directory": YANTRA_FILES_DIR
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ====== ERROR HANDLERS ======
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "/api/health",
            "/api/yantras",
            "/api/samrat-yantra",
            "/api/rasivalaya-yantra", 
            "/api/dhruva-yantra",
            "/api/rama-yantra"
            "/api/diagsma-yantra"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

# ====== MAIN ENTRY POINT ======
if __name__ == '__main__':
    print("🚀 Starting Yantra Flask Backend...")
    print(f"📁 Yantra files directory: {YANTRA_FILES_DIR}")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print("🌐 Available endpoints:")
    print("   GET  /api/health")
    print("   GET  /api/yantras") 
    print("   POST /api/samrat-yantra")
    print("   POST /api/rasivalaya-yantra")
    print("   POST /api/dhruva-yantra")
    print("   POST /api/rama-yantra")
    print("   POST /api/diagsma-yantra")
    print("   POST /api/upload-yantra-script")
    print("   GET  /api/yantra-files")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)