# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


import bpy,bmesh
from bpy.app.handlers import persistent

def find_particle_modifier(ob, particle_system):
    for mod in ob.modifiers:
        if mod.type == mod.type == 'PARTICLE_SYSTEM' and mod.particle_system==particle_system:
            return mod
    return None

def shape_hair(depsgraph, hair_object, particle_system, vector_list):
    particle_mod = find_particle_modifier(hair_object, particle_system)
    
    hair_object_eval = hair_object.evaluated_get(depsgraph)
    particle_mod_eval = hair_object_eval.modifiers[particle_mod.name]
    
    particles = particle_mod.particle_system.particles
    particles_eval = particle_mod_eval.particle_system.particles
    
    vert_idx = 0
    for p, p_eval in zip(particles, particles_eval):
        for hk in p.hair_keys:
            hk.co_object_set(hair_object_eval, particle_mod_eval, p_eval, vector_list[vert_idx])
            vert_idx += 1

@persistent
def set_particles(scene, depsgraph):
    if scene and scene.hair_rig_global_update:
        for i in scene.hair_rig_objects:
            ob = i.hair_object
            for layer in ob.hair_rig:
                hair_object = ob
                update = layer.hair_rig_update
                ps_name = layer.hair_rig_particle_system
                target_object = layer.hair_rig_target
                target_object_eval = target_object.evaluated_get(depsgraph)
                  
                if not update:
                    continue
                if target_object==None:
                    continue
                if not ps_name:
                    continue
                
                vector_list = [i.co for i in target_object_eval.data.vertices]
                shape_hair(depsgraph, hair_object, hair_object.particle_systems[ps_name], vector_list)

def has_hair(ob):
    if ob.particle_systems:
        for ps in ob.particle_systems:
            if ps.settings.type == 'HAIR':
                return True
    return False

def remove_handler_function(handler, function):
    if handler:
        for f in handler:
            if f.__name__ == function.__name__:
                handler.remove(f)

def append_handler_function(handler, function):
    remove_handler_function(handler, function)
    handler.append(function)


def add_to_scene(context, ob):
    scene = context.scene
    objects = [i.hair_object for i in scene.hair_rig_objects]
    if ob not in objects:
        item = scene.hair_rig_objects.add()
        item.hair_object=ob

def remove_from_scene(context, ob):
    scene = context.scene
    index = -1
    for i, item in enumerate(scene.hair_rig_objects):
        if item.hair_object == ob:
            index = i
            break
    if index != -1:
        scene.hair_rig_objects.remove(index)

def toggle_update(ob, toggle):
    if ob.hair_rig:
        if toggle == True: # Update
            for layer in ob.hair_rig:
                layer.hair_rig_update=True
        else: # Pause
            for layer in ob.hair_rig:
                layer.hair_rig_update=False


def get_bmesh_linked(start_index, bm):
    linked_verts = []
    bm.verts.ensure_lookup_table()
    
    start_vert = bm.verts[start_index]
    start_vert.tag = True
    next_layer = [start_vert]
    while True:
        current_layer = next_layer
        linked_verts += current_layer
        next_layer = []
        
        #calc next_layer
        for vert in current_layer:
            for e in vert.link_edges:
                next_vert = e.other_vert(vert)
                if next_vert.tag == False:
                    next_layer.append(next_vert)
                    next_vert.tag = True
                    
        if not next_layer:
            break
        
    return linked_verts

def get_bmesh_islands(bm):
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        v.tag = False
    
    islands = []
    index_pool = [i for i in range(len(bm.verts))]
    next_idx = 0
    while True:
        current_idx = next_idx
        lv=get_bmesh_linked(current_idx, bm)
        islands.append(lv)
        
        for v in lv:
            index_pool.remove(v.index)
        if not index_pool:
            break
        
        next_idx = index_pool[0]
        
        # look for end vertex
        for n in index_pool:
            if len(bm.verts[n].link_edges) == 1: 
                next_idx=n
                break
    
    return islands 

