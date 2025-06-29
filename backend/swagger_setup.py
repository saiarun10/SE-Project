from flask_restx import Api

def configure_swagger(app):
    """
    Configure Flask-RESTx API with BearerAuth security scheme.
    """
    api = Api(
        app,
        version='1.0',
        title='Financial Literacy App API',
        description='API for a financial literacy app for children aged 8-14',
        doc='/doc/',
        security='BearerAuth',
        authorizations={
            'BearerAuth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'Enter your JWT token with the `Bearer ` prefix, e.g., "Bearer <your_token>"'
            }
        }
    )
    return api