from flask import request, redirect
import jwt

def token_required(f):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return redirect('/')
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            payload = jwt.decode(token, 'financeteste@', algorithms=["HS256"])
            kwargs['user_id'] = payload['user_id']
            return f(*args, **kwargs)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return redirect('/?error=invalid_token')
    
    wrapper.__name__ = f.__name__
    return wrapper