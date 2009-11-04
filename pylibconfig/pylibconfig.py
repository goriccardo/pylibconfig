# Author: Riccardo Gori <goriccardo@gmail.com>
# License: GPL-3 http://www.gnu.org/licenses/gpl.txt

from ctypes import c_long, c_longlong, c_double, c_short, c_int, POINTER, \
                   byref, CDLL, c_void_p, c_char_p, Structure, Union, \
                   CFUNCTYPE, c_uint

class config_list_t(Structure): pass
class config_setting_t(Structure): pass
class config_t(Structure): pass

class config_value_t(Union):
    _fields_ = [('ival', c_long),
                ('llval',c_longlong),
                ('fval', c_double),
                ('sval', c_char_p),
                ('list', POINTER(config_list_t))]

config_setting_t._fields_ = [('name', c_char_p),
                            ('type', c_short),
                            ('format', c_short),
                            ('value', config_value_t),
                            ('parent', POINTER(config_setting_t)),
                            ('config', POINTER(config_t)),
                            ('hook', c_void_p),
                            ('line', c_uint)]

class py_config_setting(object):
    def __init__(self, config_setting, pyparent):
        self._cfg_set = config_setting
        self._pyparent = pyparent

    def __str__(self):
        parent = self._cfg_set
        name = parent.contents.name
        parent = parent.contents.parent
        pname = parent.contents.name
        while pname:
            name = pname + '.' + name
            parent = parent.contents.parent
            pname = parent.contents.name
        return name

    __repr__ = __str__

    def __getattr__(self, name):
        parent = self._cfg_set
        pname = parent.contents.name
        while pname:
            name = pname + '.' + name
            parent = parent.contents.parent
            pname = parent.contents.name
        return self._pyparent.__getattr__(name)

config_list_t._fields_ = [('length', c_uint),
                          ('capacity', c_uint),
                          ('elements', POINTER(POINTER(config_setting_t)))]

config_t._fields_ = [('root', POINTER(config_setting_t)),
                     ('destructor', POINTER(CFUNCTYPE(None, c_void_p))),
                     ('flags', c_int),
                     ('error_text', c_char_p),
                     ('error_line', c_int)]

class group(type): pass
class array(list): pass

