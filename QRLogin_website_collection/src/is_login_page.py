import os
import pickle
import re
from enum import Enum, auto
from lxml import html

from config.constants import FORM_ATTRIBUTES, LOGIN_KEYWORDS_REGEX, KEYWORDS_CHILDREN_ATTRIBUTES, \
    SIGN_UP_CHILDREN_REGEX, RESET_CHILDREN_REGEX, LOG_IN_CHILDREN_REGEX, SVM_PIPE_LOGIN_FORMS_MODEL, \
    NLP_LOGIN_IMPORTANT_WORDS


class FormTypes(Enum):
    SIGN_UP = auto()
    LOG_IN = auto()
    RESET = auto()


def is_login_form(form: html.HtmlElement, use_svm: bool = True) -> bool:
    """Checks if an html element is or contains a login form

    Args:
        form (html.HtmlElement): Element to check

    Returns:
        bool: If the element seems to be a login form
    """
    password = form.xpath('*//input[@type="password"] | input[@type="password"]')
    svm_pred = get_login_prediction(str(html.tostring(form, pretty_print=True)))
    if len(password) != 1:
        return False
    elif svm_pred:
        return True

    for attribute in FORM_ATTRIBUTES:
        value = str(form.get(attribute, "")).lower()
        if re.findall(LOGIN_KEYWORDS_REGEX, value):
            return True

    if contains_type_keywords_by_children(form, type_=FormTypes.LOG_IN):
        return True

    return False


def contains_type_keywords_by_children(
        html_element: html.HtmlElement, type_: FormTypes = FormTypes.SIGN_UP
) -> bool:
    """Check if any of the ``html element`` children elements has signup
    or reset password keywords based on the ``type_`` used.

    """
    all_elements = html_element.xpath("//*")
    for element in all_elements:
        for attribute in KEYWORDS_CHILDREN_ATTRIBUTES:
            value = str(element.get(attribute)).lower()

            if type_ == FormTypes.SIGN_UP and re.findall(SIGN_UP_CHILDREN_REGEX, value):
                return True

            if type_ == FormTypes.RESET:
                if re.findall(RESET_CHILDREN_REGEX, value) or (
                        "credentials" in value and "lookup" in value
                ):
                    return True

            if type_ == FormTypes.LOG_IN and re.findall(LOG_IN_CHILDREN_REGEX, value):
                return True

    return False


def get_login_prediction(form_html: str):
    """
    Predicts whether a login form is legitimate or not based on its HTML.

    """
    model = load_pickle(SVM_PIPE_LOGIN_FORMS_MODEL)
    features = get_login_features(form_html)
    return model.predict([features])[0]


def get_login_features(html_str):
    """
    Extracts login features from the given HTML string.

    """
    return get_basic_login_features(html_str) + get_additional_login_features(html_str)


def get_basic_login_features(html_str, feature_list=NLP_LOGIN_IMPORTANT_WORDS):
    """
    Returns a list of features extracted from the given HTML string based on the given feature list.

    """
    features = [html_str.count(word) for word in feature_list]
    return features


def get_additional_login_features(html_str):
    """
    Extracts additional features from the HTML string that may be useful for login policy classification.

    """
    maybe_login_form = 0
    maybe_login_form_email = (
        0
    )
    maybe_sign_up_form = 0

    page_html = html.fromstring(html_str)
    forms_html = page_html.xpath("//form")

    input_passwords = len(page_html.xpath("//input[@type='password'][not(@hidden)]"))

    total_inputs = 0

    for form_html in forms_html:
        n_input_text = len(form_html.xpath("//input[@type='text'][not(@hidden)]"))
        n_input_email = len(form_html.xpath("//input[@type='email'][not(@hidden)]"))
        n_input_password = len(
            form_html.xpath("//input[@type='password'][not(@hidden)]")
        )
        total_inputs += len(form_html.xpath("//input[not(@hidden)]"))

        if n_input_text >= 1 and n_input_password == 1:
            maybe_login_form = 1
        if n_input_email >= 1 and n_input_password == 1:
            maybe_login_form_email = 1
        if n_input_text >= 1 and n_input_password == 2:
            maybe_sign_up_form = 1

    mean_inputs_per_form = (
        (total_inputs / len(forms_html)) if len(forms_html) != 0 else 0
    )
    maybe_not_login = (
        1 if (maybe_login_form == 0 and maybe_login_form_email == 0) else 0
    )
    new_features = [
        mean_inputs_per_form,
        input_passwords,
        maybe_login_form,
        maybe_login_form_email,
        maybe_sign_up_form,
        maybe_not_login,
    ]
    return new_features


def load_pickle(file_name: str):
    """
    Load a pickle file from the assets directory.

    """
    dirname = os.path.dirname(__file__)
    with open(os.path.join(dirname, "assets", file_name), "rb") as file:
        object_file = pickle.load(file)
    return object_file


def is_login_page(form: html.HtmlElement):
    try:
        return is_login_form(form)
    except Exception as e:
        return False


# if __name__ == '__main__':
#     # with open('D:\Desktop\Enterp.html', "rb") as file:
#     with open('D:\Desktop\qq1.html', "rb") as file:
#         html_content = file.read()  # .decode('utf-8')
#         html_tree = html.fromstring(html_content)
#     is_login_form_present = is_login_form(html_tree)
#     print(is_login_form_present)
