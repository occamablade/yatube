from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

# Это нужно для того, чтобы разработчик без труда мог переопределить модель,
# которая будет хранить данные пользователей.
User = get_user_model()


#  создадим собственный класс для формы регистрации
#  сделаем его наследником предустановленного класса UserCreationForm
class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        # укажем модель, с которой связана создаваемая форма
        model = User
        # укажем, какие поля должны быть видны в форме и в каком порядке
        fields = ("first_name", "last_name", "username", "email")
