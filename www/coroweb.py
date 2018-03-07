import functools
import inspect
 
def get(path):
    '''
    Define decorator @get('/path')
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args,**kw):
            return func
        wrapper.__route__ = path
        wrapper.__method__ = 'GET'
        return wrapper
    return decorator
#通过传参可将装饰器定义成get,post,put,delete中的任何一种
#get = functools.partial(Handler_decorator,'GET')

def post(path):
    '''
    Define decorator @post('/path')
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args,**kw):
            return func
        wrapper.__route__ = path
        wrapper.__method__ = 'POST'
        return wrapper
    return decorator

#获取无默认值的命名关键字参数
def get_required_kw_args(fn):
    global args
    args = []
    #得到映射类型对象，是有序的dict类型
    params = inspect.signature(fn).parameters
    for name,param in params.items():
        #inspect.Parameter对象kind属性是_ParameterKind枚举类型对象，说明参数值通过什么绑定到参数;'此处表示参数仅通过关键字绑定到参数
        if str(param.kind)=='KEYWORD_ONLY' and param.default==inspect.Parameter.empty:
            args.append(name)
        return tuple(args)
    
#获取命名关键字参数
def get_named_kw_args(fn):
    params = inspect.signature(fn).parameters
    for name,param in params.items():
        if str(param.kind)=='KEYWORD_ONLY':
            args.append(param)
        return args
    
#判断有无命名关键字参数
def has_named_kw_args(fn):
    params = inspect.signature(fn).parameters
    for name,param in params.items():
        if not str(param.kind)=='KEYWORD_ONLY':
            return False
        return True
    
#判断有无关键字参数
def has_var_kw_args(fn):
    params = inspect.signature(fn).parameters
    for name,param in params.items():
        if str(name.kind)=='VAR_KEYWORD':
            return True
        
 #判断是否含有名叫'request'参数，且该参数是否为最后一个参数
def has_request_arg(fn):
    params = inspect.signature(fn).parameters
    sig = inspect.signature(fn)
    found = False
    for name,param in params.items():
        #先判断参数中是否有'REQUEST'
        if name == 'request':
            found = True
            continue
        #再判断有'有request'参数情况下
        if found and ((str(name.kind)!='VAR_KEYWORD' and str(name.kind)!='VAR_POSITIONAL' and str(param.kind)!='KEYWORD_ONLY')):
            raise ValueError('request parameter must be the last named parameter in func:%s%s'%(fn.__name__,str(sig)))
        return found