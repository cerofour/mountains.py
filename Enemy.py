from ursina import Entity, distance_xz, raycast, color, mouse, destroy, Vec3, time
from mesh_utils import load_model_safe

shootables_parent = Entity()
mouse.traverse_target = shootables_parent

class Enemy(Entity):
    def __init__(self, player: Entity, **kwargs):
        # Use safe model loading for the bot
        bot_model = load_model_safe('./assets/source/almost_a_hero_enemy.glb', 'cube')
        super().__init__(parent=shootables_parent, model=bot_model, scale=0.75, collider='box', x = player.position[0] * 3, **kwargs) # 0.045
        self.health_bar = Entity(parent=self, y=8, model='cube', color=color.red, world_scale=(1.5,.1,.1))
        self.max_hp = 100
        self.player = player
        self.hp = self.max_hp

    def update(self):
        #self.rotation_y += 275 * time.dt

        #self.animate("Almost_a_Hero_Enemy_01", loop = True)

        dist = distance_xz(self.player.position, self.position)
        if dist > 40:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)

        self.look_at_2d(self.player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self,))

        if hit_info.entity == self.player:
            if dist > 2:
                self.position += self.forward * time.dt * 5

        self.rotation_y += 180

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