from rest_framework.pagination import PageNumberPagination


# Класс пагинатора для Курсов и Уроков
class CourseLessonPaginator(PageNumberPagination):
    # Количество элементов по умолчанию на странице
    page_size = 10

    # Параметр, позволяющий клиенту изменять размер страницы (например, ?page_size=20)
    page_size_query_param = 'page_size'

    # Максимально допустимое количество элементов на странице (для безопасности)
    max_page_size = 50
