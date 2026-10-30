from ui.models import UIComponent


class UIManager:

    def __init__(self):
        self.components: dict[str, UIComponent] = {}


    def create(
        self,
        component: UIComponent,
    ):
        self.components[component.id] = component

        return component


    def update(
        self,
        component: UIComponent,
    ):
        self.components[component.id] = component

        return component


    def remove(
        self,
        component_id: str,
    ):
        self.components.pop(
            component_id,
            None,
        )


    def clear(self):
        self.components.clear()


    def get(
        self,
        component_id: str,
    ):
        return self.components.get(
            component_id
        )


    def get_all(self):
        return list(
            self.components.values()
        )

ui_manager = UIManager()