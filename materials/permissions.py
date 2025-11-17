from rest_framework.permissions import BasePermission


class IsModeratorOrOwner(BasePermission):
    """
    Разрешает доступ:
    1. Модераторам (для просмотра, но не создания/удаления).
    2. Владельцу объекта (для полного CRUD).
    3. Только чтение для немодерируемых полей.
    """

    def has_permission(self, request, view):
        # Разрешаем просмотр списка всем авторизованным пользователям
        if request.method == 'GET' and view.action == 'list':
            return True

        # Разрешаем создание только НЕ-модераторам (потому что модераторы не могут создавать)
        if request.method == 'POST':
            return not request.user.groups.filter(name='Модераторы').exists()

        return True  # Разрешаем все остальные операции по умолчанию, которые будут проверены в has_object_permission

    def has_object_permission(self, request, view, obj):
        # 1. Администратор (superuser) имеет полный доступ
        if request.user.is_superuser:
            return True

        # 2. Модератор (группа 'Модераторы')
        if request.user.groups.filter(name='Модераторы').exists():
            # Модераторы могут видеть (GET) и редактировать (PUT/PATCH),
            # но не могут создавать (проверено в has_permission) и удалять.
            if request.method in ('GET', 'PUT', 'PATCH'):
                return True
            # Запрещаем удаление
            if request.method == 'DELETE':
                return False

        # 3. Владелец объекта
        # Проверяем, что текущий пользователь является владельцем.
        # Предполагается, что у моделей Course и Lesson есть поле 'owner'.
        if hasattr(obj, 'owner') and obj.owner == request.user:
            # Владелец может видеть, редактировать и удалять.
            return True

        # 4. Если пользователь не модератор и не владелец
        return False
