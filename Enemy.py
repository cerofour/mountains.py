from ursina import Entity, distance_xz, raycast, color, mouse, destroy, Vec3
from mesh_utils import load_model_safe

shootables_parent = Entity()
mouse.traverse_target = shootables_parent

class Enemy(Entity):
    def __init__(self, **kwargs):
        # Use safe model loading for the bot
        bot_model = load_model_safe('./assets/ojito/Robot_Eye.fbx', 'cube')
        super().__init__(parent=shootables_parent, model=bot_model, scale_y=0.09, rotation=(0, 360, 360), scale_x=0.09, scale_z=0.09, origin_y=-.5, collider='box', **kwargs) # 0.045
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5,.1,.1))
        self.max_hp = 100
        self.hp = self.max_hp

    def update(self, target_entity: Entity):
        dist = distance_xz(target_entity.position, self.position)
        if dist > 40:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)


        self.look_at_2d(target_entity.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self))

        if hit_info.entity == target_entity:
            if dist > 2:
                self.position += self.forward * time.dt * 5

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1