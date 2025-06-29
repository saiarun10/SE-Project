# Configure Swagger for API documentation of the financial application
swagger_config = {
    "swagger": "2.0",  # Specify OpenAPI version for the API specification
    "title": "Financial Application API",  # Title displayed in Swagger UI
    "uiversion": 3,  # Use Swagger UI version 3 for enhanced interface
    "specs": [
        {
            "endpoint": "apispec_1",  # Name of the API specification
            "route": "/apispec_1.json"  # Endpoint serving the JSON specification
        }
    ],
    "securityDefinitions": {
        "JWT": {  # Define JWT-based authentication for secure endpoints
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Provide JWT token in 'Bearer <token>' format for accessing protected financial endpoints"
        }
    }
}