def add_hair(ob, key_list):
    mirror = ob.data.use_mirror_x
    ob.data.use_mirror_x = False
    
    r = bpy.context.area.spaces[0].region_3d
    orig_mtx = r.view_matrix.copy()
    orig_persp = r.view_perspective
    
    for f in ob.data.polygons:
        f.select = False
        
    ob.data.polygons[0].select = True
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.view3d.view_axis(type = 'TOP', align_active = True)
    bpy.ops.view3d.view_selected()

    bpy.ops.object.mode_set(mode = 'PARTICLE_EDIT')
    
    bpy.ops.wm.tool_set_by_id(name = "builtin_brush.Comb")
    bpy.context.scene.tool_settings.particle_edit.use_emitter_deflect = False
    bpy.ops.particle.brush_edit(stroke = [{"name":"", "location":(0, 0, 0), "mouse":(0, 0), "mouse_event":(0, 0), "pressure":0, "size":0, "pen_flip":False, "x_tilt":0, "y_tilt":0, "time":0, "is_start":False}])
    
    bpy.ops.particle.select_all(action = 'SELECT')
    bpy.ops.particle.delete(type = 'PARTICLE')
    
    bpy.ops.wm.tool_set_by_id(name = "builtin_brush.Add")
    bpy.context.scene.tool_settings.particle_edit.brush.count = 1
    
    r_w = bpy.context.region.width
    r_h = bpy.context.region.height
    p_w = int(r_w*0.5)
    p_h = int(r_h*0.5)
    
    for i in key_list:
        bpy.context.scene.tool_settings.particle_edit.default_key_count = i
        bpy.ops.particle.brush_edit(stroke = [
            {"name":"", "location":(0, 0, 0), 
            "mouse":(p_w, p_h), "mouse_event":(0, 0), 
            "pressure":0, "size":0, 
            "pen_flip":False, "x_tilt":0, 
            "y_tilt":0, "time":0, 
            "is_start":False}])

    bpy.ops.object.mode_set(mode = 'OBJECT')
    ob.data.use_mirror_x = mirror
    
    r.view_matrix = orig_mtx
    r.view_perspective = orig_persp


# operators
class HAIRRRIG_mesh_ops_public():
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob.hair_rig:
            layer = ob.hair_rig[ob.hair_rig_active_layer_index]
            if layer.hair_rig_particle_system and layer.hair_rig_target:
                return True
        return False

class HAIRRIG_OT_initialize(bpy.types.Operator):
    """recalc scene hair rig objects"""
    bl_idname = "hair_rig.initialize"
    bl_label = "Initialize"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        scene.hair_rig_objects.clear()
        for ob in bpy.data.objects:
            if ob.hair_rig:
                add_to_scene(context, ob)
        
        append_handler_function(bpy.app.handlers.depsgraph_update_post, set_particles)
        append_handler_function(bpy.app.handlers.frame_change_post, set_particles)
        
        return {'FINISHED'}

class HAIRRIG_OT_add_layer(bpy.types.Operator):
    """add a new hair rig layer"""
    bl_idname = "hair_rig.add_layer"
    bl_label = "Add Layer"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        ob = context.object
        
        if ob.hair_rig:
            act_layer = ob.hair_rig[ob.hair_rig_active_layer_index]
            layer = ob.hair_rig.add()
            layer.hair_rig_particle_system = act_layer.hair_rig_particle_system
        else:
            layer = ob.hair_rig.add()
            layer.hair_rig_particle_system = ob.particle_systems.active.name
        
        add_to_scene(context, ob)
        return {'FINISHED'}

class HAIRRIG_OT_remove_layer(bpy.types.Operator):
    """remove active hair rig layer"""
    bl_idname = 'hair_rig.remove_layer'
    bl_label = 'Remove Layer'
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.object.hair_rig
    
    def execute(self, context):
        scene = context.scene
        ob = context.object
        if ob.hair_rig:
            index = ob.hair_rig_active_layer_index
            ob.hair_rig.remove(index)
            ob.hair_rig_active_layer_index = index-1
        
        ob.hair_rig.update()
        if not ob.hair_rig:
            remove_from_scene(context, ob)
            del ob['hair_rig']
            del ob['hair_rig_active_layer_index']
        return {'FINISHED'}

class HAIRRIG_OT_move_layer(bpy.types.Operator):
    """move active hair rig layer"""
    bl_idname = 'hair_rig.move_layer'
    bl_label = 'Move Layer'
    bl_options = {'UNDO'}
    
    direction: bpy.props.BoolProperty(name = 'move_direction') #True:UP; False:DOWN
    
    @classmethod
    def poll(cls, context):
        return context.object.hair_rig
    
    def execute(self, context):
        ob = context.object
        index = ob.hair_rig_active_layer_index
        max_index = len(ob.hair_rig)-1
        
        if self.direction: #UP
            if index ==0:
                return {'FINISHED'}
            else:
                neightbor = index-1
        else: #DOWN
            if index==max_index:
                return {'FINISHED'}
            else:
                neightbor = index+1
        
        ob.hair_rig.move(neightbor, index)
        ob.hair_rig_active_layer_index = neightbor
        return {'FINISHED'}

