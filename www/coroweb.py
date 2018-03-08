import functools,inspect,asyncio,json,logging
from aiohttp import web
from urllib import parse
from www.APIError import APIError

logging.basicConfig(level=logging.INFO)
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

class RequestHandler(object):
    def __init__(self,fn,app):
        self._app = app
        self._fn = fn
        self._get_required_kw_args = get_required_kw_args(fn)
        self._get_named_kw_args = get_named_kw_args(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._has_var_kw_args = has_var_kw_args(fn)
        self._has_request_kw_args = has_request_arg(fn)
    #构造协程
    async def __call__(self,request):
        kw=None
        if self._has_var_kw_args or self._get_required_kw_args or self._has_named_kw_args:
            if request['method']=='POST':
                if not request['content_type']:
                    return web.HTTPBadRequest(text='Missing content_type')
                ct = request['content_type'].lower()
                
                if ct.startwith('application/json'):
                    params = await request.json()
                    if not isinstance(params,dict):
                        return web.HTTPBadRequest('JSON body must be dict_obj')
                    kw = params
                    
                elif ct.startwith('application/x-www-form-urlencode')or ct.startwith('mutilpart/form-data'):
                    params = request.post()
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest('Unsupported Content_type:%s'%request['content_type'])
            
            if request['method']=='GET':
                qs = request.query_string()
                if qs:
                    kw = dict()
                    for k,v in parse.parse_qs(qs,True).item():
                        kw[k]=v[0]
        if kw is None:
            kw = dict(**request.match.info)
        else:
            #移除所有非命名关键字参数
            if not self._has_var_kw_args and self._get_named_kw_args:
                copy = dict()
                for name in self._get_named_kw_args:
                    if name in kw:
                        copy[name]=kw[name]
                    kw=copy
                for k,v in request.match.info.items():
                    if k in kw:
                        logging.warning(web.HTTPBadRequest('Duplicate arg name in named arg and kw args:%s'%k))
                        kw[k]=v
        if self._has_request_kw_args:
            kw['request']=request
        if self._get_required_kw_args:
            if name not in kw:
                return web.HTTPBadRequest('Missing argument:%s'%name)
        logging.info('call with args:%'%str(kw))
        try:
            test = await self._fn(**kw)
            return test
        except APIError as e:
            return dict(error=e.error,data=e.data,message=e.message)