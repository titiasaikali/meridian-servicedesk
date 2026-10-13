# validators.py
#
# validators for file uploads, etc.

from django.utils.translation import gettext as _

from helpdesk import settings as helpdesk_settings

# TODO: can we use the builtin Django validator instead?
# see:
# https://docs.djangoproject.com/en/4.0/ref/validators/#fileextensionvalidator


def validate_file_extension(value):
    import os

    from django.core.exceptions import ValidationError

    if not helpdesk_settings.HELPDESK_VALIDATE_ATTACHMENT_TYPES:
        return

    name = os.path.basename(value.name)
    ext = os.path.splitext(name)[1].lower()

    # Reject multi-dot filenames (e.g. shell.php.png) outright.
    if name.count(".") > 1:
        raise ValidationError(_("Filenames may contain only one '.'"))

    # Extension must be on the allowlist (empty / "." allowed as before).
    if ext not in helpdesk_settings.HELPDESK_VALID_EXTENSIONS and not (
        ext == "" or ext == "."
    ):
        raise ValidationError(_("Unsupported file extension: ") + ext)

    # For image extensions, confirm the bytes really decode as that image.
    if ext in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}:
        from PIL import Image

        try:
            value.seek(0)
            Image.open(value).verify()
        except Exception:
            raise ValidationError(_("File content does not match its extension."))
        finally:
            value.seek(0)