class HAIRRIG_OT_clear_data(bpy.types.Operator):
    """move active hair rig layer"""
    bl_idname = 'hair_rig.clear_data'
    bl_label = 'Clear Data'
    bl_options = {'UNDO'}
    
    type: bpy.props.BoolProperty(name = 'Local/Global')#True:Local, False:Global

    def execute(self, context):
        ob = context.object
        scene = context.scene
        if self.type: #Local
            ob.hair_rig.clear()
            remove_from_scene(context, ob)
        else: #Global
            for ob in bpy.data.objects:
                ob.hair_rig.clear()
                ob.hair_rig_active_layer_index = 0
            scene.hair_rig_objects.clear()
        return {'FINISHED'}


class HAIRRIG_OT_toggle_update(bpy.types.Operator):
    """toggle update"""
    bl_idname = 'hair_rig.toggle_update'
    bl_label = 'Toggle Update'
    
    type: bpy.props.BoolProperty(name = 'Local/Global')# True:Local, False:Global
    toggle: bpy.props.BoolProperty(name = 'toggle_type')# True:Update. False:Pause
    
    def execute(self, context):
        if self.type==True: # Local
            ob = context.object
            toggle_update(ob, self.toggle)
        
        else: # Global
            scene = context.scene
            objects = [i.hair_object for i in scene.hair_rig_objects]
            for ob in objects:
                toggle_update(ob, self.toggle)
        
        return {'FINISHED'}


class HAIRRIG_OT_set_active(bpy.types.Operator):
    """set as active particle system"""
    bl_idname = 'hair_rig.set_active'
    bl_label = 'Set Active'
    
    name:bpy.props.StringProperty(name='name')
    
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob.hair_rig:
            layer = ob.hair_rig[ob.hair_rig_active_layer_index]
            if layer.hair_rig_particle_system:
                return True
        return False
        
    def execute(self, context):
        ob = context.object
        index = [p.name for p in ob.particle_systems].index(self.name)
        ob.particle_systems.active_index = index
        return {'FINISHED'}


class HAIRRIG_OT_hair_to_mesh(bpy.types.Operator, HAIRRRIG_mesh_ops_public):
    """generate mesh from hair"""
    bl_idname = 'hair_rig.hair_to_mesh'
    bl_label = 'Hair to Mesh'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        vertices = []
        edges = []
        faces = []
        
        deps = context.evaluated_depsgraph_get()
        ob = context.object
        ob_eval = ob.evaluated_get(deps)
        layer = ob.hair_rig[ob.hair_rig_active_layer_index]
        
        target_object = layer.hair_rig_target
        
        ps = ob_eval.particle_systems[layer.hair_rig_particle_system]
        vert_idx = 0
        for p in ps.particles:
            key_count = len(p.hair_keys)
            for i,hk in enumerate(p.hair_keys):
                vertices.append(hk.co)
                if i<key_count-1:
                    edge = (vert_idx,vert_idx+1)
                    edges.append(edge)
                vert_idx += 1

        mesh=target_object.data
        mesh.clear_geometry()
        mesh.from_pydata(vertices, edges, faces)
        
        return {'FINISHED'}

class HAIRRIG_OT_hair_shape_to_mesh(bpy.types.Operator, HAIRRRIG_mesh_ops_public):
    """match mesh vertex locations to hair key locations by indices"""
    bl_idname = 'hair_rig.hair_shape_to_mesh'
    bl_label = 'Hair Shape to Mesh'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        deps = context.evaluated_depsgraph_get()
        ob = context.object
        ob_eval = ob.evaluated_get(deps)
        layer = ob.hair_rig[ob.hair_rig_active_layer_index]
        
        target_object = layer.hair_rig_target
        mesh=target_object.data
        
        ps = ob_eval.particle_systems[layer.hair_rig_particle_system]
        vert_idx = 0
        for p in ps.particles:
            for hk in p.hair_keys:
                mesh.vertices[vert_idx].co = hk.co
                vert_idx += 1
        
        return {'FINISHED'}

