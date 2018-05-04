import sqlite3
import logging
import os

logging.basicConfig(level=logging.ERROR)


# 数据库操作，负责连接、提交事务、断开数据库，返回操作的行数与结果列表
def operate(db_name, execute_str, execute_args=None):
    result = None
    conn = sqlite3.connect(db_name + ".db")
    row_size = 0
    try:
        cursor = conn.cursor()
        if execute_args:
            cursor.execute(execute_str, execute_args)
        else:
            cursor.execute(execute_str)
        result = cursor.fetchall()
        row_size = cursor.rowcount
        cursor.close()
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        conn.close()
    return row_size, result


# 数据类型类
class Field(object):
    def __init__(self, name, column_type, primary_key=False):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key

    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.name)


# 字符串类
class StringField(Field):
    def __init__(self, name, primary_key=False):
        super(StringField, self).__init__(name, 'TEXT', primary_key)


# 整型类
class IntegerField(Field):
    def __init__(self, name, primary_key=False):
        super(IntegerField, self).__init__(name, 'INTEGER', primary_key)


# Model元类
# 将子类类属性的值自动保存到对象属性
class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        logging.info('Found model: %s' % name)
        mappings = dict()
        primary = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                # 判断是否为主键
                if v.primary_key:
                    primary = v
                    logging.info('Found primary key: %s ==> %s' % (k, v))
                mappings[k] = v
                logging.info('Found mapping: %s ==> %s' % (k, v))
        for k in mappings.keys():
            attrs.pop(k)
        attrs['__mappings__'] = mappings  # 保存属性和列的映射关系
        attrs['__table__'] = name  # 假设表名和类名一致
        attrs['__primary__'] = primary  # 保存主键
        return type.__new__(cls, name, bases, attrs)


# Model类
# 将数据库操作封装为类的方法
class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kwarg):
        super(Model, self).__init__(**kwarg)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError("'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    # 返回是否存在该数据表
    @classmethod
    def has_table(cls):
        if not os.path.exists(cls.__table__ + ".db"):
            logging.warning('DB file not exist!')
            return False
        execute_str = "select count(*) from sqlite_master where type=? and name=?"
        row_size, result = operate(cls.__table__, execute_str, ("table", cls.__table__))
        if result[0][0]:
            return True
        else:
            logging.warning('Table not exist!')
            return False

    # 新建数据表，默认数据表与数据库同名
    @classmethod
    def new_table(cls):
        fields = []
        column_types = []
        primary = cls.__primary__
        for k, v in cls.__mappings__.items():
            fields.append(v.name)
            column_types.append(v.column_type)
        # 创建数据表
        sql = 'create table %s (' % cls.__table__
        if primary is not None:
            sql += '%s %s primary key,' % (primary.name, primary.column_type)
            # 需要在参数列表中去掉此主键的键值
            fields.remove(primary.name)
            column_types.remove(primary.column_type)
        for i in range(0, len(fields) - 1):
            sql += ' %s %s, ' % (fields[i], column_types[i])
        sql += ' %s %s)' % (fields[-1], column_types[-1])
        logging.info('SQL CREATE: %s' % sql)
        row_size, result = operate(cls.__table__, sql)
        logging.info('ROW_SIZE: %s' % row_size)
        logging.info('RESULT: %s' % result)
        return row_size, result

    # 查询数据库中指定列名和值的记录
    @classmethod
    def find(cls, column_key, column_value):
        # 先将select的键名保存起来
        key_list = [k for k in cls.__mappings__]
        sql = 'select %s from %s where %s = ?' % (', '.join(['`%s`' % k for k in key_list]), cls.__table__, column_key)
        logging.info('SQL SELECT: %s' % sql)
        logging.info('ARGS: %s' % str(column_value))
        row_size, result = operate(cls.__table__, sql, (column_value,))
        logging.info('ROW_SIZE: %s' % row_size)
        logging.info('RESULT: %s' % result)
        result_list = []
        for line in result:
            result_list.append(dict(zip(key_list, line)))
        return row_size, result_list

    # 查询数据库中是否存在指定列名和值的记录
    @classmethod
    def exist(cls, column_key, column_value):
        row_size, result_list = cls.find(column_key, column_value)
        return True if result_list else False

    # 根据列名和值删除数据表中的一行数据
    @classmethod
    def remove(cls, column_key, column_value):
        sql = "delete from %s where %s = ?" % (cls.__table__, column_key)
        logging.info('SQL DELETE: %s' % sql)
        logging.info('ARGS: %s' % str(column_value))
        row_size, result = operate(cls.__table__, sql, (column_value,))
        logging.info('ROW_SIZE: %s' % row_size)
        logging.info('RESULT: %s' % result)
        return row_size, result

    # 插入一行数据到数据表
    def save(self):
        fields = []
        args = []
        for k, v in self.__mappings__.items():
            fields.append(v.name)
            args.append(getattr(self, k, None))
        # 插入一行数据
        sql = 'insert into %s (%s) values (%s)' % (self.__table__, ','.join(fields), ','.join(['?' for i in args]))
        logging.info('SQL INSERT: %s' % sql)
        logging.info('ARGS: %s' % str(args))
        row_size, result = operate(self.__table__, sql, tuple(args))
        logging.info('ROW_SIZE: %s' % row_size)
        logging.info('RESULT: %s' % result)
        return row_size, result

    # 根据列名和值修改数据表中的一行数据
    def update_by(self, column_key, column_value):
        fields = []
        args = []
        for k, v in self.__mappings__.items():
            fields.append(v.name)
            args.append(getattr(self, k, None))
        # 修改一行数据
        sql = 'update `%s` set %s where `%s` = ?' % (
            self.__table__, ', '.join(['`%s`=?' % k for k in fields]), column_key)
        args.append(column_value)
        logging.info('SQL UPDATE: %s' % sql)
        logging.info('ARGS: %s' % str(args))
        row_size, result = operate(self.__table__, sql, tuple(args))
        logging.info('ROW_SIZE: %s' % row_size)
        logging.info('RESULT: %s' % result)
        return row_size, result
