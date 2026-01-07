import logging

from sqlalchemy.exc import OperationalError

from wxcloudrun import db
from wxcloudrun.model import Counters, Student, Parent, Teacher, Admin, ParentStudent, PickupRecord

# 初始化日志
logger = logging.getLogger('log')


def query_counterbyid(id):
    """
    根据ID查询Counter实体
    :param id: Counter的ID
    :return: Counter实体
    """
    try:
        return Counters.query.filter(Counters.id == id).first()
    except OperationalError as e:
        logger.info("query_counterbyid errorMsg= {} ".format(e))
        return None


def delete_counterbyid(id):
    """
    根据ID删除Counter实体
    :param id: Counter的ID
    """
    try:
        counter = Counters.query.get(id)
        if counter is None:
            return
        db.session.delete(counter)
        db.session.commit()
    except OperationalError as e:
        logger.info("delete_counterbyid errorMsg= {} ".format(e))


def insert_counter(counter):
    """
    插入一个Counter实体
    :param counter: Counters实体
    """
    try:
        db.session.add(counter)
        db.session.commit()
    except OperationalError as e:
        logger.info("insert_counter errorMsg= {} ".format(e))


def update_counterbyid(counter):
    """
    根据ID更新counter的值
    :param counter实体
    """
    try:
        counter = query_counterbyid(counter.id)
        if counter is None:
            return
        db.session.flush()
        db.session.commit()
    except OperationalError as e:
        logger.info("update_counterbyid errorMsg= {} ".format(e))


# ==================== Student DAO ====================

def create_student(student):
    try:
        db.session.add(student)
        db.session.commit()
        return student
    except Exception as e:
        db.session.rollback()
        logger.error("create_student error: {}".format(e))
        raise


def get_student_by_id(student_id):
    try:
        return Student.query.get(student_id)
    except Exception as e:
        logger.error("get_student_by_id error: {}".format(e))
        return None


def get_student_by_number(student_number):
    try:
        return Student.query.filter_by(student_number=student_number).first()
    except Exception as e:
        logger.error("get_student_by_number error: {}".format(e))
        return None


def get_all_students():
    try:
        return Student.query.all()
    except Exception as e:
        logger.error("get_all_students error: {}".format(e))
        return []


def get_students_by_class(class_name):
    try:
        return Student.query.filter_by(class_name=class_name).all()
    except Exception as e:
        logger.error("get_students_by_class error: {}".format(e))
        return []


def update_student(student):
    try:
        db.session.commit()
        return student
    except Exception as e:
        db.session.rollback()
        logger.error("update_student error: {}".format(e))
        raise


def delete_student(student_id):
    try:
        student = Student.query.get(student_id)
        if student:
            db.session.delete(student)
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        logger.error("delete_student error: ".format(e))
        raise


# ==================== Parent DAO ====================

def create_parent(parent):
    try:
        db.session.add(parent)
        db.session.commit()
        return parent
    except Exception as e:
        db.session.rollback()
        logger.error("create_parent error: {}".format(e))
        raise


def get_parent_by_openid(openid):
    try:
        return Parent.query.filter_by(openid=openid).first()
    except Exception as e:
        logger.error("get_parent_by_openid error: {}".format(e))
        return None


def get_parent_by_id(parent_id):
    try:
        return Parent.query.get(parent_id)
    except Exception as e:
        logger.error("get_parent_by_id error: {}".format(e))
        return None


def get_all_parents():
    try:
        return Parent.query.all()
    except Exception as e:
        logger.error("get_all_parents error: {}".format(e))
        return []


def update_parent(parent):
    try:
        db.session.commit()
        return parent
    except Exception as e:
        db.session.rollback()
        logger.error("update_parent error: {}".format(e))
        raise


# ==================== Teacher DAO ====================

def create_teacher(teacher):
    try:
        db.session.add(teacher)
        db.session.commit()
        return teacher
    except Exception as e:
        db.session.rollback()
        logger.error("create_teacher error: {}".format(e))
        raise