class HAIRRIG_OT_mesh_to_hair(bpy.types.Operator, HAIRRRIG_mesh_ops_public):
    """generate hair from mesh edges"""
    bl_idname = 'hair_rig.mesh_to_hair'
    bl_label = 'Mesh to Hair'
    bl_options = {'UNDO', 'REGISTER'}
        
    regenerate_target: bpy.props.BoolProperty(name = 'Regenerate Target', default = True)
    
    def execute(self, context):
        deps = context.evaluated_depsgraph_get()
        ob = context.object
        layer = ob.hair_rig[ob.hair_rig_active_layer_index]
        
        target_object = layer.hair_rig_target
        target_object_eval = target_object.evaluated_get(deps)
        
        bm = bmesh.new()
        bm.from_mesh(target_object_eval.data)
        islands = get_bmesh_islands(bm)
        
        key_list = [len(i) for i in islands]
        
        add_hair(ob, key_list) #add hair
        
        vector_list = [j.co for i in islands for j in i]
        shape_hair(deps, ob, ob.particle_systems[layer.hair_rig_particle_system], vector_list)
        
        if self.regenerate_target:
            bpy.ops.hair_rig.hair_to_mesh()
        
        return {'FINISHED'}

class HAIRRIG_OT_mesh_shape_to_hair(bpy.types.Operator, HAIRRRIG_mesh_ops_public):
    """match hair key locations to mesh vertex locations by indices"""
    bl_idname = 'hair_rig.mesh_shape_to_hair'
    bl_label = 'Mesh Shape to Hair'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        deps = context.evaluated_depsgraph_get()
        ob = context.object
        layer = ob.hair_rig[ob.hair_rig_active_layer_index]
        
        target_object = layer.hair_rig_target
        target_object_eval = target_object.evaluated_get(deps)
        
        vector_list = [v.co for v in target_object_eval.data.vertices]
        
        shape_hair(deps, ob, ob.particle_systems[layer.hair_rig_particle_system], vector_list)
        
        return {'FINISHED'}
    
    
#uilist
class HAIRRIG_UL_uilist(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item.hair_rig_update:
                custom_icon = 'PAUSE'
            else:
                custom_icon = 'PLAY'
            
            ob = context.object
            if item.hair_rig_particle_system in ob.particle_systems.keys():
                layout.prop(context.object.particle_systems[item.hair_rig_particle_system], 'name',text = '',emboss = False)
            else:
                layout.label(text = '')
            layout.prop(item, 'hair_rig_update', text = '', icon = custom_icon)
            
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text = '')

# menus
class HAIRRIG_MT_layer_menu(bpy.types.Menu):
    bl_label = 'Layer Specials'
    
    def draw(self, context):
        layout = self.layout
        
        op = layout.operator('hair_rig.toggle_update', text = 'Update All (Local)',icon = 'PLAY')
        op.type = True # Local
        op.toggle = True # Update
        
        op = layout.operator('hair_rig.toggle_update', text = 'Update All (Global)')
        op.type = False # Global
        op.toggle = True # Update
        
        layout.separator()
        
        op = layout.operator('hair_rig.toggle_update', text = 'Pause All (Local)',icon = 'PAUSE')
        op.type = True # Local
        op.toggle = False # Pause
        
        op = layout.operator('hair_rig.toggle_update', text = 'Pause All (Global)')
        op.type = False # Global
        op.toggle = False # Pause
        
        layout.separator()
        layout.operator('hair_rig.clear_data', text = 'Clear Hair Rig Data (Local)',icon = 'TRASH').type = True # Local
        layout.operator('hair_rig.clear_data', text = 'Clear Hair Rig Data (Global)').type = False # Global

class HAIRRIG_MT_mesh_menu(bpy.types.Menu):
    bl_label = 'Target Mesh Specials'
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator('hair_rig.hair_to_mesh', text = 'Hair to Mesh')
        layout.operator('hair_rig.hair_shape_to_mesh', text = 'Hair Shape to Mesh')
        layout.operator('hair_rig.mesh_to_hair', text = 'Mesh to Hair (BETA)')
        layout.operator('hair_rig.mesh_shape_to_hair', text = 'Mesh Shape to Hair')


