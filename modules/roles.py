from flask import session, redirect

def role_required(*roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if "role" not in session:
                return redirect("/")
            
            if session["role"] not in roles:
                return "Unauthorized Access", 403
            
            return func(*args, **kwargs)

        wrapper.__name__ = func.__name__
        return wrapper
    return decorator
