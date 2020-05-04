from mongo_connect import *
class DeviceList(Document):
  user_agent = DictField()
  ip = StringField()
  create_time = DateTimeField()
  update_time = DateTimeField()
  is_permit = BooleanField(default=False)
  config = DictField()
  config_change_flag = BooleanField(default=False)
  def get_alive():
    return DeviceList.objects(create_time__gte=datetime.datetime.now()-datetime.timedelta(minutes=1))
  def get_dict(self):
    return {'id': self.id,
            'create_time': strftime(self.create_time),
            'update_time': strftime(self.update_time),
            'ip': self.ip or '',
            'user_agent': self.user_agent or {},
            'is_permit': self.is_permit or False}
  def update_attributes(self, **kwargs):
    with trail: self.create_time = kwargs['create_time']
    with trail: self.update_time = kwargs['update_time']
    with trail: self.ip =  kwargs['ip']
    with trail: self.user_agent = kwargs['user_agent']
    with trail: self.is_permit = kwargs['is_permit']
    with trail: self.config = kwargs['config']
    with trail: self.config_change_flag = kwargs['config_change_flag']
    self.save()
    return self