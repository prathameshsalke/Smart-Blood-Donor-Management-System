"""
Error Handlers - Custom error pages and handlers
"""

from flask import render_template, request, jsonify
from werkzeug.exceptions import HTTPException
from app.utils.logger import logger

def register_error_handlers(app):
    """Register error handlers with the app"""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 Bad Request"""
        logger.warning(f"400 error: {error.description}")
        
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': error.description or 'Bad request'
            }), 400
        
        return render_template('errors/400.html', error=error), 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        """Handle 401 Unauthorized"""
        logger.warning(f"401 error: {error.description}")
        
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'code': 401,
                'message': 'Authentication required'
            }), 401
        
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 Forbidden"""
        logger.warning(f"403 error: {error.description}")
        
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'code': 403,
                'message': 'Access forbidden'
            }), 403
        
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found"""
        logger.info(f"404 error: {request.path}")
        
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': 'Resource not found'
            }), 404
        
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(405)
    def method_not_allowed_error(error):
        """Handle 405 Method Not Allowed"""
        logger.warning(f"405 error: {error.description}")
        
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'code': 405,
                'message': f'Method {request.method} not allowed'
            }), 405
        
        return render_template('errors/405.html'), 405
    
    @app.errorhandler(408)
    def request_timeout_error(error):
        """Handle 408 Request Timeout"""
        logger.error(f"408 error: {error.description}")
        
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'code': 408,
                'message': 'Request timeout'
            }), 408
        
        return render_template('errors/408.html'), 408
    
    @app.errorhandler(413)
    def request_entity_too_large_error(error):
        """Handle 413 Request Entity Too Large"""
        logger.warning(f"413 error: File too large")
        
        max_size = app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024) / (1024 * 1024)
        
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'code': 413,
                'message': f'File too large. Maximum size is {max_size}MB'
            }), 413
        
        return render_template('errors/413.html', max_size=max_size), 413
    
    @app.errorhandler(429)
    def too_many_requests_error(error):
        """Handle 429 Too Many Requests"""
        logger.warning(f"429 error: Rate limit exceeded")
        
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'code': 429,
                'message': 'Too many requests. Please try again later.'
            }), 429
        
        return render_template('errors/429.html'), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error"""
        logger.error(f"500 error: {str(error)}", exc_info=True)
        
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'code': 500,
                'message': 'Internal server error'
            }), 500
        
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(502)
    def bad_gateway_error(error):
        """Handle 502 Bad Gateway"""
        logger.error(f"502 error: {error.description}")
        
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'code': 502,
                'message': 'Bad gateway'
            }), 502
        
        return render_template('errors/502.html'), 502
    
    @app.errorhandler(503)
    def service_unavailable_error(error):
        """Handle 503 Service Unavailable"""
        logger.error(f"503 error: {error.description}")
        
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'code': 503,
                'message': 'Service temporarily unavailable'
            }), 503
        
        return render_template('errors/503.html'), 503
    
    @app.errorhandler(504)
    def gateway_timeout_error(error):
        """Handle 504 Gateway Timeout"""
        logger.error(f"504 error: {error.description}")
        
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'code': 504,
                'message': 'Gateway timeout'
            }), 504
        
        return render_template('errors/504.html'), 504
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle any HTTP exception"""
        logger.error(f"HTTP {error.code}: {error.description}")
        
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'code': error.code,
                'message': error.description
            }), error.code
        
        return render_template(f'errors/{error.code}.html', error=error), error.code
    
    @app.errorhandler(Exception)
    def handle_unhandled_exception(error):
        """Handle any unhandled exception"""
        logger.critical(f"Unhandled exception: {str(error)}", exc_info=True)
        
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'code': 500,
                'message': 'An unexpected error occurred'
            }), 500
        
        return render_template('errors/500.html'), 500