def get_teacher_by_openid(openid):
    try:
        return Teacher.query.filter_by(openid=openid).first()
    except Exception as e:
        logger.error("get_teacher_by_openid error: {}".format(e))
        return None


def get_teacher_by_id(teacher_id):
    try:
        return Teacher.query.get(teacher_id)
    except Exception as e:
        logger.error("get_teacher_by_id error: {}".format(e))
        return None


def get_all_teachers():
    try:
        return Teacher.query.all()
    except Exception as e:
        logger.error("get_all_teachers error: {}".format(e))
        return []


def update_teacher(teacher):
    try:
        db.session.commit()
        return teacher
    except Exception as e:
        db.session.rollback()
        logger.error("update_teacher error: {}".format(e))
        raise


# ==================== Admin DAO ====================

def create_admin(admin):
    try:
        db.session.add(admin)
        db.session.commit()
        return admin
    except Exception as e:
        db.session.rollback()
        logger.error("create_admin error: {}".format(e))
        raise


def get_admin_by_username(username):
    try:
        return Admin.query.filter_by(username=username).first()
    except Exception as e:
        logger.error("get_admin_by_username error: {}".format(e))
        return None


# ==================== ParentStudent DAO ====================

def create_parent_student_relation(parent_id, student_id, relationship=None):
    try:
        relation = ParentStudent(parent_id=parent_id, student_id=student_id, relationship=relationship)
        db.session.add(relation)
        db.session.commit()
        return relation
    except Exception as e:
        db.session.rollback()
        logger.error("create_parent_student_relation error: {}".format(e))
        raise


def get_students_by_parent_id(parent_id):
    try:
        relations = ParentStudent.query.filter_by(parent_id=parent_id).all()
        student_ids = [r.student_id for r in relations]
        return Student.query.filter(Student.id.in_(student_ids)).all() if student_ids else []
    except Exception as e:
        logger.error("get_students_by_parent_id error: {}".format(e))
        return []


def get_parents_by_student_id(student_id):
    try:
        relations = ParentStudent.query.filter_by(student_id=student_id).all()
        parent_ids = [r.parent_id for r in relations]
        return Parent.query.filter(Parent.id.in_(parent_ids)).all() if parent_ids else []
    except Exception as e:
        logger.error("get_parents_by_student_id error: {}".format(e))
        return []


def delete_parent_student_relation(parent_id, student_id):
    try:
        relation = ParentStudent.query.filter_by(parent_id=parent_id, student_id=student_id).first()
        if relation:
            db.session.delete(relation)
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        logger.error("delete_parent_student_relation error: {}".format(e))
        raise


# ==================== PickupRecord DAO ====================

def create_pickup_record(pickup_record):
    try:
        db.session.add(pickup_record)
        db.session.commit()
        return pickup_record
    except Exception as e:
        db.session.rollback()
        logger.error("create_pickup_record error: {}".format(e))
        raise


def get_pickup_record_by_id(record_id):
    try:
        return PickupRecord.query.get(record_id)
    except Exception as e:
        logger.error("get_pickup_record_by_id error: {}".format(e))
        return None


def get_pickup_records_by_student_id(student_id, limit=None):
    try:
        query = PickupRecord.query.filter_by(student_id=student_id).order_by(PickupRecord.pickup_time.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    except Exception as e:
        logger.error("get_pickup_records_by_student_id error: {}".format(e))
        return []


def get_pickup_records_by_parent_openid(openid, limit=None):
    try:
        parent = get_parent_by_openid(openid)
        if not parent:
            return []

        student_ids = [s.id for s in get_students_by_parent_id(parent.id)]
        if not student_ids:
            return []

        query = PickupRecord.query.filter(PickupRecord.student_id.in_(student_ids)).order_by(PickupRecord.pickup_time.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    except Exception as e:
        logger.error("get_pickup_records_by_parent_openid error: {}".format(e))
        return []


def get_all_pickup_records(limit=None):
    try:
        query = PickupRecord.query.order_by(PickupRecord.pickup_time.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    except Exception as e:
        logger.error("get_all_pickup_records error: {}".format(e))
        return []
