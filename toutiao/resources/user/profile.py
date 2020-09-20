# 导入g对象
from flask import g,current_app

# 导入扩展包flask-restful提供的基类，校验参数的工具类
from flask_restful import Resource,reqparse
# 导入检查文件是否是图片的工具函数
from utils.parser import check_image
# 导入登录验证装饰器
from utils.decorators import login_required
# 导入七牛云的工具
from utils.qiniu_storage import upload
# 导入模型类
from models.user import User
from models import db

# 定义视图类，处理用户头像
class PhotoResource(Resource):

    method_decorators = [login_required]

    def patch(self):
        # 接收参数
        # 校验参数
        req = reqparse.RequestParser()
        req.add_argument('photo',type=check_image,required=True,location='files')
        args = req.parse_args()
        image = args.get("photo")
        # 业务处理
        # 上传头像
        data = image.read()
        try:
            image_name = upload(data)
        except Exception as e:
            current_app.logger.error(e)
            return {'message':'server error'},500
        # 需要保存用户头像
        # User.query.get(g.user_id)
        # User.query.filter(User.is==g.user_id).update({'profile_photo':image_name})
        # db.session.commit()
        try:
            user = User.query.filter_by(id=g.user_id).first()
            user.profile_photo = image_name
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            # flask-sqlalchemy自带事务，可以不用手动回滚。
            # db.session.rollback()
        # 返回结果
        photo_url = current_app.config.get("QINIU_DOMAIN") + image_name
        return {'photo_url':photo_url}
        pass

