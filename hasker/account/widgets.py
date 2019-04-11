from django.forms import ClearableFileInput


class ClearableImageInput(ClearableFileInput):
    template_name = "account/widgets/clearable_image_input.html"
