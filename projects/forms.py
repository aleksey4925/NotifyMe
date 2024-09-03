from django.forms import ModelForm, ModelChoiceField

from projects.models import Project, System, Chat


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ["name", "system", "login", "threshold"]

    system = ModelChoiceField(queryset=System.objects.all())


class ChatForm(ModelForm):
    class Meta:
        model = Chat
        fields = ["chat_id", "comment"]