# main panel
class HAIRRIG_PT_hair_rig(bpy.types.Panel):
    bl_category = "Hair Rig"
    bl_label = "Hair Rig Layers"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    @classmethod
    def poll(self, context):
        return context.area.ui_type == 'VIEW_3D'
    
    def draw(self, context):
        ob = context.object
        scene = context.scene
        layout = self.layout
        
        row = layout.row(align = True)
        row.prop(scene, 'hair_rig_global_update', text = 'Global Update', icon = 'PLAY')
        row.operator('hair_rig.initialize', text = '', icon = 'FILE_REFRESH')
        
        if ob.type=='MESH':
            if has_hair(ob):
                row = layout.row(align = True)
                row.template_list("HAIRRIG_UL_uilist", "", ob,"hair_rig", ob, "hair_rig_active_layer_index")
                
                subcol = row.column(align = True)
                subcol.operator('hair_rig.add_layer',text = '', icon = 'ADD')
                subcol.operator('hair_rig.remove_layer',text = '', icon = 'REMOVE')
                
                subcol.separator()
                subcol.menu('HAIRRIG_MT_layer_menu',text = '',icon = 'DOWNARROW_HLT')
                
                subcol.separator()
                subcol.operator('hair_rig.move_layer',text = '', icon = 'TRIA_UP').direction = True #UP
                subcol.operator('hair_rig.move_layer',text = '', icon = 'TRIA_DOWN').direction = False #DOWN
                
                if ob.hair_rig:
                    item = ob.hair_rig[ob.hair_rig_active_layer_index]
                    col = layout.column()
                    subrow = col.row(align = True)
                    subrow.prop_search(item, 'hair_rig_particle_system',ob, 'particle_systems',text = '')
                    
                    subrow.operator('hair_rig.set_active',text = '', icon = 'FORWARD').name = item.hair_rig_particle_system
                    
                    subrow = col.row(align = True)
                    subrow.prop(item, 'hair_rig_target', text = '')
                    subrow.menu('HAIRRIG_MT_mesh_menu',text = '',icon = 'COLLAPSEMENU')
            else:
                layout.label(text = 'object has no hair particle modifier')
        
        else:
            layout.label(text = 'non mesh type object')


# object properties
class HAIRRIG_object_properties(bpy.types.PropertyGroup):
    
    hair_rig_update: bpy.props.BoolProperty(name = 'Hair Rig Update', default = False)
    hair_rig_particle_system: bpy.props.StringProperty(name = 'Hair Rig Particle System')
    hair_rig_target: bpy.props.PointerProperty(name = 'Hair Rig Target',type = bpy.types.Object)

# scene properties
class HAIRRIG_scene_objects(bpy.types.PropertyGroup):
    hair_object: bpy.props.PointerProperty(name = 'hair_object', type = bpy.types.Object)


classes = [
    HAIRRIG_object_properties,
    HAIRRIG_scene_objects,
    
    HAIRRIG_OT_initialize,
    HAIRRIG_OT_add_layer,
    HAIRRIG_OT_remove_layer,
    HAIRRIG_OT_move_layer,
    HAIRRIG_OT_clear_data,
    HAIRRIG_OT_toggle_update,
    HAIRRIG_OT_set_active,
    
    HAIRRIG_OT_hair_to_mesh,
    HAIRRIG_OT_hair_shape_to_mesh,
    HAIRRIG_OT_mesh_to_hair,
    HAIRRIG_OT_mesh_shape_to_hair,
    
    HAIRRIG_UL_uilist,
    HAIRRIG_MT_layer_menu,
    HAIRRIG_MT_mesh_menu,
    HAIRRIG_PT_hair_rig,
    
    ]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Object.hair_rig = bpy.props.CollectionProperty(type = HAIRRIG_object_properties)
    bpy.types.Object.hair_rig_active_layer_index = bpy.props.IntProperty(name = 'Hair Rig Active Layer Index', default = 0, min = 0)
    
    bpy.types.Scene.hair_rig_objects = bpy.props.CollectionProperty(type = HAIRRIG_scene_objects)
    bpy.types.Scene.hair_rig_global_update = bpy.props.BoolProperty(name = 'Hair Rig Global Update',description = 'Hair Rig Global Update', default = False)
    
    append_handler_function(bpy.app.handlers.depsgraph_update_post, set_particles)
    append_handler_function(bpy.app.handlers.frame_change_post, set_particles)
    append_handler_function(bpy.app.handlers.load_post, set_particles)
    
def unregister():
    for c in classes:
        try:
            bpy.utils.unregister_class(c)
        except:
            pass
    del bpy.types.Object.hair_rig
    del bpy.types.Object.hair_rig_active_layer_index
    
    del bpy.types.Scene.hair_rig_objects
    del bpy.types.Scene.hair_rig_global_update
    
    remove_handler_function(bpy.app.handlers.depsgraph_update_post, set_particles)
    remove_handler_function(bpy.app.handlers.frame_change_post, set_particles)
    remove_handler_function(bpy.app.handlers.load_post, set_particles)
    
#if __name__ == "__main__":
#    register()
#    unregister()


