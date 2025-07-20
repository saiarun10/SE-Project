import yaml
from flask import Flask
from app import create_app  # Import your create_app function

def generate_swagger_yaml():
    # Create the Flask app
    app = create_app()
    
    # Use test client to get the Swagger JSON
    with app.test_client() as client:
        response = client.get('http://127.0.0.1:5000/swagger.json')
        if response.status_code == 200:
            swagger_data = response.get_json()
            
            # Save as YAML
            with open('swagger documentation.yaml', 'w') as f:
                yaml.dump(swagger_data, f, sort_keys=False)
            print("Swagger YAML file generated successfully as 'swagger documentation.yaml'")
        else:
            print(f"Failed to fetch Swagger JSON: {response.status_code}")

if __name__ == "__main__":
    generate_swagger_yaml()