class libconfigFile(object):
    #Defines
    CONFIG_TRUE        = 1
    CONFIG_FALSE       = 0
    #Types defs
    CONFIG_TYPE_NONE   = 0
    CONFIG_TYPE_GROUP  = 1
    CONFIG_TYPE_INT    = 2
    CONFIG_TYPE_INT64  = 3
    CONFIG_TYPE_FLOAT  = 4
    CONFIG_TYPE_STRING = 5
    CONFIG_TYPE_BOOL   = 6
    CONFIG_TYPE_ARRAY  = 7
    CONFIG_TYPE_LIST   = 8
    _typedict = {CONFIG_TYPE_NONE:None,
                 CONFIG_TYPE_GROUP:group,
                 CONFIG_TYPE_INT:int,
                 CONFIG_TYPE_INT64:long,
                 CONFIG_TYPE_FLOAT:float,
                 CONFIG_TYPE_STRING:str,
                 CONFIG_TYPE_BOOL:bool,
                 CONFIG_TYPE_ARRAY:array,
                 CONFIG_TYPE_LIST:list}
    def __init__(self, filename=None, new=False):
        """Warning! If new is True the file will be overwritten"""
        self._config = config_t()
        self._load_library()
        self._config_init(byref(self._config))
        if filename and not new:
            self.open(filename)
        self._openfile = filename

    def _load_library(self):
        libconfig = CDLL('libconfig.so')
        #Init
        self._config_init = libconfig.config_init
        #Destroy
        self._config_destroy = libconfig.config_destroy
        #Read
        self._config_read_file = libconfig.config_read_file
        self._config_read = libconfig.config_read
        #Write
        self._config_write_file = libconfig.config_write_file
        #Get array element
        self._config_setting_get_elem = libconfig.config_setting_get_elem
        self._config_setting_get_elem.restype = POINTER(config_setting_t)
        self._config_setting_length = libconfig.config_setting_length
        #Generic
        self._config_lookup = libconfig.config_lookup
        self._config_lookup.restype = POINTER(config_setting_t)
        #From settings
        self._config_setting_get_member = libconfig.config_setting_get_member
        self._config_setting_get_member.restype = POINTER(config_setting_t)
        #Getters
        self._config_setting_get_int = libconfig.config_setting_get_int
        self._config_setting_get_int.restype = c_long
        self._config_setting_get_int64 = libconfig.config_setting_get_int64
        self._config_setting_get_int64.restype = c_longlong
        self._config_setting_get_float = libconfig.config_setting_get_float
        self._config_setting_get_float.restype = c_double
        self._config_setting_get_bool = libconfig.config_setting_get_bool
        self._config_setting_get_string = libconfig.config_setting_get_string
        self._config_setting_get_string.restype = c_char_p
        #Setters
        self._config_setting_set_int = libconfig.config_setting_set_int
        self._config_setting_set_int64 = libconfig.config_setting_set_int64
        self._config_setting_set_float = libconfig.config_setting_set_float
        self._config_setting_set_bool = libconfig.config_setting_set_bool
        self._config_setting_set_string = libconfig.config_setting_set_string
        #Element setters
        self._config_setting_set_int_elem = libconfig.config_setting_set_int_elem
        self._config_setting_set_int64_elem = libconfig.config_setting_set_int64_elem
        self._config_setting_set_float_elem = libconfig.config_setting_set_string_elem
        self._config_setting_set_bool_elem = libconfig.config_setting_set_bool_elem
        self._config_setting_set_string_elem = libconfig.config_setting_set_string_elem
        #Remove elements
        self._config_setting_remove_elem = libconfig.config_setting_remove_elem
        #Add
        self._config_setting_add = libconfig.config_setting_add
        self._config_setting_add.restype = POINTER(config_setting_t)
        self._config_setting_add.argtypes = [POINTER(config_setting_t),
                                             c_char_p, c_int]

    def _arr2list(self, conf, name):
        ret = []
        ln = self._config_setting_length(byref(conf), name)
        for i in range(ln):
            ret.append(self._config_setting_get_elem(conf, name))
        return ret

    def _get_value(self, cfg_set_t_p):
        """Return the value of the config_setting_t"""
        if not bool(cfg_set_t_p):
            return None
        partype = cfg_set_t_p.contents.type
        if partype == self.CONFIG_TYPE_GROUP:
            return py_config_setting(cfg_set_t_p, self)
        if partype == self.CONFIG_TYPE_INT:
            return int(self._config_setting_get_int(cfg_set_t_p))
        if partype == self.CONFIG_TYPE_INT64:
            return long(self._config_setting_get_int64(cfg_set_t_p))
        if partype == self.CONFIG_TYPE_FLOAT:
            return float(self._config_setting_get_float(cfg_set_t_p))
        if partype == self.CONFIG_TYPE_STRING:
            return str(self._config_setting_get_string(cfg_set_t_p))
        if partype == self.CONFIG_TYPE_BOOL:
            return bool(self._config_setting_get_bool(cfg_set_t_p))
        if partype in (self.CONFIG_TYPE_LIST,self.CONFIG_TYPE_ARRAY):
            #Is a list or an array
            ret = []
            ln = self._config_setting_length(cfg_set_t_p)
            for i in xrange(ln):
                ret.append(self._get_value(self._config_setting_get_elem( \
                                                       cfg_set_t_p, c_int(i))))
            return ret

    def _set_value(self, cfg_set_t_p, value):
        if isinstance(value, bool):
            return self._config_setting_set_bool(cfg_set_t_p, value)
        elif isinstance(value, int):
            return self._config_setting_set_int(cfg_set_t_p, c_long(value))
        elif isinstance(value, long):
            return self._config_setting_set_int64(cfg_set_t_p, c_longlong(value))
        elif isinstance(value, float):
            return self._config_setting_set_float(cfg_set_t_p, c_double(value))
        elif isinstance(value, str):
            return self._config_setting_set_string(cfg_set_t_p, value)
        elif isinstance(value, list):
            return self._set_list(cfg_set_t_p, value)

    def _set_list(self, cfg_set_t_p, lst, idx = -1):
        """
        If idx is < 0 the list will be overwritten
        """
        if idx < 0:
            for i in xrange(self._config_setting_length(cfg_set_t_p)):
                self._config_setting_remove_elem(cfg_set_t_p, c_uint(i))
            idx = -len(lst)
        elif idx >= self._config_setting_length(cfg_set_t_p):
            idx = -len(lst)
        for el in lst:
            if isinstance(el, bool):
                self._config_setting_set_bool_elem(cfg_set_t_p, idx, el)
            elif isinstance(el, int):
                self._config_setting_set_int_elem(cfg_set_t_p, idx, c_long(el))
            elif isinstance(el, long):
                self._config_setting_set_int64_elem(cfg_set_t_p, idx, c_longlong(el))
            elif isinstance(el, float):
                self._config_setting_set_float_elem(cfg_set_t_p, idx, c_double(el))
            elif isinstance(el, str):
                self._config_setting_set_string_elem(cfg_set_t_p, idx, el)
            else:
                raise NotImplementedError()
            idx += 1
        return 1

    def _get_type_enum(self, val):
        tval = type(val)
        for enum, tp in self._typedict.iteritems():
            if tp == tval:
                return enum
        else:
            raise ValueError('Value not understood')

    def getType(self, name):
        """Get the type of the config setting name"""
        param = self._config_lookup(byref(self._config), name)
        if not bool(param):
            return None
        enum = param.contents.type
        return self._typedict[enum]

    def __getattr__(self, name):
        ret = self.get(name)
        if ret == None:
            raise AttributeError('This configfile has not attribute %s' % name)
        return ret

    def get(self, name, default=None):
        """Return default if not found"""
        if not isinstance(name, str):
            raise ValueError("The name of must be a string")
        param = self._config_lookup(byref(self._config), name)
        ret = self._get_value(param)
        if ret == None:
            return default
        return ret

    def getLine(self, name):
        """Return 0 if not found"""
        assert isinstance(name, str)
        param = self._config_lookup(byref(self._config), name)
        if not bool(param):
            return 0
        return param.contents.line

    def hasPar(self, name):
        return not(self.get(name) == None)
    has = hasPar

    def set(self, name, value, add=False):
        assert isinstance(name, str)
        param = self._config_lookup(byref(self._config), name)
        if not bool(param):
            if add:
                typint = self._get_type_enum(value)
                nlist = name.split('.')
                current = self._config.root
                next = self._config_setting_get_member(current, nlist[0])
                for i in xrange(len(nlist)-1):
                    if not bool(next):
                        next = self._config_setting_add(current, nlist[i], self.CONFIG_TYPE_GROUP)
                    current = next
                    next = self._config_setting_get_member(next, nlist[i+1])
                param = self._config_setting_add(current, nlist[-1], typint)
                if not bool(param):
                    return 0
            else:
                return 0 
        ret = self._set_value(param, value)
        return ret

    def set_elem(self, name, idx, value):
        assert isinstance(name, str)
        param = self._config_lookup(byref(self._config), name)
        assert param.contents.type in (self.CONFIG_TYPE_LIST,self.CONFIG_TYPE_ARRAY)
        if not isinstance(value, list): value = [value]
        return self._set_list(param, value, idx)

    def append(self, name, value):
        assert isinstance(name, str)
        param = self._config_lookup(byref(self._config), name)
        assert param.contents.type in (self.CONFIG_TYPE_LIST,self.CONFIG_TYPE_ARRAY)
        if not isinstance(value, list): value = [value]
        idx = self._config_setting_length(param)
        return self._set_list(param, value, idx)

    def write(self, filename=None):
        """
        Write the config file to filename.
        If the filename is not specified write to the opened file
        """
        if filename == None: filename = self._openfile
        self._config_write_file(byref(self._config), filename)

    def open(self, filename):
        """Open an existing config file"""
        if self._config_read_file(byref(self._config), filename) == self.CONFIG_TRUE:
            self._openfile = filename
        else:
            raise ValueError("%s at line %d" % (self._config.error_text,self._config.error_line))

    def close(self):
        """Close this file and init a new empty one"""
        self._config_destroy(byref(self._config))
        self._config_init(byref(self._config))
        self._openfile = None
