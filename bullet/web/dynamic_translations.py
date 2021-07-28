import re
from typing import Dict, Tuple, Optional

from django.template import Variable
from django.utils import translation
from django.utils.functional import lazy
from django.utils.safestring import SafeData, mark_safe, SafeString
from django.utils.translation import pgettext_lazy, gettext_lazy


class TranslationCache:
    def __init__(self):
        self.__cache: Dict[Tuple[str, Optional[str], str], SafeString] = {}
        self.reload()

    def reload(self):
        from web.models import Translation
        for trans in Translation.objects.filter(content__isnull=False):
            self.__cache[(trans.language, trans.context, trans.reference)] = mark_safe(trans.content)
        return

    def translate(self, reference, context):
        curr_lang = translation.get_language()
        return self.__cache.get((curr_lang, context, reference)) or reference


def translate(reference, context=None):
    global translation_cache
    if translation_cache is None:
        raise ValueError("Translation cache has not been initialized")
    return translation_cache.translate(reference, context)


translate_lazy = lazy(translate, str)

translation_cache: 'TranslationCache'


def init():
    global translation_cache
    translation_cache = TranslationCache()

    # Pretty much copy-paste from django.template.base.Variable.resolve with added dynamic trans handling
    def modified_variable_resolve(self, context):
        if self.lookups is not None:
            value = self._resolve_lookup(context)
        else:
            value = self.literal
        if self.translate:
            is_safe = isinstance(value, SafeData)
            msgid = value.replace('%', '%%')
            msgid = mark_safe(msgid) if is_safe else msgid

            if re.match(r'^dynamic:.*', msgid):
                msgid = msgid[8:]
                return translate_lazy(msgid, self.message_context)
            else:
                if self.message_context:
                    return pgettext_lazy(self.message_context, msgid)
                else:
                    return gettext_lazy(msgid)
        return value

    Variable.resolve = modified_variable_resolve
