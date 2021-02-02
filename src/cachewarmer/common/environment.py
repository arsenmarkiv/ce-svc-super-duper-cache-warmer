import os


class Variables:
    def __init__(self, logger_name='load'):
        default_debug_mode = '1'
        default_environment = 'production'
        default_host = 'localhost'
        default_secret_key = 'test_key'
        default_port = 6012
        default_url_prefix = '/svc-appstm-da-cachemanager'
        default_auth_tenant = "test-tenent"
        default_tenant_id = os.environ.get('tenant_id', '')
        default_service_name = 'svc-appstm-da-cachemanager'

        self.debug_mode = os.environ.get('FLASK_DEBUG', default_debug_mode)
        self.environment = os.environ.get('FLASK_ENV', default_environment)
        self.host = os.environ.get('FLASK_HOST', default_host)
        self.port = os.environ.get('FLASK_PORT', default_port)
        self.secret_key = os.environ.get('SECRET_KEY', default_secret_key)
        self.url_prefix = os.environ.get('URL_PREFIX', default_url_prefix)
        self.auth_tenant = os.environ.get('AUTH_TENANT', default_auth_tenant)
        self.tenant_id = os.environ.get('AZURE_AD_TENANT_ID',
                                        default_tenant_id)
        self.allowed_origin = os.environ.get('ALLOWED_ORIGIN',
                                             'http://localhost:3000')
        self.service_name = os.environ.get('service_name',
                                           default_service_name)
