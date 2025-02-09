from django.db.models import Manager


class CustomCategoryManager(Manager):

    def category_with_3_products(self):
        categories = []
        for category in self.filter(visible=True):
            for sub in category.sub_categories.all():
                if sub.products.count() > 3:
                    categories.append((category, sub.products.all()[0:3]))
        return categories

    def with_sub_cats(self):
        categories = []
        for category in self.filter(visible=True):
            categories.append(dict(id=category.id, name=category.name,
                                   subs=list(category.sub_categories.filter(visible=True).values('id', 'name'))))
        return categories


class DeletableManager(Manager):
    def visible(self):
        return self.filter(visible=True)

    def invisible(self):
        return self.filter(visible=False)
