from mongoengine import *
import string
import random
import hashlib
connect('demo_applejenny', host='localhost', port=27017)
import datetime
import trail as trail_m
trail = trail_m.main()
def strftime(datetime_tmp,format='%Y-%m-%d %H:%M:%S'):
  value = ''
  with trail: value = datetime_tmp.strftime(format)
  return value
def strptime(datetime_tmp,format='%Y-%m-%d %H:%M:%S'):
  value = datetime_tmp
  with trail: value = datetime.datetime.strptime(datetime_tmp,format)
  return value
def timestamp(datetime_tmp):
  value = 0
  with trail: value = datetime_tmp.timestamp()
  return value
class PasswordField(StringField):
    """A password field - generate password using specific algorithm (md5,sha1,sha512 etc) and regex validator

        Default regex validator: r[A-Za-z0-9] <- Match any of the above: leters and digits

        Example:

            class User(Document):
                username  = StringField(required=True,unique=True)
                password  = PasswordField(algorithm="md5")
                ip        = IPAddressField()

            # save user:
            user = User(username=username,password="mongoengine789",ip="192.167.12.255")
            user.save()

            # search user 
            user = User.objects(username=username).first()
            if user is None:
                print "Not found!"
                return 
            user_password = user.password
            print str(upassword) -> {'hash': 'c2e920e469d14f240d4de02883489750a1a63e68', 'salt': 'QBX6FZD', 'algorithm': 'sha1'}
            ... check password ...

    """
    ALGORITHM_MD5 = "md5"
    ALGORITHM_SHA1 = "sha1"
    ALGORITHM_SHA256 = "sha256"
    ALGORITHM_SHA512 = "sha512"
    ALGORITHM_CRYPT = "crypt"
    DEFAULT_VALIDATOR = r'[A-Za-z0-9]'    # letters and digits
    DOLLAR = "$"

    def __init__(self, min_length=6,  max_length=None, salt=None,
                 algorithm=ALGORITHM_SHA1, regex=DEFAULT_VALIDATOR, **kwargs):
        self.max_length = max_length
        self.min_length = min_length
        self.algorithm = algorithm.lower()
        self.salt = salt or self.random_password()
        super(PasswordField, self).__init__(kwargs)

    def random_password(self, nchars=6):
        chars   = string.printable
        hash    = ''
        for char in range(nchars):
            rand_char = random.randrange(0, len(chars))
            hash += chars[rand_char]
        return hash

    def hexdigest(self, password):
        if self.algorithm == PasswordField.ALGORITHM_CRYPT:
            try:
                import crypt
            except ImportError:
                self.error("crypt module not found in this system. Please use md5 or sha* algorithm")
            return crypt.crypt(password, self.salt)

        # use sha1 algoritm
        encode_password = (self.salt + password).encode("utf-8")
        if self.algorithm == PasswordField.ALGORITHM_SHA1:
            return hashlib.sha1(encode_password).hexdigest()
        elif self.algorithm == PasswordField.ALGORITHM_MD5:
            return hashlib.md5(encode_password).hexdigest()
        elif self.algorithm == PasswordField.ALGORITHM_SHA256:
            return hashlib.sha256(encode_password).hexdigest()
        elif self.algorithm == PasswordField.ALGORITHM_SHA512:
            return hashlib.sha512(encode_password).hexdigest()
        raise ValueError('Unsupported hash type %s' % self.algorithm)

    def set_password(self, password):
        """
            Sets the user's password using format [encryption algorithm]$[salt]$[password]
                Example: sha1$SgwcbaH$20f16a1fa9af6fa40d59f78fd2c247f426950e46
        """
        password =  self.hexdigest(password)
        return '%s$%s$%s' % (self.algorithm, self.salt, password)

    def to_mongo(self, value):
        return self.set_password(value)

    def to_python(self, value):
        """
            Return password like sha1$DEnDMSj$ef5cd35779bba65528c900d248f3e939fb495c65
        """
        return value

    def to_dict(self, value):
        """
            Return password split into components
        """
        (algorithm, salt, hash) = value.split(PasswordField.DOLLAR)
        return {"algorithm" : algorithm,
                "salt"      : salt,
                "hash"      : hash}
    def confirm_password(password,value):
      hash_password = PasswordField().to_dict(password)
      password_filed = PasswordField(salt=hash_password['salt'],algorithm=hash_password['algorithm'])
      return password == password_filed.to_mongo(value)