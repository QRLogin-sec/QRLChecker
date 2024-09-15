DOMAIN_LIST = [
    'https://www.google.com/', 'https://www.google.ad/', 'https://www.google.ae/',
    'https://www.google.com.af/', 'https://www.google.com.ag/', 'https://www.google.com.ai/',
    'https://www.google.al/', 'https://www.google.am/', 'https://www.google.co.ao/',
    'https://www.google.com.ar/', 'https://www.google.as/', 'https://www.google.at/',
    'https://www.google.com.au/', 'https://www.google.az/', 'https://www.google.ba/',
    'https://www.google.com.bd/', 'https://www.google.be/', 'https://www.google.bf/',
    'https://www.google.bg/', 'https://www.google.com.bh/', 'https://www.google.bj/',
    'https://www.google.com.bn/', 'https://www.google.com.bo/', 'https://www.google.com.br/',
    'https://www.google.bs/', 'https://www.google.at/', 'https://www.google.bt/',
    'https://www.google.co.bw/', 'https://www.google.com.bz/'
]

LOGIN_IDENTITIES = [
    '登录', '登陆', '登入', '登錄', '登陸', 'Sign in', 'Log in', 'Login', 'Enter', 'sign in', 'Sign In', 'LOG IN',
    'SIGN IN', 'Signin', 'SIGNIN', 'LOGIN', 'login', 'log in', 'Log In', 'enter', 'Anmelden', 'Einloggen',
    'Iniciar sesión', 'Benutzerkonto anmelden', 'Eingeben', 'betreten', 'Acceder', 'Войти', 'تسجيل الدخول',
    'Se connecter', 'Connexion', 'Sidentifier', 'Entrer', 'ログイン', 'サインイン', '入力', 'ウェブサイトに入る', 'アカウントにログインする', '로그인',
    '사인 인', '입력하다', '웹 사이트에 들어가다', 'साइन इन करें', 'लॉग इन करें', 'लॉगिन', '会员'
]

QR_KEYWORDS = ['qrcode', 'QR code', 'scan the code', 'qr code', 'qr_code', 'Scan code', 'qr-code', 'qrLogin', 'qrCode',
               'sign in with QR', 'login by qr', 'QR-code']

HUMAN_VERIFICATION_KEYWORDS = ["人机验证", "reCAPTCHA", "recaptcha", "g-recaptcha"]

HUMAN_VERIFICATION_HINTS = ["验证您不是机器人", "请点击下方图像进行验证"]

FORM_ATTRIBUTES = ["class", "id", "action"]

LOGIN_KEYWORDS_REGEX = r"log(.{0,1})in|sign(.{0,1})in|account"

KEYWORDS_CHILDREN_ATTRIBUTES = ["class", "name", "id"]

SIGN_UP_CHILDREN_REGEX = r"sign(.{0,1})up|regist|account|create"

LOG_IN_CHILDREN_REGEX = r"log(.{0,1})in|sign(.{0,1})in|account"

RESET_CHILDREN_REGEX = r"recover|forgot|reset"

SVM_RELEVANT_WORDS = "SVM_important_words.pkl"

SVM_PIPE_LOGIN_FORMS_MODEL = "SVM_login.pkl"

NLP_LOGIN_IMPORTANT_WORDS = [
    "newsletter",
    "search",
    "registry",
    "signup",
    "account",
    "create",
    "customer",
    "regist",
    "login",
    "sso",
    "accounting",
    "author",
    "signin",
    "auth",
    "forgot",
    "reset",
    "recover",
    "credentials",
    "lookup",
    "password",
]
