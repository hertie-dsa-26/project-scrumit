import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = False
    TESTING = False
    
class DevelopmentConfig(Config):
    """Development environment"""
    DEBUG = True
    
class TestingConfig(Config):
    """Testing environment"""
    TESTING = True
